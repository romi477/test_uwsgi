# uwsgi --wsgi-file test_app.py --http :9000

import http.client


def application(environ, start_response):
    print(environ)
    url = environ['PATH_INFO']
    if url == '/info/':
        status_code, extra_headers, response_content = info_page_handler(environ)
    else:
        status_code = 404
        extra_headers = {}
        response_content = b'404'
    headers = {
        'Content-Type': 'text/plain',
   }
    headers.update(extra_headers)

    start_response(
        '%s %s' % (status_code, http.client.responses[status_code]),
        list(headers.items()),
    )
    return [response_content]


def info_page_handler(environ):
    response_content = b'Hello from simple WSGI app3'
    return 201, {}, response_content