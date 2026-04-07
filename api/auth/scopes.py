from http.server import BaseHTTPRequestHandler
import json

from api.services.oauth_config import SCOPES


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "scopes": SCOPES.split(),
        }).encode())
