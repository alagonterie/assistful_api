from http import HTTPStatus

from flask_restx import Resource

from controller.controller_helpers import make_response, create_user_context, from_body
from controller.request_validation.auth_validation import signed_in
from controller.request_validation.field_validation import is_valid_uri
from provider.provider_modules import assistant_provider
from repository.repo_modules import assistant_repo
from shared.globals.constants import INSUFFICIENT_ACCESS, API_KEY
from shared.globals.enums import AccessLevels
from shared.models.dto.assistant_dto import AssistantDTO
from shared.models.rest.assistant_controls import AssistantControls

assistant_ns = AssistantControls.namespace


@assistant_ns.route('')
@assistant_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
class AssistantList(Resource):

    @assistant_ns.doc('get_assistant_list', security=API_KEY)
    @assistant_ns.marshal_list_with(AssistantControls.Models.assistant_id_response)
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def get(self):
        """
        Get the list of all user created assistants
        """
        ctx = create_user_context()

        assistant_list = assistant_repo.get_all(ctx)
        return make_response(assistant_list)

    @assistant_ns.doc('create_assistant', security=API_KEY)
    @assistant_ns.expect(AssistantControls.Models.assistant_post_request, validate=True)
    @assistant_ns.marshal_with(AssistantControls.Models.assistant_id_response)
    @assistant_ns.response(HTTPStatus.CREATED, 'Assistant created')
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def post(self):
        """
        Creates a new assistant with the given context
        """
        ctx = create_user_context()

        assistant_context = from_body('context')

        assistant_id = assistant_repo.insert(ctx, assistant_context)
        return make_response(AssistantDTO(assistant_id=assistant_id), HTTPStatus.CREATED)


@assistant_ns.route('/<string:assistant_id>/configure/url')
@assistant_ns.response(HTTPStatus.NOT_FOUND, 'Assistant not found')
@assistant_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
@assistant_ns.param(AssistantDTO.id_name(), 'The assistant identifier')
class AssistantConfigureURL(Resource):

    @assistant_ns.doc('config_assistant_url', security=API_KEY)
    @assistant_ns.expect(AssistantControls.Models.assistant_config_url_put_request, validate=True)
    @assistant_ns.response(HTTPStatus.OK, 'Assistant configured')
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def put(self, assistant_id: str):
        """
        Configures an assistant to have functionality based on the given URL which points to an OpenAPI specification.
        """
        ctx = create_user_context()

        from flask_restx import reqparse
        parser = reqparse.RequestParser()
        parser.add_argument('docs_uri', type=is_valid_uri, required=True)
        spec_uri = parser.parse_args().get('docs_uri')
        api_base_uri = from_body('api_base_uri')

        assistant_provider.configure_from_uri(ctx, assistant_id, spec_uri, api_base_uri)
        return make_response()


@assistant_ns.route('/<string:assistant_id>/configure/spec')
@assistant_ns.response(HTTPStatus.NOT_FOUND, 'Assistant not found')
@assistant_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
@assistant_ns.param(AssistantDTO.id_name(), 'The assistant identifier')
class AssistantConfigureSpec(Resource):

    @assistant_ns.doc('config_assistant_spec', security=API_KEY)
    # @assistant_ns.expect(AssistantControls.Models.assistant_config_spec_put_request, validate=True)
    @assistant_ns.response(HTTPStatus.OK, 'Assistant configured')
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def put(self, assistant_id: str):
        """
        Configures an assistant to have functionality based on the given OpenAPI specification.
        """
        ctx = create_user_context()

        from flask import request
        spec_json = request.get_json()

        assistant_provider.configure_from_spec(ctx, assistant_id, spec_json)
        return make_response()
