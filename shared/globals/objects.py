from shared.globals.constants import OWNER_ID
from shared.globals.enums import AccessLevels
from shared.models.security.user_context import UserContext

NO_USER_CONTEXT = UserContext()
OWNER_CONTEXT = UserContext(user_id=OWNER_ID, access_level=AccessLevels.OWNER)

# TODO: Need to use Google Secret Manager in GCP to store creds like this.
FIREBASE_CREDS: dict[str, str] = {
    'type': 'service_account',
    'project_id': '',
    'private_key_id': '',
    'private_key': '',
    'client_email': '',
    'client_id': '',
    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
    'token_uri': 'https://oauth2.googleapis.com/token',
    'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
    'client_x509_cert_url': '',
    'universe_domain': 'googleapis.com'
}
