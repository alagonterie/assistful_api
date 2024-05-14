from firebase_admin.firestore import firestore as fs
from marshmallow import Schema, fields, post_load

from shared.globals.enums import ChatbotTemperaments
from shared.models.base_dto import BaseDTOFactory, BaseDTO
from shared.models.data_class.chatbot_temperament_dc import ChatbotTemperamentDC


class ChatbotDTO(ChatbotTemperamentDC, BaseDTO):
    """Class representing a Chatbot.

    :param chatbot_id: The ID of the chatbot.
    :type chatbot_id: str
    :param context: The context of the chatbot.
    :type context: str
    """

    @staticmethod
    def id_name() -> str:
        return 'chatbot_id'

    def id_value(self) -> str:
        return self.chatbot_id

    def __init__(self,
                 chatbot_id: str = None,
                 context: str = None,
                 temperament: ChatbotTemperaments | str = None,
                 temperature: float = None,
                 top_k: int = None,
                 top_p: float = None):
        self.chatbot_id = chatbot_id
        self.context = context

        super().__init__(temperament, temperature, top_k, top_p)


class ChatbotDTOFactory(BaseDTOFactory):
    """
    Creates ChatbotDTO objects from DocumentSnapshots.
    """

    @staticmethod
    def create_from_doc(doc_snapshot: fs.DocumentSnapshot) -> ChatbotDTO | None:
        return BaseDTOFactory.doc_to_object(ChatbotSchema(), doc_snapshot, ChatbotDTO.id_name())


class ChatbotSchema(Schema):
    """Schema for the Chatbot model"""

    chatbot_id = fields.Str()
    context = fields.Str()

    temperament = fields.Str()
    temperature = fields.Float()
    top_k = fields.Integer()
    top_p = fields.Float()

    @post_load
    def make_chatbot(self, data, **_kwargs):
        return ChatbotDTO(**data)
