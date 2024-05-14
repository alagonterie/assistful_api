from firebase_admin.firestore import firestore as fs
from marshmallow import Schema, fields, post_load

from shared.globals.constants import FIELD_ORG_ID
from shared.models.base_dto import BaseDTOFactory, BaseDTO


class OrgDTO(BaseDTO):
    """Class representing an Organization.

    :param org_id: The ID of the organization.
    :type org_id: str
    :param org_name: The name of the organization.
    :type org_name: str
    """

    @staticmethod
    def id_name() -> str:
        return FIELD_ORG_ID

    def id_value(self) -> str:
        return self.org_id

    def __init__(self,
                 org_id: str = None,
                 org_name: str = None):
        self.org_id = org_id
        self.org_name = org_name


class OrgDTOFactory(BaseDTOFactory):
    """
    Creates OrgDTO objects from DocumentSnapshots.
    """

    @staticmethod
    def create_from_doc(doc_snapshot: fs.DocumentSnapshot) -> OrgDTO | None:
        return BaseDTOFactory.doc_to_object(OrgSchema(), doc_snapshot, OrgDTO.id_name())


class OrgSchema(Schema):
    """Schema for the Org model"""

    org_id = fields.Str()
    org_name = fields.Str()

    @post_load
    def make_org(self, data, **_kwargs):
        return OrgDTO(**data)
