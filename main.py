import os

import flask
from flask import Blueprint
from flask_restx import Api

from controller.controller_modules.assistant_controller import assistant_ns
from controller.controller_modules.auth_controller import auth_ns
from controller.controller_modules.chat_controller import chat_ns
from controller.controller_modules.chatbot_controller import chatbot_ns
from controller.controller_modules.example_controller import example_ns
from controller.controller_modules.org_controller import org_ns
from controller.controller_modules.scrap_controller import scrap_ns
from controller.request_filters.testing_filters import init_testing_filters
from shared.globals import constants
from shared.globals.constants import API_KEY
from shared.utilities import is_testing_environment

app = flask.Flask(__name__)
blueprint = Blueprint(constants.BASE_PATH, __name__, url_prefix=f'/{constants.BASE_PATH}')

authorizations = {
    API_KEY: {
        'description': f'JWT {constants.AUTH_HEADER_NAME} header using the Bearer scheme. '
                       'Enter "Bearer" [space] and then your token in the text input below. '
                       'Example: "Bearer 12345abcdef"',
        'type': 'apiKey',
        'in': 'header',
        'name': constants.AUTH_HEADER_NAME
    }
}

api = Api(
    blueprint,
    version='1.0',
    title=f'{constants.APP_NAME} API',
    description=f'{constants.APP_NAME} ReST Services',
    authorizations=authorizations,
    doc='/docs/'
)

api.add_namespace(assistant_ns)
api.add_namespace(auth_ns)
api.add_namespace(chat_ns)
api.add_namespace(chatbot_ns)
api.add_namespace(example_ns)
api.add_namespace(org_ns)
api.add_namespace(scrap_ns)

app.register_blueprint(blueprint)

is_testing = is_testing_environment()
if is_testing:
    os.environ['FIRESTORE_EMULATOR_HOST'] = '[::1]:8587'

init_testing_filters(app, is_testing)

if __name__ == '__main__':
    app.run(host=constants.DEBUG_HOST, port=constants.DEBUG_PORT, debug=True)
