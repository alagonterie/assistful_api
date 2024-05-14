from json import loads
from typing import Optional, Any
from uuid import UUID

from langchain.callbacks.base import BaseCallbackHandler

from shared.models.ai.assistful_prompts import RESPONSE_PREFIX


class ToolMemoryCallbackHandler(BaseCallbackHandler):
    def __init__(self, tool_memory: set[str]):
        self.tool_memory = tool_memory

    def on_tool_end(
        self,
        output: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any
    ) -> Any:
        if RESPONSE_PREFIX in output:
            json_output_str = output.split(RESPONSE_PREFIX)[-1]
            new_values = self.get_lowest_level_values(json_output_str)

            self.tool_memory.update(new_values)
            print('Tool memory updated:', self.tool_memory)

        return super().on_tool_end(
            output,
            run_id=run_id,
            parent_run_id=parent_run_id,
            **kwargs
        )

    @staticmethod
    def get_lowest_level_values(json_str: str) -> set[str]:
        json = loads(json_str)
        values = set()

        def process(data: Any):
            if isinstance(data, dict):
                for value in data.values():
                    process(value)
            elif isinstance(data, list):
                for item in data:
                    process(item)
            else:
                values.add(str(data))

        process(json)
        return values
