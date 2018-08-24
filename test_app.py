# uwsgi --wsgi-file test_app.py --http :9000

import http.client



class App:
    def __init__(self):
        self.handlers = {}


    def __call__(self, environ, start_response):
        print(environ)
        url = environ['PATH_INFO']
        method = environ['REQUEST_METHOD']
        if url in self.handlers:
            allowed_methods, handler = self.handlers[url]
            if method not in allowed_methods:
                handler = App.not_allowed_handler
        else:
            handler = App.not_found_handler

        status_code, extra_headers, response_content = handler(environ)
        headers = {
            'Content-Type': 'text/plain',
       }
        headers.update(extra_headers)

        start_response(
            f'{status_code} {http.client.responses[status_code]}',
            list(headers.items()),
        )
        return [response_content.encode('utf8')]

    def add_handler(self, url, methods=None):
        methods = methods or ['GET']
        def wrapper(handler):
            self.handlers[url] = methods, handler
        return wrapper

    @staticmethod
    def not_found_handler(environ):
        response_content = 'Not found'
        return 404, {}, response_content

    @staticmethod
    def not_allowed_handler(environ):
        response_content = 'Not allowed'
        return 405, {}, response_content


application = App()

@application.add_handler('/')
def index_page_handler(environ):
    response_content = 'Index'
    return 200, {}, response_content

@application.add_handler('/info/')
def info_page_handler(environ):
    response_content = 'Hello from simple WSGI app3'
    return 200, {}, response_content

