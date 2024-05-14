from flask_restx import Namespace, fields

from shared.models.dto.chatbot_dto import ChatbotDTO

_namespace = Namespace('chatbots', description='Chatbot operations')


class ChatbotControls:
    namespace = _namespace

    class Models:
        chatbot_post_request = _namespace.model('ChatbotPostRequest', {
            'context': fields.String(required=True, description='The context for the new chatbot. Can determine the self-identity of the chatbot.'),
            'temperament': fields.String(description='Determines the level of variety in chatbot messages. Options are TAME, FUN, LOOSE, and WILD. The default value is FUN.')
        })

        chatbot_id_response = _namespace.model('ChatbotIdResponse', {
            ChatbotDTO.id_name(): fields.String(readonly=True, description='The chatbot identifier')
        })

        chatbot_response = _namespace.model('ChatbotResponse', {
            ChatbotDTO.id_name(): fields.String(readonly=True, description='The chatbot identifier'),
            'temperament': fields.String(readonly=True, description='Determines the level of variety in chatbot messages.')
        })
