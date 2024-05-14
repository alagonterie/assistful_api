from http import HTTPStatus

from flask_restx import Resource

from controller.controller_helpers import make_response, from_body
from controller.request_validation.auth_validation import signed_in
from provider.provider_modules.ai import scrap_provider
from shared.globals.constants import INSUFFICIENT_ACCESS, API_KEY
from shared.globals.enums import AccessLevels
from shared.models.rest.scrap_controls import ScrapControls

# This whole file is testing code. I like the word "scrap".

scrap_ns = ScrapControls.namespace


@scrap_ns.route('')
@scrap_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
class Scrap(Resource):

    @scrap_ns.doc('scrap', security=API_KEY)
    @scrap_ns.expect(ScrapControls.Models.scrap_post_request, validate=True)
    @scrap_ns.marshal_with(ScrapControls.Models.scrap_response)
    @scrap_ns.response(HTTPStatus.OK, 'Scrapping')
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def post(self):
        """
        Scrap with a test agent
        """

        query = from_body('query')
        query_response = scrap_provider.query_test_agent(query)
        return make_response({'query_response': query_response}, HTTPStatus.OK)


@scrap_ns.route('/vector-store')
@scrap_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
class ScrapVectorStoreClear(Resource):

    @scrap_ns.doc('clear_scrap_vector_store', security=API_KEY)
    @scrap_ns.response(HTTPStatus.NO_CONTENT, 'Vector store cleared')
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def delete(self):
        """
        Clear the in-memory vector store test database
        """

        scrap_provider.clear_vector_store()
        return make_response(status=HTTPStatus.NO_CONTENT)


@scrap_ns.route('/memory')
@scrap_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
class ScrapMemoryClear(Resource):

    @scrap_ns.doc('clear_scrap_memory', security=API_KEY)
    @scrap_ns.response(HTTPStatus.NO_CONTENT, 'Memory cleared')
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def delete(self):
        """
        Clear the chat memory of the test agent
        """

        scrap_provider.clear_memory()
        return make_response(status=HTTPStatus.NO_CONTENT)
