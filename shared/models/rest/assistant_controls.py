from flask_restx import Namespace, fields

from shared.models.dto.assistant_dto import AssistantDTO

_namespace = Namespace('assistants', description='Assistant operations')


class AssistantControls:
    namespace = _namespace

    class Models:
        assistant_post_request = _namespace.model('AssistantPostRequest', {
            'context': fields.String(required=True, description='The context for the new assistant. Can determine the self-identity of the assistant.')
        })

        assistant_config_url_put_request = _namespace.model('AssistantConfigUrlPutRequest', {
            'docs_uri': fields.String(required=True, description='The full URI pointing to the Swagger or OpenAPI specification JSON.'),
            'api_base_uri': fields.String(description='The full base URI for all of the API endpoints.')
        })

        assistant_id_response = _namespace.model('AssistantIdResponse', {
            AssistantDTO.id_name(): fields.String(readonly=True, description='The assistant identifier')
        })
