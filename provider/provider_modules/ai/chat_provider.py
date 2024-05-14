from google.oauth2 import service_account
from langchain.chat_models import ChatVertexAI
from langchain.schema import HumanMessage, SystemMessage

from repository.firestore import FIREBASE_CREDS
from repository.repo_modules import chat_repo, chatbot_repo
from shared.globals.constants import MAX_OUTPUT_TOKENS
from shared.models.data_class.chat_message_dc import ChatMessageDC
from shared.models.data_class.chatbot_temperament_dc import ChatbotTemperamentDC
from shared.models.dto.chat_dto import ChatDTO
from shared.models.security.user_context import UserContext


def get_chats(ctx: UserContext, chatbot_id: str) -> list[ChatDTO]:
    """
    This method retrieves chats based on the provided parameters.
    If the chatbot ID is None, it returns all chats from the chat repository.
    Otherwise, it returns chats that belong to the specified chatbot ID.

    :param ctx: UserContext object representing the user context
    :param chatbot_id: String representing the ID of the chatbot
    :return: List of ChatDTO objects representing the chats
    """
    if chatbot_id is None:
        return chat_repo.get_all(ctx)

    return chat_repo.get_by_chatbot_id(ctx, chatbot_id)


def get_chat_messages(ctx: UserContext, chat_id: str) -> list[ChatMessageDC]:
    """
    Retrieve chat messages for a given chat ID.

    :param ctx: UserContext object representing the user's context and permissions.
    :param chat_id: ID of the chat for which to retrieve messages.
    :return: A list of ChatMessageDC objects representing the chat messages.
    """
    chat = chat_repo.get(ctx, chat_id)
    return chat.messages()


def start_chat(ctx: UserContext, chatbot_id: str, message: str) -> ChatDTO:
    """
    Starts a chat conversation with a chatbot.

    :param ctx: The UserContext object representing the current user's context.
    :param chatbot_id: The ID of the chatbot to start the conversation with.
    :param message: The initial message to send to the chatbot.
    :return: The ChatDTO object representing the new chat conversation.
    """
    chatbot = chatbot_repo.get(ctx, chatbot_id)
    initial_messages = [
        SystemMessage(content=chatbot.context),
        HumanMessage(content=message)
    ]

    chat_vertex = _get_chat_vertex(chatbot)
    response_message = chat_vertex(initial_messages)

    history = [chatbot.context, message, response_message.content.strip()]
    temperament_fields = chatbot.get_temperament_fields()

    new_chat = ChatDTO(initiator_id=ctx.user_id, respondent_id=chatbot_id, history=history, **temperament_fields)
    new_chat_id = chat_repo.insert(ctx, new_chat)

    new_chat.chat_id = new_chat_id
    return new_chat


def continue_chat(ctx: UserContext, chat_id: str, new_message: str) -> ChatDTO:
    """
    Continues the chat by adding a new message, generating a response using ChatVertexAI,
    adding the new message and response to the chat history, and returning the response.

    :param ctx: The UserContext object representing the user's session context.
    :param chat_id: The ID of the chat.
    :param new_message: The new message to be added to the chat.
    :return: A ChatDTO object representing the response message from the chat.
    """
    chat = chat_repo.get(ctx, chat_id)
    chat.add_message(new_message)

    chat_vertex = _get_chat_vertex(chat)
    response_message = chat_vertex(chat.messages_langchain())

    response_content = response_message.content.strip()
    chat_repo.add_to_history(ctx, chat_id, [new_message, response_content])

    return ChatDTO(sender=chat.respondent_id, message=response_content)


def _get_chat_vertex(chatbot_temperament: ChatbotTemperamentDC) -> ChatVertexAI:
    """
    :param chatbot_temperament: A data class representing the temperament of the chatbot.
    :return: An instance of ChatVertexAI, which is a chatbot model used for generating responses.

    This method takes a ChatbotTemperamentDC object as a parameter and returns an instance of ChatVertexAI.
    Within the method, the chatbot temperament fields are extracted from the ChatbotTemperamentDC object and used
    as arguments to initialize the ChatVertexAI object.

    Additionally, the credentials are set to the FIREBASE_CREDS and
    the maximum number of output tokens is set to MAX_OUTPUT_TOKENS.
    The initialized ChatVertexAI object is then returned.
    """
    kwargs = chatbot_temperament.get_vertex_chat_fields()
    kwargs.update({
        'credentials': service_account.Credentials.from_service_account_info(FIREBASE_CREDS),
        'max_output_tokens': MAX_OUTPUT_TOKENS
    })

    chat_vertex = ChatVertexAI(**kwargs)
    return chat_vertex
