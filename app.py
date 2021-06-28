import socket
import constants
from utils import setup_logger, parse_http, parse_api_route, process_response, to_environ, start_response
from src import weather

maps = {"weather": (weather,
                    {
                        "send_collected_data_to_display": weather.send_collected_data_to_display
                    }
                    )
        }


class Babloo:

    def __init__(self, host, port, connections=1):
        self.server_logger = setup_logger("server")
        self.host = host
        self.port = port
        self.connections = connections
        pass

    def create_webserver(self):
        """
        A simple Web Server
        """
        # receiving HTTP
        with socket.socket() as s:
            self.server_logger.info('binding host to socket')
            s.bind((self.host, self.port))
            #  self.connections here means that {self.connections} these many connection(s) are kept waiting
            #  if the server is busy and if a {self.connections + ..} socket tries to connect then the connection is refused.
            s.listen(self.connections)
            conn, addr = s.accept()

            def view(req):
                # process request and return response accordingly
                self.server_logger.info(f"req received {req}")
                return "hello world"

            while True:
                with conn:
                    http_request = conn.recv(1024).decode('utf-8')
                    request = parse_http(http_request)
                    response = view(request)
                    http_response = process_response(response)
                    conn.sendall(http_response.encode('utf-8'))
                    conn.close()

    def create_wsgi_compatible_web_server(self):
        """
        Making it WSGI compatible
        """
        try:
            self.server_logger.info("Initialising Engine")
            with socket.socket() as s:
                s.bind((self.host, self.port))
                s.listen(1)
                self.server_logger.info(f"Engine Started at {self.host}:{self.port}")
                conn, addr = s.accept()

                while True:
                    with conn:
                        http_request = conn.recv(1024).decode('utf-8')
                        request = parse_http(http_request)
                        environ = to_environ(*request)
                        response = self.application(start_response, environ, conn)
                        self.server_logger.info(f"response: {response}")
                        for data in response:
                            conn.sendall(data.encode('utf-8'))
                            # conn.sendall(json.dumps(response).encode('utf-8'))

                    conn.close()
                    s.close()
                    s.detach()
                    self.server_logger.info('Shutting down Engine')
                    return
        except Exception as exx:
            self.server_logger.exception(f"exception- {exx}")
            return

    def application(self, start_resp, environ, conn):
        """

        :param start_resp: a starting response for the request
        :param environ: environment variable or variables for the request
        :param conn: connection object
        :return:
        """
        # from this callable object you can route your requests to the rest of your python application
        # and return the response accordingly
        response = self.view(environ)
        start_resp(status="200 ok", headers=[('Content-Length', len(response))], conn=conn)
        # return {"data": response}
        return [response]

    def view(self, environ):
        path = environ["PATH_INFO"]
        routing_details = parse_api_route(path, api_url=constants.API_URL_PREFIX, logger=self.server_logger)
        response = self.router(routing_details)
        return str(response)

    def router(self, routing_details):
        return maps[routing_details["file"]][1][routing_details["method"]]()


server_obj = Babloo(host='localhost', port=8080)
server_obj.create_wsgi_compatible_web_server()
