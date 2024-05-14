from flask_restx import Namespace, fields

_namespace = Namespace('scrap', description='Just scrapping')


class ScrapControls:
    namespace = _namespace

    class Models:
        scrap_response = _namespace.model('ScrapResponse', {
            'query_response': fields.String(readonly=True, description='The response from scrapping the query'),
        })

        scrap_post_request = _namespace.model('ScrapPostRequest', {
            'query': fields.String(required=True, description='The query to scrap with')
        })
