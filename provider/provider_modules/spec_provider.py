from typing import Optional


def spec_from_uri(spec_uri: str, base_uri: Optional[str] = None) -> dict:
    """
    Retrieve API specification from a URI.

    :param spec_uri: A string that represents the URI of the API specification.
    :param base_uri: (Optional) A string that represents the base URI of the API.
    :return: A dictionary that contains the API specification.
    """
    spec: dict = _get_spec_dict_from_url(spec_uri)

    return spec_from_dict(spec, base_uri)


def spec_from_dict(spec: dict, base_uri: Optional[str] = None) -> dict:
    """
    Convert a Swagger/OpenAPI specification from a dictionary to the OpenAPI format.

    :param spec: A dictionary containing the Swagger/OpenAPI specification.
    :param base_uri: Optional base URI for the specification. Defaults to None.
    :return: The converted OpenAPI specification as a dictionary.
    """
    _validate_spec_dict_and_base_uri(spec, base_uri)
    spec: dict = _convert_swagger_to_openapi(spec, base_uri)

    return spec


def _get_spec_dict_from_url(spec_uri: str) -> dict:
    """
    Attempts to retrieve a specification hosted at the given URI.

    :param spec_uri: The URL of the API specification.
    :return: A dictionary containing the API specification.
    """
    spec = {}
    try:
        import requests
        from requests import Response

        response: Response = requests.get(spec_uri)
        response.raise_for_status()

        spec: dict = response.json()
    except:
        import flask
        import http

        flask.abort(http.HTTPStatus.BAD_REQUEST, f'Failed to get API docs from the URI: {spec_uri}')

    return spec


def _validate_spec_dict_and_base_uri(spec: dict, base_uri: Optional[str] = None) -> None:
    """
    Validate the given spec dictionary as proper Swagger/OpenAPI. Also validates the optional base URI.

    :param spec: The OpenAPI specification dictionary.
    :type spec: dict
    :param base_uri: The base URI to validate against (optional).
    :type base_uri: str, optional
    """
    try:
        import openapi_spec_validator

        openapi_spec_validator.validate_spec(spec)
        if base_uri:
            _validate_base_uri(base_uri)

    except ValueError as value_error:
        import flask
        from http import HTTPStatus

        flask.abort(HTTPStatus.BAD_REQUEST, str(value_error))
    except:
        import flask
        from http import HTTPStatus

        flask.abort(HTTPStatus.BAD_REQUEST, f'Validation failed for the given API docs')


def _convert_swagger_to_openapi(spec: dict, base_uri: Optional[str] = None) -> dict:
    """
    Convert older Swagger definitions (1.X, 2.X) to OpenAPI 3.X specification using the Swagger Converter API.

    :param spec: A dictionary representing a Swagger specification.
    :param base_uri: An optional string representing the base URI to use for the converted OpenAPI specification.
    :return: A dictionary representing the converted OpenAPI specification.

    If the `spec` parameter contains a `'swagger'` key,
    the method sends a POST request to the Swagger Converter API with the Swagger specification as JSON.
    The response is expected to be a JSON-formatted OpenAPI specification.

    If the Swagger Converter API call is successful,
    the method checks if the converted specification contains a `'servers'` key and if the `'servers'` list is not empty.
    It also checks if the first server in the list has a `'url'` key. If any of these checks fail, an exception is raised.

    If the `base_uri` parameter is provided,
    it replaces the `'url'` value of the first server in the converted specification.
    If `base_uri` is not provided and there is an error during the conversion process,
    a `BadRequest` error is raised if the Flask framework is available, or a `ServiceUnavailable` error is raised otherwise.
    """
    if spec.get('swagger'):
        try:
            import requests
            from requests import Response

            response: Response = requests.post('https://converter.swagger.io/api/convert', json=spec)
            response.raise_for_status()

            spec: dict = response.json()

            if 'servers' not in spec or not any(spec['servers']) or not spec['servers'][0].get('url'):
                raise Exception()

            _validate_base_uri(spec['servers'][0]['url'])
        except ValueError as value_error:
            if not base_uri:
                import flask
                from http import HTTPStatus

                flask.abort(HTTPStatus.BAD_REQUEST, str(value_error))
            else:
                spec['servers'][0]['url'] = base_uri
        except:
            import flask
            from http import HTTPStatus

            flask.abort(HTTPStatus.SERVICE_UNAVAILABLE, f'Failed to convert Swagger to OpenAPI format')

    return spec


def _validate_base_uri(base_uri: str) -> None:
    """
    Validate the given base URI.

    :param base_uri: The base URI to be validated.
    :return: None
    :raises ValueError: If the validation fails for the given base URI.
    """
    from urllib.parse import urlparse

    result = urlparse(base_uri)
    if not all([result.scheme in ['http', 'https'], result.netloc]):
        raise ValueError(f'Validation failed for the given base URI: {base_uri}')
