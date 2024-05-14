from http import HTTPStatus

from flask_restx import Resource

from controller.controller_helpers import make_response, from_body
from controller.request_validation.auth_validation import signed_in
from provider.provider_modules import org_provider, auth_provider
from shared.globals.constants import INSUFFICIENT_ACCESS, API_KEY
from shared.globals.enums import AccessLevels
from shared.models.rest.auth_controls import AuthControls

auth_ns = AuthControls.namespace


@auth_ns.route('/users')
@auth_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
class AuthUsers(Resource):
    @auth_ns.doc('list_users', security=API_KEY)
    @signed_in(required_access_level=AccessLevels.OWNER)
    def get(self):
        """Lists all API users"""

        user_data = auth_provider.get_all_users()
        return make_response(user_data)


@auth_ns.route('/sign-up')
@auth_ns.response(HTTPStatus.BAD_REQUEST, 'Invalid email or password')
class AuthSignUp(Resource):
    @auth_ns.doc('sign_up')
    @auth_ns.expect(AuthControls.Models.sign_up_request, validate=True)
    @auth_ns.marshal_with(AuthControls.Models.sign_up_response)
    @auth_ns.response(HTTPStatus.CREATED, 'Organization and user account created')
    def post(self):
        """Create a new organization and the founding admin user account"""

        # TODO: get these from sign_up_request model?
        org_name, email, password = from_body(('org_name', 'email', 'password'))
        user = org_provider.create_org_and_admin_owner_user(org_name, email, password)

        return make_response(user, HTTPStatus.CREATED)


# TODO: /sign-in/admin
# TODO: /sign-in/service
@auth_ns.route('/sign-in')
@auth_ns.response(HTTPStatus.BAD_REQUEST, 'Invalid email or password')
class AuthSignIn(Resource):
    @auth_ns.doc('sign_in')
    @auth_ns.expect(AuthControls.Models.sign_in_request, validate=True)
    @auth_ns.marshal_with(AuthControls.Models.auth_response)
    def post(self):
        """Sign in an existing API user"""

        email, password = from_body(('email', 'password'))
        json_response = auth_provider.sign_in_with_email_and_password(email, password)
        return make_response({
            'user_id': json_response['localId'],
            'id_token': json_response['idToken'],
            'refresh_token': json_response['refreshToken'],
            'expire_seconds': int(json_response['expiresIn'])
        })


@auth_ns.route('/refresh')
@auth_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
@auth_ns.response(HTTPStatus.BAD_REQUEST, 'Invalid refresh token')
class AuthRefresh(Resource):
    @auth_ns.doc('refresh', security=API_KEY)
    @auth_ns.expect(AuthControls.Models.refresh_request, validate=True)
    @auth_ns.marshal_with(AuthControls.Models.auth_response)
    @signed_in()
    def post(self):
        """Refresh authentication for the signed in API user"""

        refresh_token = from_body('refresh_token')
        json_response = auth_provider.refresh_id_token(refresh_token)
        return make_response({
            'user_id': json_response['user_id'],
            'id_token': json_response['id_token'],
            'refresh_token': json_response['refresh_token'],
            'expire_seconds': int(json_response['expires_in'])
        })


@auth_ns.route('/profile')
@auth_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
class AuthProfile(Resource):
    @auth_ns.doc('profile', security=API_KEY)
    @signed_in()
    def post(self):
        """Fetch auth and account details for the signed in API user"""

        decoded_id_token = auth_provider.get_decoded_id_token()
        return make_response(decoded_id_token)
