from repository.base_repo import GenericRepo
from repository.firestore import db
from shared.models.dto.example_dto import ExampleDTO, ExampleDTOFactory
from shared.models.security.user_context import UserContext

EXAMPLES = GenericRepo[ExampleDTO]('Example', db.collection('examples'), ExampleDTOFactory)


def get(ctx: UserContext, example_id: str) -> ExampleDTO | None:
    """
    Retrieve an example with the given ID.

    :param ctx: The user context for the request.
    :param example_id: The ID of the example to retrieve.
    :return: An object representing the example with the given ID, or None if not found.
    """
    example = EXAMPLES.get(ctx, example_id)
    return example


def get_all(ctx: UserContext) -> list[ExampleDTO | None]:
    """
    Retrieve all examples from the Firestore database.

    :param ctx: The user context for the request.
    :return: A list of objects representing the example documents.
             Each object contains properties for the fields in the document.
    """
    all_examples = EXAMPLES.get_all(ctx, )
    return all_examples


def insert(ctx: UserContext, details: str) -> str:
    """
    Insert a new example document with the given details into the Firestore database.

    :param ctx: The user context for the request.
    :param details: The details of the example document.
    :return: The ID of the newly created example document.
    """
    new_example_id = EXAMPLES.insert(ctx, ExampleDTO(details=details))
    return new_example_id


def update_details(ctx: UserContext, example_id: str, details: str) -> None:
    """
    Update the details of an example with the given example_id.

    :param ctx: The user context for the request.
    :param example_id: The unique identifier of the example.
    :param details: The new details to be set for the example.
    """
    EXAMPLES.update(ctx, ExampleDTO(example_id=example_id, details=details))


def delete(ctx: UserContext, example_id: str) -> None:
    """
    Delete an example from the database.

    :param ctx: The user context for the request.
    :param example_id: The ID of the example to be deleted.
    """
    EXAMPLES.delete(ctx, example_id)
