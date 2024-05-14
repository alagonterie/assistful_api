from firebase_admin.firestore import firestore as fs
from marshmallow import Schema, fields, post_load

from shared.models.base_dto import BaseDTOFactory, BaseDTO


class AssistantDTO(BaseDTO):
    """Class representing an Assistant.

    :param assistant_id: The ID of the assistant.
    :type assistant_id: str
    :param context: The context of the assistant.
    :type context: str
    """

    @staticmethod
    def id_name() -> str:
        return 'assistant_id'

    def id_value(self) -> str:
        return self.assistant_id

    def __init__(self,
                 assistant_id: str = None,
                 context: str = None):
        self.assistant_id = assistant_id
        self.context = context


class AssistantDTOFactory(BaseDTOFactory):
    """
    Creates AssistantDTO objects from DocumentSnapshots.
    """

    @staticmethod
    def create_from_doc(doc_snapshot: fs.DocumentSnapshot) -> AssistantDTO | None:
        return BaseDTOFactory.doc_to_object(AssistantSchema(), doc_snapshot, AssistantDTO.id_name())


class AssistantSchema(Schema):
    """Schema for the Assistant model"""

    assistant_id = fields.Str()
    context = fields.Str()

    @post_load
    def make_assistant(self, data, **_kwargs):
        return AssistantDTO(**data)
