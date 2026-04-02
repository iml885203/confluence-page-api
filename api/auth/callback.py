from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlencode, urlparse, quote
import json

import jwt
import requests

from api.services.oauth_config import (
    JWT_ALGORITHM,
    REQUEST_TIMEOUT,
    TOKEN_URL,
    build_callback_url,
    format_token_response,
    get_default_redirect_uri,
    get_oauth_config,
    is_allowed_redirect,
)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            config = get_oauth_config()
        except ValueError:
            self._send_error(500, "OAuth is not configured")
            return

        parsed = urlparse(self.path)
        query_params = parse_qs(parsed.query)

        default_redirect = get_default_redirect_uri(self.headers)

        error = query_params.get("error", [None])[0]
        if error:
            error_desc = query_params.get("error_description", [error])[0]
            error_redirect = f"{default_redirect}#error={quote(error_desc)}"
            self.send_response(302)
            self.send_header("Location", error_redirect)
            self.end_headers()
            return

        code = query_params.get("code", [None])[0]
        state = query_params.get("state", [None])[0]

        if not code or not state:
            self._send_error(400, "Missing code or state parameter")
            return

        try:
            state_payload = jwt.decode(
                state, config["state_secret"], algorithms=[JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            self._send_error(400, "State token expired, please try again")
            return
        except jwt.InvalidTokenError:
            self._send_error(400, "Invalid state token")
            return

        redirect_uri = state_payload.get("redirect_uri", default_redirect)

        # Validate redirect_uri unless it's our own default success page
        if redirect_uri != default_redirect and not is_allowed_redirect(redirect_uri, config):
            self._send_error(400, "Invalid redirect_uri in state")
            return

        try:
            token_response = requests.post(
                TOKEN_URL,
                json={
                    "grant_type": "authorization_code",
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "code": code,
                    "redirect_uri": build_callback_url(self.headers),
                },
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException:
            self._send_error(502, "Failed to connect to authentication server")
            return

        if token_response.status_code != 200:
            try:
                print(f"Token exchange error: {token_response.json()}")
            except ValueError:
                print(f"Token exchange error: {token_response.text}")
            self._send_error(502, "Token exchange failed")
            return

        fragment_params = urlencode(format_token_response(token_response.json()))
        spa_redirect = f"{redirect_uri}#{fragment_params}"

        self.send_response(302)
        self.send_header("Location", spa_redirect)
        self.end_headers()

    def _send_error(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
