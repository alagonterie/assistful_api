"""Chain that makes API calls and summarizes the responses to answer a question."""
import json
from typing import Any, Dict, Optional, cast

from langchain.callbacks.manager import CallbackManagerForChainRun, Callbacks
from langchain.chains import OpenAPIEndpointChain
from langchain.chains.api.openapi.response_chain import APIResponderChain
from langchain.schema.language_model import BaseLanguageModel
from langchain.utilities.requests import Requests
from requests import Response

from shared.models.ai.chains.assistful_api_requester_chain import AssistfulAPIRequesterChain
from shared.models.ai.agents.tools.utils.assistful_api_operation import AssistfulAPIOperation


class AssistfulOpenAPIEndpointChain(OpenAPIEndpointChain):
    """Chain interacts with an OpenAPI endpoint using natural language."""

    def _call(
            self,
            inputs: Dict[str, Any],
            run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()

        instructions = inputs[self.instructions_key]
        instructions = instructions[: self.max_text_length]

        _api_arguments = self.api_request_chain.predict_and_parse(
            instructions=instructions,
            callbacks=_run_manager.get_child()
        )
        api_arguments = cast(str, _api_arguments)

        _run_manager.on_text(api_arguments, color="green", end="\n", verbose=self.verbose)

        intermediate_steps = {"request_args": api_arguments}
        if api_arguments.startswith("ERROR"):
            return self._get_output(api_arguments, intermediate_steps)
        elif api_arguments.startswith("MESSAGE:"):
            return self._get_output(api_arguments[len("MESSAGE:"):], intermediate_steps)

        try:
            request_args = self.deserialize_json_input(api_arguments)
            method = getattr(self.requests, self.api_operation.method.value)

            api_response: Response = method(**request_args)
            api_response.raise_for_status()

            from requests.exceptions import JSONDecodeError
            try:
                json_response = json.dumps(api_response.json())
            except JSONDecodeError:
                json_response = None

            method_str = str(self.api_operation.method.value)
            response_text = (
                    f"{api_response.status_code}: {api_response.reason}"
                    + f"\nFor {method_str.upper()} {request_args['url']}"
                    + (f"\nCalled with args: {request_args['params']}" if any(request_args['params']) else '')
                    + (f"\nResponded with: {json_response}" if json_response else '')
            )
        except Exception as e:
            response_text = f"Error with message: {str(e)}"

        response_text = response_text[: self.max_text_length]
        intermediate_steps["response_text"] = response_text

        _run_manager.on_text(response_text, color="blue", end="\n", verbose=self.verbose)

        if self.api_response_chain is not None:
            _answer = self.api_response_chain.predict_and_parse(
                response=response_text,
                instructions=instructions,
                callbacks=_run_manager.get_child(),
            )
            answer = cast(str, _answer)

            _run_manager.on_text(answer, color="yellow", end="\n", verbose=self.verbose)

            return self._get_output(answer, intermediate_steps)
        else:
            return self._get_output(response_text, intermediate_steps)

    @classmethod
    def from_api_operation(
            cls,
            operation: AssistfulAPIOperation,
            llm: BaseLanguageModel,
            requests: Optional[Requests] = None,
            verbose: bool = False,
            return_intermediate_steps: bool = False,
            raw_response: bool = False,
            callbacks: Callbacks = None,
            **kwargs: Any
    ) -> "AssistfulOpenAPIEndpointChain":
        """Create an AssistfulOpenAPIEndpointChain from an operation and a spec."""
        # noinspection PyProtectedMember
        from langchain.chains.api.openapi.chain import _ParamMapping
        param_mapping = _ParamMapping(
            query_params=operation.query_params,
            body_params=operation.body_params,
            path_params=operation.path_params,
        )

        requests_chain = AssistfulAPIRequesterChain.from_llm_and_typescript(
            llm,
            typescript_definition=operation.to_typescript(),
            verbose=verbose,
            callbacks=callbacks,
        )

        if raw_response:
            response_chain = None
        else:
            response_chain = APIResponderChain.from_llm(
                llm,
                verbose=verbose,
                callbacks=callbacks
            )

        _requests = requests or Requests()
        return cls(
            api_request_chain=requests_chain,
            api_response_chain=response_chain,
            api_operation=operation,
            requests=_requests,
            param_mapping=param_mapping,
            verbose=verbose,
            return_intermediate_steps=return_intermediate_steps,
            callbacks=callbacks,
            **kwargs,
        )
