from firebase_admin.firestore import firestore as fs

from repository.base_repo import GenericRepo
from repository.firestore import db
from shared.globals.constants import FIELD_ORG_ID
from shared.models.dto.chat_dto import ChatDTO, ChatDTOFactory
from shared.models.security.user_context import UserContext

CHAT_DB = db.collection('chats')
CHATS = GenericRepo[ChatDTO]('Chat', CHAT_DB, ChatDTOFactory)


def get(ctx: UserContext, chat_id: str) -> ChatDTO | None:
    """
    Retrieve a specific chat by its chat_id.

    :param ctx: The user context.
    :param chat_id: The ID of the chat to retrieve.
    :return: The ChatDTO object if the chat is found, otherwise None.
    """
    chat = CHATS.get(ctx, chat_id)
    return chat


def get_by_chatbot_id(ctx: UserContext, chatbot_id: str) -> list[ChatDTO] | None:
    """
    Retrieves a list of ChatDTO objects based on the chatbot ID.

    :param ctx: The user context.
    :param chatbot_id: The chatbot ID to filter the chats by.
    :return: A list of ChatDTO objects or None if no chats are found.
    """
    chat_docs = (CHAT_DB
                 .where(filter=fs.FieldFilter('respondent_id', '==', chatbot_id))
                 .where(filter=fs.FieldFilter(FIELD_ORG_ID, '==', ctx.org_id))
                 .get())

    return [ChatDTOFactory.create_from_doc(chat_doc) for chat_doc in chat_docs]


def get_all(ctx: UserContext) -> list[ChatDTO | None]:
    """
    Retrieves all chat objects.

    :param ctx: User context.
    :return: A list of ChatDTO objects or None if there are no chats found.
    """
    all_chats = CHATS.get_all(ctx)
    return all_chats


def insert(ctx: UserContext, chat: ChatDTO) -> str:
    """
    Inserts a new chat into the database.

    :param ctx: The user context.
    :param chat: The chat DTO to be inserted.
    :return: The ID of the new chat.
    """
    new_chat_id = CHATS.insert(ctx, chat)
    return new_chat_id


def add_to_history(ctx: UserContext, chat_id: str, new_messages: list[str]) -> None:
    """
    Add new messages to the chat history.

    :param ctx: The user context.
    :param chat_id: The ID of the chat.
    :param new_messages: List of new messages to be added.
    """
    CHATS.add_elements(ctx, chat_id, 'history', new_messages)
