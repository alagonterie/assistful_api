from firebase_admin.firestore import firestore as fs
from marshmallow import Schema, fields, post_load

from shared.models.base_dto import BaseDTOFactory, BaseDTO


class ToolDTO(BaseDTO):
    """Class representing a Tool.

    :param tool_id: The ID of the tool.
    :type tool_id: str
    :param api_operation: Contains various details about the API endpoint/operation
    :type api_operation: str
    """

    @staticmethod
    def id_name() -> str:
        return 'tool_id'

    def id_value(self) -> str:
        return self.tool_id

    def __init__(self,
                 tool_id: str = None,
                 api_operation: str = None):
        self.tool_id = tool_id
        self.api_operation = api_operation


class ToolDTOFactory(BaseDTOFactory):
    """
    Creates ToolDTO objects from DocumentSnapshots.
    """

    @staticmethod
    def create_from_doc(doc_snapshot: fs.DocumentSnapshot) -> ToolDTO | None:
        return BaseDTOFactory.doc_to_object(ToolSchema(), doc_snapshot, ToolDTO.id_name())


class ToolSchema(Schema):
    """Schema for the Tool model"""

    tool_id = fields.Str()
    api_operation = fields.Str()

    @post_load
    def make_tool(self, data, **_kwargs):
        return ToolDTO(**data)
