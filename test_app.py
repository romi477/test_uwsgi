# uwsgi --wsgi-file test_app.py --http :9000
import http.client
import json
import re


class App:
    def __init__(self):
        self.handlers = {}

    def __call__(self, environ, start_response):
        # print(environ)
        url = environ['PATH_INFO']
        method = environ['REQUEST_METHOD']

        handler, url_args = self.get_handler(url, method)

        status_code, extra_headers, response_content = handler(environ, url_args)
        content_type = 'text/plain'
        if not type(response_content) is str:
            response_content = json.dumps(response_content)
            content_type = 'text/json'
        headers = {'Content-Type': content_type}
        headers.update(extra_headers)
        start_response(
            f'{status_code} {http.client.responses[status_code]}',
            list(headers.items()),
        )
        return [response_content.encode('utf8')]

    def get_handler(self, url, method):
        handler = None
        url_args = None
        if not url.endswith('/'):
            handler = App.no_trailing_slash_handler
        else:
            for url_regexp, (current_methods, current_handler) in self.handlers.items():
                match = re.match(url_regexp, url)
                if match is None:
                    continue
                url_args = match.groupdict()
                handler = current_handler
                break
            if handler is None:
                handler = App.not_found_handler
        return handler, url_args

    def add_handler(self, url, methods=None):
        methods = methods or ['GET']
        def wrapper(handler):
            self.handlers[url] = methods, handler
        return wrapper

    @staticmethod
    def not_found_handler(environ, url_args):
        response_content = 'Not found'
        return 404, {}, response_content

    @staticmethod
    def not_allowed_handler(environ, url_args):
        response_content = 'Not allowed'
        return 405, {}, response_content

    @staticmethod
    def no_trailing_slash_handler(environ, url_args):
        return (
            301,
            {'Location': f'{environ["PATH_INFO"]}/'},
            'Redirect to url with trailing slash'
        )


application = App()

@application.add_handler(r'^/$', methods=['GET', 'POST'])
def index_page_handler(environ, url_args):
    return 200, {}, 'Index'

@application.add_handler(r'^/info/$')
def info_page_handler(environ, url_args):
    return 200, {}, {'user_ip': environ['REMOTE_ADDR']}

@application.add_handler(r'^/lessons/(?P<lesson_id>\d+)/$')
def info_page_handler(environ, url_args):
    return 200, {}, {'lesson_id': url_args['lesson_id']}

