"""request parser."""

from typing import Any

from langchain.chains.api.openapi.requests_chain import APIRequesterChain, APIRequesterOutputParser
from langchain.chains.llm import LLMChain
from langchain.prompts.prompt import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel

from shared.models.ai.assistful_prompts import ASSISTFUL_REQUEST_TEMPLATE


class AssistfulAPIRequesterChain(APIRequesterChain):
    """Get the request parser."""

    @classmethod
    def from_llm_and_typescript(
            cls,
            llm: BaseLanguageModel,
            typescript_definition: str,
            verbose: bool = True,
            **kwargs: Any,
    ) -> LLMChain:
        """Get the request parser."""
        output_parser = APIRequesterOutputParser()
        prompt = PromptTemplate(
            template=ASSISTFUL_REQUEST_TEMPLATE,
            output_parser=output_parser,
            partial_variables={'schema': typescript_definition},
            input_variables=['instructions'],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose, **kwargs)
