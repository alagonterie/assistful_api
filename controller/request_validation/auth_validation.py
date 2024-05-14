from http import HTTPStatus
from typing import Any
from functools import wraps

import flask

from provider.provider_modules import auth_provider
from shared.globals.constants import INSUFFICIENT_ACCESS
from shared.globals.enums import AccessLevels, CustomClaimKeys


def signed_in(required_access_level=AccessLevels.SERVICE) -> Any:
    """
    Decorator that checks if the user is signed in with the required access level.

    :param required_access_level: The minimum access level required for the user. Defaults to `AccessLevels.SERVICE`.
    :return: The wrapped function.
    """

    def outer_func(func_to_wrap):
        @wraps(func_to_wrap)
        def inner_func(*args, **kwargs):
            _signed_in(required_access_level)

            response = func_to_wrap(*args, **kwargs)
            return response

        return inner_func

    return outer_func


def _signed_in(required_access_level=AccessLevels.SERVICE) -> Any:
    """
    Checks if the user is signed in with the required access level.

    :param required_access_level: The minimum access level required for the user to be considered signed in.
           Defaults to AccessLevels.BROWSER.
    :return: Returns None if the user is signed in with the required access level.
    :raises flask.abort(401): If the user is not signed in.
    :raises flask.abort(500): If there's an error verifying the ID token.
    :raises flask.abort(401): If the user has insufficient access level.
    """

    user = auth_provider.get_logged_in_user()

    if user.custom_claims[CustomClaimKeys.ACCESS_LEVEL.value] < required_access_level.value:
        return flask.abort(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
