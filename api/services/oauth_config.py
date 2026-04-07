import os
from urllib.parse import urlparse

AUTHORIZE_URL = "https://auth.atlassian.com/authorize"
TOKEN_URL = "https://auth.atlassian.com/oauth/token"
RESOURCES_URL = "https://api.atlassian.com/oauth/token/accessible-resources"

SCOPES = "read:me read:page:confluence read:content-details:confluence read:user:confluence offline_access"
JWT_ALGORITHM = "HS256"
REQUEST_TIMEOUT = 10

_REQUIRED_ENV_VARS = [
    "ATLASSIAN_CLIENT_ID",
    "ATLASSIAN_CLIENT_SECRET",
    "STATE_SECRET",
]


def get_oauth_config():
    env = {k: os.environ.get(k) for k in _REQUIRED_ENV_VARS}
    missing = [k for k, v in env.items() if not v]

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    # Comma-separated list of allowed redirect origins (optional)
    allowed_origins = os.environ.get("ALLOWED_REDIRECT_ORIGINS", "")

    return {
        "client_id": env["ATLASSIAN_CLIENT_ID"],
        "client_secret": env["ATLASSIAN_CLIENT_SECRET"],
        "state_secret": env["STATE_SECRET"],
        "allowed_origins": [o.strip() for o in allowed_origins.split(",") if o.strip()],
    }


def _build_base_url(headers):
    host = headers.get("Host", "localhost:3000")
    protocol = headers.get("X-Forwarded-Proto", "http")
    return f"{protocol}://{host}"


def get_default_redirect_uri(headers):
    return f"{_build_base_url(headers)}/api/auth/success"


def build_callback_url(headers):
    return f"{_build_base_url(headers)}/api/auth/callback"


def is_allowed_redirect(redirect_uri, config):
    parsed = urlparse(redirect_uri)
    redirect_origin = f"{parsed.scheme}://{parsed.netloc}"
    return redirect_origin in config["allowed_origins"]


def format_token_response(token_data):
    return {
        "access_token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token", ""),
        "expires_in": token_data.get("expires_in", 3600),
        "token_type": token_data.get("token_type", "Bearer"),
    }
