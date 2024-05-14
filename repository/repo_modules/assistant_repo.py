from repository.base_repo import GenericRepo
from repository.firestore import db
from shared.models.dto.assistant_dto import AssistantDTO, AssistantDTOFactory
from shared.models.security.user_context import UserContext

ASSISTANTS = GenericRepo[AssistantDTO]('Assistant', db.collection('assistants'), AssistantDTOFactory)


def get(ctx: UserContext, assistant_id: str) -> AssistantDTO | None:
    """
    Retrieve an assistant with the given ID.

    :param ctx: The user context for the request.
    :param assistant_id: The ID of the assistant to retrieve.
    :return: An object representing the assistant with the given ID, or None if not found.
    """
    assistant = ASSISTANTS.get(ctx, assistant_id)
    return assistant


def get_all(ctx: UserContext) -> list[AssistantDTO | None]:
    """
    Retrieve all assistants from the Firestore database.

    :param ctx: The user context for the request.
    :return: A list of objects representing the assistant documents.
             Each object contains properties for the fields in the document.
    """
    all_assistants = ASSISTANTS.get_all(ctx)
    return all_assistants


def insert(ctx: UserContext, context: str) -> str:
    """
    Insert a new assistant document with the given context into the Firestore database.

    :param ctx: The user context for the request.
    :param context: The context of the assistant document.
    :return: The ID of the newly created assistant document.
    """
    new_assistant_id = ASSISTANTS.insert(ctx, AssistantDTO(context=context))
    return new_assistant_id
