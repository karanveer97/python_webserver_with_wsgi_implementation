import logging
from io import StringIO


# Parsing HTTP
# Splitting up a bunch of text
def parse_http(http):
    """
    :param http: (sample input)
                 GET / HTTP/1.1
                 Host: localhost:8080
                 User-Agent: curl/7.64.0
                 Accept: */*
    :return: method, path, protocol, headers, body
    """
    request, *headers, _, body = http.split('\r\n')
    method, path, protocol = request.split(" ")
    headers = dict(
              line.split(':', maxsplit=1)
              for line in headers
              )
    return method, path, protocol, headers, body


# Responding with HTTP
# Something a browser can understand
def process_response(response):
    """
    HTTP/1.1 200 ok
    Content-Type: text/html
    Content-Length: 11

    Hello world

    ^ protocol: HTTP/1.1
      status code: 200 ok
      headers: Content-Type: text/html
               Content-Length: 11
      body: Hello world
    """
    return (
            'HTTP/1.1 200 OK\r\n'
            f'Content-Length: {len(response)}\r\n'
            'Content-Type: text/html\r\n'
            '\r\n' +
            str(response) +
            '\r\n'
    )


def to_environ(method, path, protocol, headers, body):
    return {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'SERVER_PROTOCOL': protocol,
        'wsgi.input': StringIO(body),
        'headers': format_headers(headers),
    }


def start_response(status, headers, conn):
    conn.sendall(f'HTTP/1.1 {status}\r\n'.encode('utf-8'))
    for (key, value) in headers:
        conn.sendall(f'{key}: {value}\r\n'.encode('utf-8'))
    conn.sendall('\r\n'.encode('utf-8'))


def parse_api_route(path, api_url, logger=None):
    if logger:
        logger.info(f"api call: {path}")
    else:
        print(f"api call: {path}")
    raw = path.split(api_url)[1]
    route = raw.split("/")
    file = route[0]
    method = route[1].split("?")[0]
    args = route[1].split("?")[1].split("&")
    details_dict = {"file": file, "method": method, "args": {k.split("=")[0]: k.split("=")[1] for k in args}}
    return details_dict


def format_headers(headers):
    # code the required formatting here and utilise it as required.
    return headers


def setup_logger(logger_name):
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    return logger






