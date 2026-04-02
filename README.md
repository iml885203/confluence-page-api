# Confluence Page API

This project provides a serverless API for interacting with Confluence pages. Built with Python and deployed on Vercel, it offers endpoints to fetch and parse Confluence page content and version information.

## Features

- **Page Content API**: Fetches and parses Confluence page content into a structured format
- **Version API**: Retrieves version information for Confluence pages
- **OAuth 2.0 Authentication**: Atlassian OAuth 2.0 (3LO) flow for SPA integration
- **Base URL Configuration**: Configurable Confluence base URL through headers
- **Pass-through Authentication**: Forwards authentication headers to Confluence APIs

## API Endpoints

### Get Page Content
```
GET /api/pages/{pageId}
```
Headers:
- `X-Base-Url`: Your Confluence base URL (required)
- `Authorization`: Your authentication token (optional)

Response:
```json
[
  {
    "category": "string",
    "webs": [
      {
        "Icon": "string",
        "Title": "string",
        "Description": "string",
        "Tags": ["string"],
        "Link": "string",
        "SubLinks": [
          {
            "Title": "string",
            "Link": "string"
          }
        ],
        "Category": "string"
      }
    ]
  }
]
```

### Get Page Version
```
GET /api/pages/{pageId}/version
```
Headers:
- `X-Base-Url`: Your Confluence base URL (required)
- `Authorization`: Your authentication token (optional)

Response:
```json
{
  "version": "integer"
}
```

### OAuth 2.0 Endpoints

#### Start OAuth Login
```
GET /api/auth/login?redirect_uri={spa_url}
```
Redirects the user to Atlassian's authorization page. The `redirect_uri` parameter is optional — if omitted, the user is redirected to `/api/auth/success` after authorization. If provided, the origin must be listed in `ALLOWED_REDIRECT_ORIGINS`.

#### OAuth Callback
```
GET /api/auth/callback
```
Handles the Atlassian OAuth callback. Exchanges the authorization code for tokens and redirects to the target URL with `#access_token=...&refresh_token=...&expires_in=...`.

#### Refresh Token
```
POST /api/auth/refresh
```
Body:
```json
{ "refresh_token": "..." }
```
Response:
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

#### Get Accessible Resources
```
GET /api/auth/resources
```
Headers:
- `Authorization`: Bearer token from OAuth flow

Returns the list of Confluence sites the user can access. Use the `id` field as `cloudId` to construct `X-Base-Url: https://api.atlassian.com/ex/confluence/{cloudId}`.

Response:
```json
[
  {
    "id": "cloud-id",
    "name": "site-name",
    "url": "https://site.atlassian.net",
    "scopes": ["..."],
    "avatarUrl": "..."
  }
]
```

## Setup & Development

### Prerequisites
- Python 3.8+
- Node.js (for Vercel CLI)

### Local Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd confluence-page-api
```

2. **Install dependencies:**
```bash
uv sync
```

> If you don't have `uv`, install it with `curl -LsSf https://astral.sh/uv/install.sh | sh`

3. **Install Vercel CLI:**
```bash
npm i -g vercel
```

4. **Set up environment variables (for OAuth):**

Copy `.env.example` and fill in your values:
```bash
cp .env.example .env
```
```env
ATLASSIAN_CLIENT_ID=your_client_id
ATLASSIAN_CLIENT_SECRET=your_client_secret
STATE_SECRET=any_random_secret_string
ALLOWED_REDIRECT_ORIGINS=http://localhost:5173
```

Register your OAuth 2.0 app at [Atlassian Developer Console](https://developer.atlassian.com/console/myapps/) with callback URL `http://localhost:3000/api/auth/callback`.

### Running Locally

1. **Start the development server:**
```bash
vercel dev
```

The API will be available at `http://localhost:3000/api`.

### Running Tests

**Run all tests:**
```bash
uv run pytest tests/ -v
```

**Run specific test types:**
```bash
# Endpoint structure tests
uv run pytest tests/test_vercel_endpoints.py -v

# Service layer tests
uv run pytest tests/unit/test_confluence_proxy.py -v
```

**Run tests with coverage:**
```bash
uv run pytest tests/ --cov=api --cov-report=term-missing --cov-report=html:htmlcov
```

**Live server testing:**
```bash
# Start vercel dev in one terminal
vercel dev

# Run live tests in another terminal
python tests/run_vercel_tests.py
```

### Test Structure

The project uses a Vercel-compatible testing approach:

- **`tests/test_vercel_endpoints.py`** - HTTP endpoint structure validation
- **`tests/unit/test_confluence_proxy.py`** - Service layer unit tests
- **`tests/run_vercel_tests.py`** - Live server integration test runner

Tests avoid importing from `[pageId]` directories (Vercel dynamic routes) and instead test the HTTP interface, which is the recommended approach for serverless functions.

## Deployment

Deploy to Vercel with one click:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fvercel%2Fexamples%2Ftree%2Fmain%2Fpython%2Fconfluence-page-api)
