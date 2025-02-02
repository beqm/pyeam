import json
import socket
import logging
import threading
from pyeam.tools import stdout
from http.server import HTTPServer
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler
from pyeam.core.ipc.exceptions import PyeamIPCPortInUse

def command(func):
    IPC._route(func.__name__, command=func, method="GET")
    return func

class HTTPClient(BaseHTTPRequestHandler):
    logger = logging.getLogger("pyeam")

    def do_GET(self):
        self._handle_request('GET')

    def do_POST(self):
        self._handle_request('POST')

    def log_message(self, format, *args):
        url_parts = args[0].split(' ')
        method = url_parts[0]
        url = url_parts[1]

        status = args[1]

        message = f"[{method}] - {status} - {url}"
        self.logger.info(message)
        return

    def _handle_request(self, method):
        from pyeam.core.builder import Builder

        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        args_list = [value for arg_list in query_params.values() for value in arg_list]


        if path in IPC.routes.keys():
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', Builder.config.build.dev_url)
                self.end_headers()

                # Execute invoke command
                response_data = IPC.routes[path]['command'](*args_list)

                response_json = json.dumps(response_data)
                self.wfile.write(response_json.encode())

            except Exception as err:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'500 Internal error')

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')


class IPC:
    routes = {}
    logger = logging.getLogger("pyeam")

    @classmethod
    def _is_port_in_use(cls, host: str, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result == 0

    @classmethod
    def _run(cls, address: str="localhost", port=7330):
        
        if cls._is_port_in_use(address, port):
            stdout.error(f"Port {port} is already in use!")
            raise PyeamIPCPortInUse(f"Port {port} is already in use!")
       
        server = HTTPServer((address, port), HTTPClient)

        http_client_thread = threading.Thread(target=server.serve_forever, daemon=True)
        cls.logger.info(f"IPC running on {address}:{port}")
        return http_client_thread

    @classmethod
    def _route(cls, path: str, command: callable, method: str="GET"):
        cls.routes[f"/api/invoke/{path}"] = {'route': f"/api/invoke/{path}", 'method': method, 'command': command}