from http import HTTPStatus

from flask_restx import Resource

from controller.controller_helpers import make_response, create_user_context, from_body, from_uri
from controller.request_validation.auth_validation import signed_in
from provider.provider_modules.ai import chat_provider
from shared.globals.constants import INSUFFICIENT_ACCESS, API_KEY
from shared.globals.enums import AccessLevels
from shared.models.dto.chat_dto import ChatDTO
from shared.models.dto.chatbot_dto import ChatbotDTO
from shared.models.rest.chat_controls import ChatControls

chat_ns = ChatControls.namespace


@chat_ns.route('')
@chat_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
class ChatList(Resource):

    @chat_ns.doc('get_chat_list', security=API_KEY)
    @chat_ns.param(ChatbotDTO.id_name(), 'The identifier of the chatbot in the chat', _in='query', required=False)
    @chat_ns.marshal_list_with(ChatControls.Models.chat_response)
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def get(self):
        """
        Gets a list of user chats. Optionally filtered by chatbot
        """
        ctx = create_user_context()

        chatbot_id = from_uri(ChatbotDTO.id_name())
        chat_list = chat_provider.get_chats(ctx, chatbot_id)
        return make_response(chat_list)


@chat_ns.route('/<string:chat_id>/messages')
@chat_ns.response(HTTPStatus.NOT_FOUND, 'Chat not found')
@chat_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
@chat_ns.param(ChatDTO.id_name(), 'The chat identifier')
class ChatMessageList(Resource):

    @chat_ns.doc('get_chat_message_list', security=API_KEY)
    @chat_ns.marshal_list_with(ChatControls.Models.chat_message_response)
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def get(self, chat_id: str):
        """
        Gets all of the messages in a chat
        """
        ctx = create_user_context()

        messages = chat_provider.get_chat_messages(ctx, chat_id)
        return make_response(messages)


@chat_ns.route('/start')
@chat_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
class ChatStart(Resource):

    @chat_ns.doc('start_chat', security=API_KEY)
    @chat_ns.expect(ChatControls.Models.chat_start_post_request, validate=True)
    @chat_ns.marshal_with(ChatControls.Models.chat_message_start_response)
    @chat_ns.response(HTTPStatus.CREATED, 'Chat started')
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def post(self):
        """
        Starts a new chat with a chatbot
        """
        ctx = create_user_context()

        chatbot_id, message = from_body(('chatbot_id', 'message'))
        started_chat = chat_provider.start_chat(ctx, chatbot_id, message)
        return make_response(started_chat, HTTPStatus.CREATED)


@chat_ns.route('/<string:chat_id>/continue')
@chat_ns.response(HTTPStatus.UNAUTHORIZED, INSUFFICIENT_ACCESS)
class ChatContinue(Resource):

    @chat_ns.doc('continue_chat', security=API_KEY)
    @chat_ns.expect(ChatControls.Models.chat_continue_post_request, validate=True)
    @chat_ns.marshal_with(ChatControls.Models.chat_message_response)
    @chat_ns.response(HTTPStatus.CREATED, 'Chat continued')
    @signed_in(required_access_level=AccessLevels.ADMIN)
    def post(self, chat_id: str):
        """
        Continues a started chat with a chatbot
        """
        ctx = create_user_context()

        message = from_body('message')
        continued_chat = chat_provider.continue_chat(ctx, chat_id, message)
        return make_response(continued_chat, HTTPStatus.CREATED)
