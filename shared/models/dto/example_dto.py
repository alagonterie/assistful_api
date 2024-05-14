from firebase_admin.firestore import firestore as fs
from marshmallow import Schema, fields, post_load

from shared.models.base_dto import BaseDTOFactory, BaseDTO


class ExampleDTO(BaseDTO):
    """Class representing an Example.

    :param example_id: The ID of the example.
    :type example_id: str
    :param details: The details of the example.
    :type details: str
    """

    @staticmethod
    def id_name() -> str:
        return 'example_id'

    def id_value(self) -> str:
        return self.example_id

    def __init__(self,
                 example_id: str = None,
                 details: str = None):
        self.example_id = example_id
        self.details = details


class ExampleDTOFactory(BaseDTOFactory):
    """
    Creates ExampleDTO objects from DocumentSnapshots.
    """

    @staticmethod
    def create_from_doc(doc_snapshot: fs.DocumentSnapshot) -> ExampleDTO | None:
        return BaseDTOFactory.doc_to_object(ExampleSchema(), doc_snapshot, ExampleDTO.id_name())


class ExampleSchema(Schema):
    """Schema for the Example model"""

    example_id = fields.Str()
    details = fields.Str()

    @post_load
    def make_example(self, data, **_kwargs):
        return ExampleDTO(**data)
