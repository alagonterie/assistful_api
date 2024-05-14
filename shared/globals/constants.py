APP_NAME: str = 'Assistful'

GCP_DEFAULT_LOCATION: str = 'us-central1'
GCP_DEFAULT_TEXT_MODEL: str = 'text-bison@001'

PROD_HOST: str = 'assistful.dev'
DEBUG_HOST: str = '127.0.0.1'
DEBUG_PORT: int = 8080

BASE_PATH: str = 'api'
DOCS_URL: str = 'swagger.json'

# TODO: Need to use Google Secret Manager in GCP to store creds like this.
OWNER_EMAIL: str = ''
DEBUG_OWNER_EMAIL: str = ''

DEFAULT_HEADERS: dict[str, str] = {'content-type': 'application/json; charset=UTF-8'}

API_KEY: str = 'apikey'
AUTH_HEADER_NAME: str = 'x-api-key'
INSUFFICIENT_ACCESS: str = 'Insufficient access'

TYPE_NAME_ORG: str = 'Organization'

FIELD_ORG_ID: str = 'org_id'

FIELD_INSERT_USER: str = 'insert_user'
FIELD_UPDATE_USER: str = 'update_user'

FIELD_EMPTY_SELECT: str = 'non_existing_field'

MAX_OUTPUT_TOKENS: int = 256

# TODO: Need to use Google Secret Manager in GCP to store creds like this.
PROJECT_ID: str = ''
FIREBASE_API_KEY: str = ''

OWNER_ID: str = ''
DEBUG_OWNER_ID: str = ''
