from http.server import BaseHTTPRequestHandler
import json

import requests

from api.services.oauth_config import (
    REQUEST_TIMEOUT,
    TOKEN_URL,
    format_token_response,
    get_oauth_config,
)

MAX_BODY_SIZE = 8192


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        try:
            config = get_oauth_config()
        except ValueError:
            self._send_error(500, "OAuth is not configured")
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            self._send_error(400, "Invalid Content-Length header")
            return

        if content_length == 0:
            self._send_error(400, "Request body is required")
            return

        if content_length > MAX_BODY_SIZE:
            self._send_error(413, "Request body too large")
            return

        try:
            body = json.loads(self.rfile.read(content_length))
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON in request body")
            return

        refresh_token = body.get("refresh_token")
        if not refresh_token:
            self._send_error(400, "refresh_token is required")
            return

        try:
            token_response = requests.post(
                TOKEN_URL,
                json={
                    "grant_type": "refresh_token",
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "refresh_token": refresh_token,
                },
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException:
            self._send_error(502, "Failed to connect to authentication server")
            return

        if token_response.status_code != 200:
            try:
                print(f"Token refresh error: {token_response.json()}")
            except ValueError:
                print(f"Token refresh error: {token_response.text}")
            self._send_error(502, "Token refresh failed")
            return

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(format_token_response(token_response.json())).encode())

    def _send_error(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
