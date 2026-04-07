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

        code = query_params.get("code", [None])[0]
        state = query_params.get("state", [None])[0]

        # Parse state to extract redirect_uri and response_mode
        redirect_uri = default_redirect
        response_mode = "fragment"
        state_valid = False
        if state:
            try:
                state_payload = jwt.decode(
                    state, config["state_secret"], algorithms=[JWT_ALGORITHM]
                )
                redirect_uri = state_payload.get("redirect_uri", default_redirect)
                response_mode = state_payload.get("response_mode", "fragment")
                if redirect_uri != default_redirect and not is_allowed_redirect(redirect_uri, config):
                    redirect_uri = default_redirect
                state_valid = True
            except jwt.ExpiredSignatureError:
                pass
            except jwt.InvalidTokenError:
                pass

        error = query_params.get("error", [None])[0]
        if error:
            error_desc = query_params.get("error_description", [error])[0]
            error_param = f"error={quote(error_desc)}"
            if response_mode == "query":
                separator = "&" if "?" in redirect_uri else "?"
                error_redirect = f"{redirect_uri}{separator}{error_param}"
            else:
                error_redirect = f"{redirect_uri}#{error_param}"
            self.send_response(302)
            self.send_header("Location", error_redirect)
            self.end_headers()
            return

        if not code or not state_valid:
            self._send_error(400, "Missing or invalid code/state parameter")
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

        token_params = urlencode(format_token_response(token_response.json()))

        if response_mode == "query":
            separator = "&" if "?" in redirect_uri else "?"
            spa_redirect = f"{redirect_uri}{separator}{token_params}"
        else:
            spa_redirect = f"{redirect_uri}#{token_params}"

        self.send_response(302)
        self.send_header("Location", spa_redirect)
        self.end_headers()

    def _send_error(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
