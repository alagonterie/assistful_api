from flask_restx import Namespace, fields

from shared.models.dto.org_dto import OrgDTO

_namespace = Namespace('organizations', description='Organization operations')


class OrgControls:
    namespace = _namespace

    class Models:
        org_response = _namespace.model('OrganizationResponse', {
            OrgDTO.id_name(): fields.String(readonly=True, description='The organization unique identifier'),
            'org_name': fields.String(readonly=True, description='The name of the organization')
        })
