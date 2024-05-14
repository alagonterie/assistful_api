from http import HTTPStatus
from flask_restx import Resource

from controller.controller_helpers import make_response, from_body, create_user_context
from controller.request_validation.auth_validation import signed_in
from repository.repo_modules import example_repo
from shared.globals.constants import INSUFFICIENT_ACCESS, API_KEY
from shared.globals.enums import AccessLevels
from shared.models.dto.example_dto import ExampleDTO
from shared.models.rest.example_controls import ExampleControls

example_ns = ExampleControls.namespace


@example_ns.route('')
@example_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
class ExampleList(Resource):
    """Shows a list of all examples and lets you POST to add new examples"""

    @example_ns.doc('list_examples', security=API_KEY)
    @example_ns.marshal_list_with(ExampleControls.Models.example_response)
    @signed_in(required_access_level=AccessLevels.OWNER)
    def get(self):
        """List all examples"""
        ctx = create_user_context()

        examples = example_repo.get_all(ctx)
        return make_response(examples)

    @example_ns.doc('create_example', security=API_KEY)
    @example_ns.expect(ExampleControls.Models.example_post_request, validate=True)
    @example_ns.marshal_with(ExampleControls.Models.example_id_response)
    @example_ns.response(HTTPStatus.CREATED, 'Example created')
    @signed_in(required_access_level=AccessLevels.ADMIN_OWNER)
    def post(self):
        """Create a new example"""
        ctx = create_user_context()

        details = from_body('details')
        example_id = example_repo.insert(ctx, details)
        return make_response(ExampleDTO(example_id=example_id), HTTPStatus.CREATED)


@example_ns.route('/<string:example_id>')
@example_ns.response(HTTPStatus.NOT_FOUND, 'Example not found')
@example_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
@example_ns.param(ExampleDTO.id_name(), 'The example identifier')
class Example(Resource):
    """Show a single example item and lets you delete them"""

    @example_ns.doc('get_example', security=API_KEY)
    @example_ns.marshal_with(ExampleControls.Models.example_response)
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def get(self, example_id: str):
        """Fetch an example given its identifier"""
        ctx = create_user_context()

        example = example_repo.get(ctx, example_id)
        return make_response(example)

    @example_ns.doc('delete_example', security=API_KEY)
    @example_ns.response(HTTPStatus.NO_CONTENT, 'Example deleted')
    @signed_in(required_access_level=AccessLevels.ADMIN_OWNER)
    def delete(self, example_id: str):
        """Delete an example given its identifier"""
        ctx = create_user_context()

        example_repo.delete(ctx, example_id)
        return make_response(status=HTTPStatus.NO_CONTENT)

    @example_ns.doc('update_example', security=API_KEY)
    @example_ns.expect(ExampleControls.Models.example_put_request, validate=True)
    @example_ns.response(HTTPStatus.OK, 'Example updated')
    @signed_in(required_access_level=AccessLevels.ADMIN_OWNER)
    def put(self, example_id: str):
        """Update an example given its identifier"""
        ctx = create_user_context()

        details = from_body('details')
        example_repo.update_details(ctx, example_id, details)
        return make_response()
