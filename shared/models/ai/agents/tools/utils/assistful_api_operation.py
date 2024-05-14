# TODO: This might not be necessary at all

import logging
from enum import Enum
from typing import (
    Dict,
    List,
    Optional,
    Sequence,
)

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools.openapi.utils.api_models import APIProperty, APIRequestBody, INVALID_LOCATION_TEMPL, \
    APIRequestBodyProperty, SCHEMA_TYPE, _SUPPORTED_MEDIA_TYPES, APIPropertyLocation, APIOperation
from langchain.tools.openapi.utils.openapi_utils import HTTPVerb, OpenAPISpec
from openapi_schema_pydantic import Parameter, MediaType, Response

logger = logging.getLogger(__name__)
PRIMITIVE_TYPES = {
    "integer": int,
    "number": float,
    "string": str,
    "boolean": bool,
    "array": List,
    "object": Dict,
    "null": None,
}


# TODO: Response support?
class AssistfulAPIResponseProperty(BaseModel):
    """Base model for an API response property."""

    name: str = Field(alias="name")
    """The name of the property."""

    type: SCHEMA_TYPE = Field(alias="type")
    """The type of the property.

    Either a primitive type, a component/parameter type,
    or an array or 'object' (dict) of the above."""

    description: Optional[str] = Field(alias="description", default=None)
    """The description of the property."""


# TODO: Response support?
class AssistfulAPIResponse(BaseModel):
    """A model for a request body."""

    description: Optional[str] = Field(alias="description")
    """The description of the request body."""

    properties: List[APIRequestBodyProperty] = Field(alias="properties")

    # E.g., application/json - we only support JSON at the moment.
    media_type: str = Field(alias="media_type")
    """The media type of the request body."""

    @classmethod
    def _process_supported_media_type(
            cls,
            media_type_obj: MediaType,
            spec: OpenAPISpec,
    ) -> List[APIRequestBodyProperty]:
        """Process the media type of the request body."""
        from openapi_schema_pydantic import Reference

        references_used = []
        schema = media_type_obj.media_type_schema
        if isinstance(schema, Reference):
            references_used.append(schema.ref.split("/")[-1])
            schema = spec.get_referenced_schema(schema)
        if schema is None:
            raise ValueError(
                f"Could not resolve schema for media type: {media_type_obj}"
            )
        api_request_body_properties = []
        required_properties = schema.required or []
        if schema.type == "object" and schema.properties:
            for prop_name, prop_schema in schema.properties.items():
                if isinstance(prop_schema, Reference):
                    prop_schema = spec.get_referenced_schema(prop_schema)

                api_request_body_properties.append(
                    APIRequestBodyProperty.from_schema(
                        schema=prop_schema,
                        name=prop_name,
                        required=prop_name in required_properties,
                        spec=spec,
                    )
                )
        else:
            api_request_body_properties.append(
                APIRequestBodyProperty(
                    name="body",
                    required=True,
                    type=schema.type,
                    default=schema.default,
                    description=schema.description,
                    properties=[],
                    references_used=references_used,
                )
            )

        return api_request_body_properties

    @classmethod
    def from_request_body(
            cls, response: Response, spec: OpenAPISpec
    ) -> "AssistfulAPIResponse":
        """Instantiate from an OpenAPI RequestBody."""
        properties = []
        for media_type, media_type_obj in response.content.items():
            if media_type not in _SUPPORTED_MEDIA_TYPES:
                continue
            api_request_body_properties = cls._process_supported_media_type(
                media_type_obj,
                spec,
            )
            properties.extend(api_request_body_properties)

        # noinspection PyUnboundLocalVariable
        return cls(
            description=response.description,
            properties=properties,
            media_type=media_type,
        )


class AssistfulAPIOperation(APIOperation):
    """A model for a single API operation."""

    api_title: str = Field(alias="api_title")
    """The title of the API."""

    base_url: str = Field(alias="base_url")
    """The base URL of the operation."""

    path: str = Field(alias="path")
    """The path of the operation."""

    method: HTTPVerb = Field(alias="method")
    """The HTTP method of the operation."""

    operation_id: str = Field(alias="operation_id")
    """The unique identifier of the operation."""

    description: Optional[str] = Field(alias="description")
    """The description of the operation."""

    properties: Sequence[APIProperty] = Field(alias="properties")

    # TODO: Add parse in used components to be able to specify what type of
    # referenced object it is.
    # """The properties of the operation."""
    # components: Dict[str, BaseModel] = Field(alias="components")

    request_body: Optional[APIRequestBody] = Field(alias="request_body")
    """The request body of the operation."""

    # TODO: Response support?
    # response: Optional[APIResponse] = Field(alias="response")
    # """The response of the operation."""

    @staticmethod
    def _get_properties_from_parameters(
            parameters: List[Parameter], spec: OpenAPISpec
    ) -> List[APIProperty]:
        """Get the properties of the operation."""
        properties = []
        for param in parameters:
            if APIProperty.is_supported_location(param.param_in):
                properties.append(APIProperty.from_parameter(param, spec))
            elif param.required:
                raise ValueError(
                    INVALID_LOCATION_TEMPL.format(
                        location=param.param_in, name=param.name
                    )
                )
            else:
                logger.warning(
                    INVALID_LOCATION_TEMPL.format(
                        location=param.param_in, name=param.name
                    )
                    + " Ignoring optional parameter"
                )
                pass
        return properties

    @classmethod
    def from_openapi_spec(
            cls,
            spec: OpenAPISpec,
            path: str,
            method: str,
    ) -> "AssistfulAPIOperation":
        """Create an AssistfulAPIOperation from an OpenAPI spec."""
        # noinspection PyUnresolvedReferences
        api_title = spec.info.title
        operation = spec.get_operation(path, method)
        parameters = spec.get_parameters_for_operation(operation)
        properties = cls._get_properties_from_parameters(parameters, spec)
        operation_id = OpenAPISpec.get_cleaned_operation_id(operation, path, method)

        request_body = spec.get_request_body_for_operation(operation)
        api_request_body = (
            APIRequestBody.from_request_body(request_body, spec)
            if request_body is not None
            else None
        )

        # TODO: Response support?
        # response = spec.get_response_for_operation(operation)
        # api_response = (
        #     APIResponse.from_response(response, spec)
        #     if response is not None
        #     else None
        # )

        description = operation.description or operation.summary
        # noinspection PyUnresolvedReferences
        if not description and spec.paths is not None:
            # noinspection PyUnresolvedReferences
            description = spec.paths[path].description or spec.paths[path].summary
        return cls(
            api_title=api_title,
            operation_id=operation_id,
            description=description or "",
            base_url=spec.base_url,
            path=path,
            method=method,
            properties=properties,
            request_body=api_request_body,
            # TODO: Response support?
            # response=api_response,
        )

    @staticmethod
    def ts_type_from_python(type_: SCHEMA_TYPE) -> str:
        if type_ is None:
            # TODO: Handle Nones better. These often result when
            # parsing specs that are < v3
            return "any"
        elif isinstance(type_, str):
            return {
                "str": "string",
                "integer": "number",
                "float": "number",
                "date-time": "string",
            }.get(type_, type_)
        elif isinstance(type_, tuple):
            return f"Array<{AssistfulAPIOperation.ts_type_from_python(type_[0])}>"
        elif isinstance(type_, type) and issubclass(type_, Enum):
            return " | ".join([f"'{e.value}'" for e in type_])
        else:
            return str(type_)

    def _format_nested_properties(
            self, properties: List[APIRequestBodyProperty], indent: int = 2
    ) -> str:
        """Format nested properties."""
        formatted_props = []

        for prop in properties:
            prop_name = prop.name
            prop_type = self.ts_type_from_python(prop.type)
            prop_required = "" if prop.required else "?"
            prop_desc = f"/* {prop.description} */" if prop.description else ""

            if prop.properties:
                nested_props = self._format_nested_properties(
                    prop.properties, indent + 2
                )
                prop_type = f"{{\n{nested_props}\n{' ' * indent}}}"

            formatted_props.append(
                f"{prop_desc}\n{' ' * indent}{prop_name}"
                f"{prop_required}: {prop_type},"
            )

        return "\n".join(formatted_props)

    def to_typescript(self) -> str:
        """Get typescript string representation of the operation."""
        operation_name = self.operation_id
        params = []

        if self.request_body:
            formatted_request_body_props = self._format_nested_properties(
                self.request_body.properties
            )
            params.append(formatted_request_body_props)

        for prop in self.properties:
            prop_name = prop.name
            prop_type = self.ts_type_from_python(prop.type)

            prop_required = "REQUIRED | " if prop.required else ""
            prop_desc = f"/* {prop_required}{prop.description} */" if prop.description else ""

            params.append(
                f"{prop_desc}\n\t\t{prop_name}{'' if prop.required else '?'}: {prop_type},"
            )

        formatted_params = "\n".join(params).strip()
        description_str = f"/* {self.description} */" if self.description else ""
        typescript_definition = f"""
{description_str}
type {operation_name} = (_: {{
{formatted_params}
}}) => any;
"""  # TODO: Instead of "any" above, we could use the response model name and append the typescript model def below?
        return typescript_definition.strip()

    @property
    def query_params(self) -> List[str]:
        return [
            prop.name
            for prop in self.properties
            if prop.location == APIPropertyLocation.QUERY
        ]

    @property
    def path_params(self) -> List[str]:
        return [
            prop.name
            for prop in self.properties
            if prop.location == APIPropertyLocation.PATH
        ]

    @property
    def body_params(self) -> List[str]:
        if self.request_body is None:
            return []
        return [prop.name for prop in self.request_body.properties]
