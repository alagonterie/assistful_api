from json import dumps
from typing import Optional, Any, Type, Callable

from langchain.pydantic_v1 import BaseModel
from langchain.tools import StructuredTool
from langchain.tools.base import ToolException
from langchain.tools.openapi.utils.openapi_utils import OpenAPISpec, HTTPVerb
from requests import get, post, put, patch, delete, Response
from requests.exceptions import JSONDecodeError

from shared.globals.constants import DEFAULT_HEADERS
from shared.models.ai.agents.tools.utils.assistful_api_operation import AssistfulAPIOperation
from shared.models.ai.assistful_prompts import RESPONSE_PREFIX


class AssistfulNLATool(StructuredTool):
    """
    Class for creating tools that interact with an API using natural language.
    """

    api_operation: Optional[AssistfulAPIOperation] = None
    """Hold on to API Operation details for later access."""

    tool_memory: Optional[list[str]] = None
    """Shared memory of tool output for reference in a chain that runs multiple tools."""

    @classmethod
    def from_spec(
            cls,
            path: str,
            method: str,
            spec: OpenAPISpec,
    ) -> "AssistfulNLATool":
        """
        Create an instance of the AssistfulTool using the provided specification.

        :param path: The path of the API endpoint.
        :param method: The HTTP method.
        :param spec: The OpenAPI specification.
        :return: An instance of the AssistfulNLATool.
        """
        api_operation = AssistfulAPIOperation.from_openapi_spec(spec, path, method)
        name, description = AssistfulNLATool._get_name_and_description_from_api_operation(api_operation)

        return cls(
            name=name,
            description=description,
            args_schema=BaseModel,
            api_operation=api_operation
        )

    @classmethod
    def from_query_and_api_operation(
            cls,
            user_query: str,
            api_operation: AssistfulAPIOperation,
            tool_memory: Optional[set[str]] = None,
            headers: Optional[dict] = None,
    ) -> "AssistfulNLATool":
        """
        Create an instance of the AssistfulTool using the provided user query and API operation object.

        :param user_query: The original user query that prompted the tool creation.
        :param api_operation: Instance of AssistfulAPIOperation class representing the API operation to be performed.
        :param tool_memory: Optional memory to be written to by the tool after execution.
        :param headers: Optional headers to be included in the request.
        :return: An instance of the AssistfulNLATool class initialized with the provided parameters.
        """
        name, description = AssistfulNLATool._get_name_and_description_from_api_operation(api_operation)

        args_schema_model, fields_dict = AssistfulNLATool._generate_args_schema_objects(api_operation)
        tool_func = AssistfulNLATool._generate_tool_func(api_operation, fields_dict, user_query, tool_memory, headers)

        structured_tool = AssistfulNLATool.from_function(
            tool_func,
            name=name,
            description=description,
            args_schema=args_schema_model
        )

        return cls(
            func=structured_tool.func,
            name=structured_tool.name,
            description=description,
            args_schema=structured_tool.args_schema,
            handle_tool_error=AssistfulNLATool._handle_error,
            api_operation=api_operation,
            tool_memory=tool_memory
        )

    @classmethod
    def _get_name_and_description_from_api_operation(cls, api_operation: AssistfulAPIOperation) -> tuple[str, str]:
        api_title = f'{api_operation.api_title.replace(" ", "_")}.' if api_operation.api_title else ''
        name = f'{api_title}{api_operation.operation_id}'
        description = (
            f"I'm an AI from {api_title}. Instruct what you want,"
            " and I'll assist via an API with description:"
            f" {api_operation.description}"
        )

        return name, description

    @classmethod
    def _generate_args_schema_objects(
            cls,
            api_operation: AssistfulAPIOperation
    ) -> tuple[Type[BaseModel], dict[str, dict]]:
        # Generate field definitions
        props = (list(api_operation.properties or []) +
                 list(api_operation.request_body.properties or [] if api_operation.request_body else []))

        fields_dict: dict[str, dict] = {}
        fields_definitions: dict[str, tuple] = {}
        for prop in props:
            definitions = {
                'description': prop.description,
                'type': prop.type,
                'required': prop.required
            }

            if prop.default:
                definitions['default'] = prop.default

            from langchain.tools.openapi.utils.api_models import APIProperty, APIRequestBodyProperty
            if type(prop) == APIRequestBodyProperty and any(prop.properties):
                definitions['properties'] = prop.properties
            elif type(prop) == APIProperty:
                definitions['location'] = prop.location

            fields_dict[prop.name] = definitions
            definitions = {key: value for key, value in definitions.items() if key != 'location'}

            from langchain.pydantic_v1 import Field
            fields_definitions[prop.name] = (Optional[Any], Field(**definitions))

        # Create the Pydantic BaseModel dynamically
        from langchain.pydantic_v1.main import create_model
        args_schema_model = create_model('ArgsSchemaModel', **fields_definitions)

        return args_schema_model, fields_dict

    @classmethod
    def _generate_tool_func(
            cls,
            api_operation: AssistfulAPIOperation,
            fields_dict: dict[str, dict],
            user_query: Optional[str] = None,
            tool_memory: Optional[set[str]] = None,
            headers: Optional[dict] = None
    ) -> Callable[[dict[str, Any]], str]:
        def tool_func(**args) -> str:
            print('Tool func called with args:', args)
            AssistfulNLATool._validate_missing_fields(user_query, args, fields_dict, tool_memory)

            if headers:
                headers.update(**DEFAULT_HEADERS)

            response, response_json = AssistfulNLATool._exec_api_operation(api_operation, args, headers)
            return f'Status: {response.status_code} {response.reason}\n{RESPONSE_PREFIX}{response_json}'

        return tool_func

    @classmethod
    def _validate_missing_fields(
        cls,
        user_query: str,
        args: dict[str, Any],
        fields_dict: dict[str, dict],
        tool_memory: set[str]
    ) -> None:
        if not user_query or not args or not any(args) or not fields_dict or not any(fields_dict):
            return

        if not tool_memory:
            tool_memory = set()

        # Do we need to worry about nested required fields?
        missing_fields = []
        required_fields: set = {key for key, field in fields_dict.items() if field.get('required')}
        for key, value in args.items():
            # The LLM fills in required fields with random garbage when not provided by the user.
            # Adding a check for if the value is not in the user query, prevents LLM hallucinated arguments.
            value_str = str(value)
            if key in required_fields and value_str not in user_query and value_str not in tool_memory:
                missing_fields.append(key)

        if any(missing_fields):
            raise ToolException(f'Missing required fields: {missing_fields}')

    @classmethod
    def _exec_api_operation(
            cls,
            api_operation: AssistfulAPIOperation,
            args: dict[str, Any],
            headers: Optional[dict] = None
    ) -> tuple[Response, str]:
        response = None
        response_json = {}
        url = f'{api_operation.base_url}{api_operation.path}'
        for path_param in api_operation.path_params:
            url = url.replace(f'{{{path_param}}}', args[path_param])

        try:
            if api_operation.method == HTTPVerb.GET:
                response = get(url, data=dumps(args), params={}, headers=headers)
            elif api_operation.method == HTTPVerb.POST:
                response = post(url, data=dumps(args), params={}, headers=headers)
            elif api_operation.method == HTTPVerb.PUT:
                response = put(url, data=dumps(args), params={}, headers=headers)
            elif api_operation.method == HTTPVerb.PATCH:
                response = patch(url, data=dumps(args), params={}, headers=headers)
            elif api_operation.method == HTTPVerb.DELETE:
                response = delete(url, data=dumps(args), params={}, headers=headers)

            response_json = response.json()
            response.raise_for_status()
        except JSONDecodeError:
            response_json = {}
        except Exception as ex:
            error_message = response_json.get('message') or response.text or str(ex)
            raise ToolException(error_message)

        return response, dumps(response_json)

    @classmethod
    def _handle_error(cls, error: ToolException) -> str:
        return f'STOP! Tell the user there was an error: "{error.args[0]}"'
