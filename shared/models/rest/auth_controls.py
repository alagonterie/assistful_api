from flask_restx import Namespace, fields

from shared.models.dto.org_dto import OrgDTO

_namespace = Namespace('auth', description='Auth operations')


class AuthControls:
    namespace = _namespace

    class Models:
        sign_up_request = _namespace.model('SignUpRequest', {
            'email': fields.String(required=True, description='The email for the new user account'),
            'password': fields.String(required=True, description='The account password for authentication'),
            'org_name': fields.String(required=True, description='The name of the new organization that will be created')
        })

        sign_in_request = _namespace.model('SignInRequest', {
            'email': fields.String(required=True, description='The email for the user account'),
            'password': fields.String(required=True, description='The account password for authentication')
        })

        refresh_request = _namespace.model('RefreshRequest', {
            'refresh_token': fields.String(required=True, description='The refresh token from signing in')
        })

        auth_response = _namespace.model('AuthResponse', {
            'user_id': fields.String(readonly=True, description='The unique identifier of the user'),
            'id_token': fields.String(readonly=True, description='The temporary token that grants access to the API'),
            'refresh_token': fields.String(readonly=True, description='The token used to refresh access with a new id_token'),
            'expire_seconds': fields.Integer(readonly=True, description='The seconds until the id_token is set to expire')
        })

        sign_up_response = _namespace.model('SignUpResponse', {
            'user_id': fields.String(readonly=True, description='The unique identifier of the new user'),
            OrgDTO.id_name(): fields.String(readonly=True, description='The unique identifier of the new organization')
        })
