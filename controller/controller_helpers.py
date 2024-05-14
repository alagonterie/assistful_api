from enum import Enum
from http import HTTPStatus
from typing import Any, Type, TypeVar

import flask
from flask import make_response as old_make_response, Response, request

from provider.provider_modules.auth_provider import get_logged_in_user
from shared.globals.enums import CustomClaimKeys, AccessLevels
from shared.models.security.user_context import UserContext


def create_user_context() -> UserContext:
    """
    Create a UserContext object based on the logged in user.

    :return: UserContext object representing the logged in user.
    """
    user = get_logged_in_user()

    user_id = user.uid
    org_id = str(user.custom_claims[CustomClaimKeys.ORG_ID.value])
    access_level = AccessLevels(user.custom_claims[CustomClaimKeys.ACCESS_LEVEL.value])
    return UserContext(user_id=user_id, org_id=org_id, access_level=access_level)


def make_response(data: dict | Any = None, status: HTTPStatus = HTTPStatus.OK) -> tuple[dict | list, HTTPStatus] | Response:
    """
    Create a Flask response object.

    :param data: The response data as a dictionary or any other object.
    :param status: The HTTP status code for the response (default: 200 OK).
    :return: A tuple containing the response data and the HTTP status code, or a Flask response object.
    """

    if isinstance(data, (dict, list)):
        return data if data is not None else {}, status
    elif data:
        return data.__dict__, status
    else:
        return old_make_response({}, status)


def from_uri(query_param_names: str | tuple[str, ...]) -> str | tuple[str, ...]:
    """
    Extracts field values from query parameters in a URI.

    :param query_param_names: A string or tuple of strings representing the names of the query parameters.
    :return: The extracted field value(s).
    """

    def __extract_field_value_from_uri(query_param_name: str) -> str:
        value = request.args.get(query_param_name)
        return None if value is None or str(value) == 'None' else str(value)

    if isinstance(query_param_names, str):
        return __extract_field_value_from_uri(query_param_names)

    return tuple([__extract_field_value_from_uri(query_param_name) for query_param_name in query_param_names])


def from_body(field_names: str | tuple[str, ...]) -> str | tuple[str, ...]:
    """
    Extracts field values from the request body.

    :param field_names: The name(s) of the field(s) to extract from the request body.
    :return: The extracted field value(s) as a string or tuple of strings.
    """

    def __extract_field_value_from_body(field_name: str) -> str:
        value = flask.request.json.get(field_name)
        return str(value) if value is not None else None

    if isinstance(field_names, str):
        return __extract_field_value_from_body(field_names)

    return tuple([__extract_field_value_from_body(field_name) for field_name in field_names])


TEnum = TypeVar('TEnum', bound=Enum)


def validate_enum(name: str, value: str | None, enum_class: Type[TEnum]) -> TEnum | None:
    """
    Validates a string against a given enum. If the string is a valid name of an enum member,
    returns the corresponding enum member. Otherwise, aborts with a HTTP 400 error.

    :param name: The name of the field being validated.
    :param value: The string to validate.
    :param enum_class: The enum class to validate against.
    :return: The corresponding enum member if the string is valid.
    """

    if value is None:
        return None

    for item in enum_class:
        if item.name == value:
            return item

    error = f'Invalid {name}, expected one of: {", ".join([e.name for e in enum_class])}'
    flask.abort(HTTPStatus.BAD_REQUEST, error)
