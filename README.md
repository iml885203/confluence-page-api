# Confluence Page API

This project provides a serverless API for interacting with Confluence pages. Built with Python and deployed on Vercel, it offers endpoints to fetch and parse Confluence page content and version information.

## Features

- **Page Content API**: Fetches and parses Confluence page content into a structured format
- **Version API**: Retrieves version information for Confluence pages
- **Base URL Configuration**: Configurable Confluence base URL through headers
- **Authentication Support**: Handles Confluence authentication through headers

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

2. **Set up Python virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

4. **Install Vercel CLI:**
```bash
npm i -g vercel
```

### Running Locally

1. **Start the development server:**
```bash
vercel dev
```

The API will be available at `http://localhost:3000/api`.

### Running Tests

**Run all tests:**
```bash
pytest tests/ -v
```

**Run specific test types:**
```bash
# Endpoint structure tests
pytest tests/test_vercel_endpoints.py -v

# Service layer tests
pytest tests/unit/test_confluence_proxy.py -v
```

**Run tests with coverage:**
```bash
pytest tests/ --cov=api --cov-report=term-missing --cov-report=html:htmlcov
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
