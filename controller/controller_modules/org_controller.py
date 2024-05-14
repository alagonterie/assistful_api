from http import HTTPStatus

from flask_restx import Resource

from controller.controller_helpers import make_response, create_user_context
from controller.request_validation.auth_validation import signed_in
from provider.provider_modules import org_provider
from shared.globals.constants import INSUFFICIENT_ACCESS, API_KEY
from shared.globals.enums import AccessLevels
from shared.models.ai.agents import assistful_agent
from shared.models.rest.org_controls import OrgControls

org_ns = OrgControls.namespace


@org_ns.route('')
@org_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
class OrgList(Resource):
    """
    Retrieve information about the organization that the user belongs to.
    """

    @org_ns.doc('get_org', security=API_KEY)
    @org_ns.marshal_with(OrgControls.Models.org_response)
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def get(self):
        """Get information about the organization that the signed in user belongs to"""
        ctx = create_user_context()

        org = org_provider.get_org_info(ctx)
        return make_response(org)
