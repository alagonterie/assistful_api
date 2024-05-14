import flask
import requests

from shared.globals.constants import DEFAULT_HEADERS


def google_api_post(url: str, data: str) -> dict:
    """
    Perform a POST request to a Google API.

    :param url: The URL endpoint of the Google API.
    :param data: The data to be sent in the request body.
    :return: The response from the Google API, as a JSON object.
    """
    response: dict = requests.post(url, headers=DEFAULT_HEADERS, data=data).json()
    if 'error' in response:
        flask.abort(response['error']['code'], response['error']['message'])

    return response
