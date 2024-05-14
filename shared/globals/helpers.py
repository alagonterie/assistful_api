from shared.globals import constants


# noinspection HttpUrlsUsage
def get_debug_uri() -> str:
    return f'http://{constants.DEBUG_HOST}:{constants.DEBUG_PORT}/{constants.BASE_PATH}'


def get_debug_docs_uri() -> str:
    return f'{get_debug_uri()}/{constants.DOCS_URL}'
