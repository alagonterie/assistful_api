from dataclasses import dataclass
from http import HTTPStatus

import flask

from shared.globals.constants import INSUFFICIENT_ACCESS
from shared.globals.enums import AccessLevels


@dataclass
class UserContext(object):
    """
    The UserContext class represents the context of a user in the system.

    :param user_id: The ID of the user.
    :type user_id: str, optional
    :param org_id: The ID of the organization the user belongs to.
    :type org_id: str, optional
    :param access_level: The access level of the user.
    :type access_level: AccessLevels, optional
    """
    user_id: str = None
    org_id: str = None
    access_level: AccessLevels = None

    def abort_if_insufficient_access(self, access_level: AccessLevels) -> None:
        """
        Aborts the current request and returns an unauthorized response if the user's access level is insufficient.

        :param access_level: The required access level needed for the operation.
        """
        if self.access_level is not None and self.access_level.value < access_level.value:
            flask.abort(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
