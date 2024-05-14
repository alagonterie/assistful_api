from repository.base_repo import GenericRepo
from repository.firestore import db
from shared.globals.constants import TYPE_NAME_ORG
from shared.models.dto.org_dto import OrgDTO, OrgDTOFactory
from shared.models.security.user_context import UserContext

ORGS = GenericRepo[OrgDTO](TYPE_NAME_ORG, db.collection('organizations'), OrgDTOFactory)


def get(ctx: UserContext, org_id: str) -> OrgDTO | None:
    """
    Retrieve an organization with the given ID.

    :param ctx: The user context for the request.
    :param org_id: The ID of the organization to retrieve.
    :return: An object representing the organization with the given ID, or None if not found.
    """
    org = ORGS.get(ctx, org_id)
    return org


def insert(ctx: UserContext, org_name: str) -> str:
    """
    Inserts a new organization into the Firestore database.

    :param ctx: The user context for the request.
    :param org_name: The name of the organization to insert.
    :return: The ID of the newly inserted organization document.
    """
    new_org_id = ORGS.insert(ctx, OrgDTO(org_name=org_name))
    return new_org_id


def delete(ctx: UserContext, org_id: str) -> None:
    """
    Delete an organization from the database.

    :param ctx: The user context for the request.
    :param org_id: The ID of the organization to be deleted.
    """
    ORGS.delete(ctx, org_id)
