from flask_restx import Namespace, fields

from shared.models.dto.example_dto import ExampleDTO

_namespace = Namespace('examples', description='Example operations')


class ExampleControls:
    namespace = _namespace

    class Models:
        example_post_request = _namespace.model('ExamplePostRequest', {
            'details': fields.String(required=True, description='The details for the new example')
        })

        example_put_request = _namespace.model('ExamplePutRequest', {
            'details': fields.String(required=True, description='The new example details')
        })

        example_id_response = _namespace.model('ExampleIdResponse', {
            ExampleDTO.id_name(): fields.String(readonly=True, description='The example unique identifier')
        })

        example_response = _namespace.model('ExampleResponse', {
            ExampleDTO.id_name(): fields.String(readonly=True, description='The example unique identifier'),
            'details': fields.String(readonly=True, description='The example details')
        })
