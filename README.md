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

## Running Locally

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Run the development server:
```bash
vercel dev
```

The API will be available at `http://localhost:3000/api`.

## Deployment

Deploy to Vercel with one click:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fvercel%2Fexamples%2Ftree%2Fmain%2Fpython%2Fconfluence-page-api)
