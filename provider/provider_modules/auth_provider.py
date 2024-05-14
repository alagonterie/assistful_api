import json
from http import HTTPStatus
from typing import Any, Callable

import flask
from firebase_admin import auth
from firebase_admin.auth import UserRecord

from provider.provider_helpers import google_api_post
from shared.globals.constants import FIREBASE_API_KEY, OWNER_EMAIL
from shared.globals.enums import AccessLevels, CustomClaimKeys


def create_admin_owner_user(email: str, password: str, org_id: str, on_fail: Callable) -> str:
    """
    Creates an ADMIN_OWNER user in the system.

    :param on_fail: Operation called if the user failed to be created.
    :param email: The email address of the user.
    :param password: The password for the user account.
    :param org_id: The organization ID to associate with the user account.

    :return: The ID of the created user.
    """
    try:
        user_record = auth.create_user(email=email, password=password)
        auth.set_custom_user_claims(user_record.uid, {
            CustomClaimKeys.ACCESS_LEVEL.value: AccessLevels.OWNER.value if email == OWNER_EMAIL else AccessLevels.ADMIN_OWNER.value,
            CustomClaimKeys.ORG_ID.value: org_id
        })
    except ValueError as value_error:
        on_fail()
        flask.abort(HTTPStatus.BAD_REQUEST, value_error)
    except Exception as ex:
        on_fail()
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR, str(ex))

    if not user_record:
        on_fail()
        flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR, 'Unexpected error')

    user_id = user_record.uid
    return user_id


def sign_in_with_email_and_password(email: str, password: str) -> dict:
    """
    Sign in a user with email and password using Firebase Authentication.

    :param email: Email address of the user.
    :param password: Password of the user.
    :return: A dictionary containing the response data from the Firebase Authentication API.
    """
    url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}'
    data = json.dumps({'email': email, 'password': password, 'returnSecureToken': True})

    response = google_api_post(url, data)
    return response


def refresh_id_token(refresh_token: str) -> dict:
    """
    Refreshes the ID token using the provided refresh token.

    :param refresh_token: The refresh token used to refresh the ID token.
    :return: A dictionary containing the response from the server.
    """
    url = f'https://securetoken.googleapis.com/v1/token?key={FIREBASE_API_KEY}'
    data = json.dumps({'grant_type': 'refresh_token', 'refresh_token': refresh_token})

    response = google_api_post(url, data)
    return response


def get_all_users() -> list[Any]:
    """
    Retrieve all users from Firebase authentication.

    :return: A list of dictionaries containing user information.
    :rtype: list[Any]
    """
    return [{'user_id': user.uid, 'email': user.email} for user in auth.list_users().iterate_all()]


def get_logged_in_user() -> UserRecord:
    """
    Get the currently logged in user.

    :return: The UserRecord object representing the currently logged in user.
    :rtype: UserRecord
    """
    decoded_id_token = get_decoded_id_token()
    uid = decoded_id_token.get('uid')

    user = auth.get_user(uid)
    return user


def get_decoded_id_token() -> dict:
    """
    Verify and decode the ID token from the x-api-key header.

    :return: A dictionary containing the decoded token.
    """
    id_token = flask.request.headers.get('x-api-key')
    if not id_token:
        return flask.abort(HTTPStatus.UNAUTHORIZED, 'No access')

    try:
        decoded_token = auth.verify_id_token(id_token.split()[1], check_revoked=True)
    except Exception as exception:
        return flask.abort(HTTPStatus.INTERNAL_SERVER_ERROR, f'Failed to verify ID token: {exception}')

    return decoded_token
