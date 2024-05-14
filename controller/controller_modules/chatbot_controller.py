from http import HTTPStatus

from flask_restx import Resource

from controller.controller_helpers import make_response, create_user_context, from_body, validate_enum
from controller.request_validation.auth_validation import signed_in
from repository.repo_modules import chatbot_repo
from shared.globals.constants import INSUFFICIENT_ACCESS, API_KEY
from shared.globals.enums import AccessLevels, ChatbotTemperaments
from shared.models.dto.chatbot_dto import ChatbotDTO
from shared.models.rest.chatbot_controls import ChatbotControls

chatbot_ns = ChatbotControls.namespace


@chatbot_ns.route('')
@chatbot_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
class ChatbotList(Resource):

    @chatbot_ns.doc('get_chatbot_list', security=API_KEY)
    @chatbot_ns.marshal_list_with(ChatbotControls.Models.chatbot_response)
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def get(self):
        """
        Get the list of all user created chatbots
        """
        ctx = create_user_context()

        chatbot_list = chatbot_repo.get_all(ctx)
        return make_response(chatbot_list)

    @chatbot_ns.doc('create_chatbot', security=API_KEY)
    @chatbot_ns.expect(ChatbotControls.Models.chatbot_post_request, validate=True)
    @chatbot_ns.marshal_with(ChatbotControls.Models.chatbot_id_response)
    @chatbot_ns.response(HTTPStatus.CREATED, 'Chatbot created')
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def post(self):
        """
        Creates a new chatbot with the given context
        """
        ctx = create_user_context()

        chatbot_context, temperament_str = from_body(('context', 'temperament'))
        temperament = validate_enum('temperament', temperament_str, ChatbotTemperaments)

        chatbot_id = chatbot_repo.insert(ctx, chatbot_context, temperament)
        return make_response(ChatbotDTO(chatbot_id=chatbot_id), HTTPStatus.CREATED)
