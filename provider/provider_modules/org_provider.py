from provider.provider_modules import auth_provider
from repository.repo_modules import org_repo
from shared.globals.objects import NO_USER_CONTEXT, OWNER_CONTEXT
from shared.models.dto.org_dto import OrgDTO
from shared.models.security.user_context import UserContext


def create_org_and_admin_owner_user(org_name: str, email: str, password: str) -> UserContext:
    """
    Create organization and the founding ADMIN_OWNER account.

    :param org_name: Name of the organization to be created.
    :param email: Email of the user.
    :param password: Password for the user account.
    :return: UserContext object containing the user ID and organization ID.
    """
    org_id = org_repo.insert(NO_USER_CONTEXT, org_name)

    def on_fail():
        org_repo.delete(OWNER_CONTEXT, org_id)

    user_id = auth_provider.create_admin_owner_user(email, password, org_id, on_fail)

    return UserContext(user_id=user_id, org_id=org_id)


def get_org_info(ctx: UserContext) -> OrgDTO:
    """Retrieves the organization information for the currently logged in user.

    :return: The organization information as an instance of OrgDTO.
    """
    org = org_repo.get(ctx, ctx.org_id)

    return org
