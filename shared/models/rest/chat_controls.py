from flask_restx import Namespace, fields

from shared.models.dto.chat_dto import ChatDTO
from shared.models.dto.chatbot_dto import ChatbotDTO

_namespace = Namespace('chats', description='Chat operations')


class ChatControls:
    namespace = _namespace

    class Models:
        chat_response = _namespace.model('ChatResponse', {
            ChatDTO.id_name(): fields.String(readonly=True, description='The identifier of the chat'),
            'respondent_id': fields.String(readonly=True, description='The identifier of the chatbot in the chat'),
        })

        chat_message_response = _namespace.model('ChatMessageResponse', {
            'sender': fields.String(readonly=True, description='A description of the chat message sender'),
            'message': fields.String(readonly=True, description='The text of a chat message')
        })

        chat_message_start_response = _namespace.model('ChatMessageStartResponse', {
            ChatDTO.id_name(): fields.String(readonly=True, description='The identifier of the started chat'),
            'sender': fields.String(readonly=True, description='A description of the chat message sender'),
            'message': fields.String(readonly=True, description='The initial response message text')
        })

        chat_start_post_request = _namespace.model('ChatStartPostRequest', {
            ChatbotDTO.id_name(): fields.String(required=True, description='The identifier of the chatbot to start a chat with'),
            'message': fields.String(required=True, description='The initial chat message text from the user')
        })

        chat_continue_post_request = _namespace.model('ChatContinuePostRequest', {
            'message': fields.String(required=True, description='The chat message text from the user')
        })
