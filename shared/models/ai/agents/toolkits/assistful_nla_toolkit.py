from __future__ import annotations

from abc import ABC
from typing import List, Sequence, cast

from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.pydantic_v1 import Field
from langchain.tools import BaseTool
from langchain.tools.openapi.utils.openapi_utils import OpenAPISpec

from shared.models.ai.agents.tools.assistful_nla_tool import AssistfulNLATool


class AssistfulNLAToolkit(BaseToolkit, ABC):
    """
    Toolkit for creating AssistfulTools.

    This toolkit provides tools for performing natural language API operations.
    It is used to create tools for each operation defined in the OpenAPI specification.
    """

    nla_tools: Sequence[AssistfulNLATool] = Field(...)
    """List of API Endpoint Tools."""

    # noinspection PyUnresolvedReferences
    @staticmethod
    def _get_http_operation_tools(spec: OpenAPISpec) -> List[AssistfulNLATool]:
        """Get the tools for all the API operations."""
        if not spec.paths:
            return []
        http_operation_tools = []
        for path in spec.paths:
            for method in spec.get_methods_for_path(path):
                endpoint_tool = AssistfulNLATool.from_spec(
                    path=path,
                    method=method,
                    spec=spec,
                )
                http_operation_tools.append(endpoint_tool)
        return http_operation_tools

    @classmethod
    def from_spec(cls, spec: OpenAPISpec) -> AssistfulNLAToolkit:
        """Instantiate the toolkit by creating tools for each operation."""
        http_operation_tools = cls._get_http_operation_tools(spec)
        return cls(nla_tools=http_operation_tools)

    def get_tools(self) -> List[BaseTool]:
        return [cast(BaseTool, tool) for tool in self.nla_tools]

