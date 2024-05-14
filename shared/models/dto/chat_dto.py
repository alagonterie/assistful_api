from firebase_admin.firestore import firestore as fs
from langchain.schema import BaseMessage, SystemMessage, HumanMessage, AIMessage
from marshmallow import Schema, fields, post_load

from shared.globals.enums import ChatbotTemperaments
from shared.models.base_dto import BaseDTOFactory, BaseDTO
from shared.models.data_class.chat_message_dc import ChatMessageDC
from shared.models.data_class.chatbot_temperament_dc import ChatbotTemperamentDC


class ChatDTO(ChatbotTemperamentDC, BaseDTO):
    """Class representing a Chat.

    :param chat_id: The ID of the chat.
    :type chat_id: str
    :param initiator_id: The ID of the one who initiated the chat.
    :type initiator_id: str
    :param respondent_id: The ID of the one who responded to the initiated chat.
    :type respondent_id: str
    :param sender: A description of the sender of the latest chat message.
    :type sender: str
    :param message: The text of the latest chat message.
    :type message: str
    :param history: The message history of the chat.
    :type history: list[str]
    """

    @staticmethod
    def id_name() -> str:
        return 'chat_id'

    def id_value(self) -> str:
        return self.chat_id

    def __init__(self,
                 chat_id: str = None,
                 initiator_id: str = None,
                 respondent_id: str = None,
                 sender: str = None,
                 message: str = None,
                 history: list[str] = None,
                 temperament: ChatbotTemperaments | str = None,
                 temperature: float = None,
                 top_k: int = None,
                 top_p: float = None):
        self.chat_id = chat_id
        self.initiator_id = initiator_id
        self.respondent_id = respondent_id
        self.sender = sender
        self.message = message
        self.history = history

        super().__init__(temperament, temperature, top_k, top_p)

        # Auto fill the latest sender and message if data is only coming from history (loading from DB).
        if self.sender is None and self.message is None and self.history is not None and len(self.history) >= 3:
            latest_message_idx = len(self.history) - 1
            latest_message = self.history[latest_message_idx]
            self.sender = self.initiator_id if latest_message_idx % 2 != 0 else self.respondent_id
            self.message = latest_message

    def messages(self) -> list[ChatMessageDC]:
        return [
            ChatMessageDC(
                sender=self.initiator_id if i % 2 == 0 else self.respondent_id,
                message=message
            )
            for i, message in enumerate(self.history[1:])
        ]

    def messages_langchain(self) -> list[BaseMessage]:
        return [
            SystemMessage(content=message) if i == 0 else
            HumanMessage(content=message) if i % 2 != 0 else
            AIMessage(content=message)
            for i, message in enumerate(self.history)
        ]

    def add_message(self, message: str) -> None:
        if self.history is None or len(self.history) < 3:
            raise Exception('Something is off with the chat history')

        self.history.append(message)


class ChatDTOFactory(BaseDTOFactory):
    """
    Creates ChatDTO objects from DocumentSnapshots.
    """

    @staticmethod
    def create_from_doc(doc_snapshot: fs.DocumentSnapshot) -> ChatDTO | None:
        return BaseDTOFactory.doc_to_object(ChatSchema(), doc_snapshot, ChatDTO.id_name())


class ChatSchema(Schema):
    """Schema for the Chat model"""

    chat_id = fields.Str()
    initiator_id = fields.Str()
    respondent_id = fields.Str()
    sender = fields.Str()
    message = fields.Str()
    history = fields.List(fields.Str())

    temperament = fields.Str()
    temperature = fields.Float()
    top_k = fields.Integer()
    top_p = fields.Float()

    @post_load
    def make_chat(self, data, **_kwargs):
        return ChatDTO(**data)
