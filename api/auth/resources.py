from http.server import BaseHTTPRequestHandler
import json

import requests

from api.services.oauth_config import REQUEST_TIMEOUT, RESOURCES_URL


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        auth_header = self.headers.get("Authorization")

        if not auth_header:
            self._send_error(401, "Authorization header is required")
            return

        try:
            response = requests.get(
                RESOURCES_URL,
                headers={"Authorization": auth_header, "Accept": "application/json"},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException:
            self._send_error(502, "Failed to connect to Atlassian API")
            return

        if response.status_code != 200:
            self._send_error(response.status_code, "Failed to fetch accessible resources")
            return

        try:
            resources = response.json()
        except ValueError:
            self._send_error(502, "Invalid response from Atlassian API")
            return

        result = [
            {
                "id": resource["id"],
                "name": resource["name"],
                "url": resource["url"],
                "scopes": resource.get("scopes", []),
                "avatarUrl": resource.get("avatarUrl", ""),
            }
            for resource in resources
        ]

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def _send_error(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
