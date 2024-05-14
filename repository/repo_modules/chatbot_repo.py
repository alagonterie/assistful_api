from repository.base_repo import GenericRepo
from repository.firestore import db
from shared.globals.enums import ChatbotTemperaments
from shared.models.dto.chatbot_dto import ChatbotDTO, ChatbotDTOFactory
from shared.models.security.user_context import UserContext

CHATBOTS = GenericRepo[ChatbotDTO]('Chatbot', db.collection('chatbots'), ChatbotDTOFactory)


def get(ctx: UserContext, chatbot_id: str) -> ChatbotDTO | None:
    """
    Fetches the ChatbotDTO object with the given chatbot_id.

    :param ctx: The UserContext object representing the current user's context.
    :param chatbot_id: The unique identifier of the chatbot.
    :return: Returns the fetched ChatbotDTO object if it exists, otherwise returns None.
    """
    chatbot = CHATBOTS.get(ctx, chatbot_id)
    return chatbot


def get_all(ctx: UserContext) -> list[ChatbotDTO | None]:
    """
    Retrieve all chatbots.

    :param ctx: User context.
    :return: List of ChatbotDTO or None.
    """
    all_chatbots = CHATBOTS.get_all(ctx)
    return all_chatbots


def insert(ctx: UserContext, context: str, temperament: ChatbotTemperaments = None) -> str:
    """
    Inserts a new chatbot into the database.

    :param ctx: The user context.
    :param context: The context of the chatbot.
    :param temperament: The temperament of the chatbot. Defaults to ChatbotTemperaments.FUN.
    :return: The ID of the newly inserted chatbot.
    """
    new_chatbot_id = CHATBOTS.insert(ctx, ChatbotDTO(context=context, temperament=temperament))
    return new_chatbot_id
