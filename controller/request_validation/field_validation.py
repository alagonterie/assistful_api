from typing import Any
from urllib.parse import urlparse


def is_valid_uri(value: Any) -> Any:
    """
    Check if a URI is valid.

    :param value: The URI to be validated.
    :return: The valid URI.
    :raises ValueError: If the URI is not valid.
    """
    parsed = urlparse(value)
    if all([parsed.scheme.lower() in {'http', 'https'}, parsed.netloc]):
        return value
    else:
        raise ValueError('The URL is not valid')
