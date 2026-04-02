from http.server import BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs, urlparse
import json
import secrets
import time

import jwt

from api.services.oauth_config import (
    AUTHORIZE_URL,
    JWT_ALGORITHM,
    SCOPES,
    build_callback_url,
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
        redirect_uri = query_params.get("redirect_uri", [None])[0]

        if redirect_uri:
            if not is_allowed_redirect(redirect_uri, config):
                self._send_error(400, "Invalid redirect_uri")
                return
        else:
            redirect_uri = default_redirect

        now = int(time.time())
        state = jwt.encode(
            {
                "redirect_uri": redirect_uri,
                "nonce": secrets.token_hex(16),
                "exp": now + 600,
                "iat": now,
            },
            config["state_secret"],
            algorithm=JWT_ALGORITHM,
        )

        authorize_params = urlencode({
            "audience": "api.atlassian.com",
            "client_id": config["client_id"],
            "scope": SCOPES,
            "redirect_uri": build_callback_url(self.headers),
            "state": state,
            "response_type": "code",
            "prompt": "consent",
        })

        self.send_response(302)
        self.send_header("Location", f"{AUTHORIZE_URL}?{authorize_params}")
        self.end_headers()

    def _send_error(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
