import json
import threading
from http.server import HTTPServer
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

class HTTPClient(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request('GET')

    def do_POST(self):
        self._handle_request('POST')


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
                print(err)
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

    @classmethod
    def _run(cls, address: str="localhost", port=7330):
        server = HTTPServer((address, port), HTTPClient)

        print("IPC running")
        http_client_thread = threading.Thread(target=server.serve_forever)
        return http_client_thread

    @classmethod
    def _route(cls, path: str, command: callable, method: str="GET"):
        cls.routes[f"/api/invoke/{path}"] = {'route': f"/api/invoke/{path}", 'method': method, 'command': command}