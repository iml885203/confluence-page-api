# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a serverless Python API for Confluence page operations deployed on Vercel. The architecture follows a handler-based pattern with service classes for external API integration.

**Key Components:**
- `api/handlers/base_handler.py`: Base HTTP handler class providing common functionality for authentication, header validation, and response handling
- `api/services/confluence_proxy.py`: Service layer for Confluence API interactions with pagination support
- `api/pages/[pageId]/`: Dynamic route handlers for page-specific operations
- `api/proxy/pages/[pageId].py`: Proxy endpoint for direct page access

**Data Models:**
- `PageVersion`: Represents page version metadata (version, authorId, createdAt)
- `ConfluenceUser`: User information with avatar URLs

## Common Commands

**Local Development:**
```bash
vercel dev
```
The API will be available at `http://localhost:3000/api`.

**Dependencies:**
- Python dependencies are managed via `requirements.txt`
- Install with: `pip install -r requirements.txt`

## API Authentication & Headers

All endpoints require the `X-Base-Url` header containing the Confluence base URL. Authentication is handled via the optional `Authorization` header passed through to Confluence APIs.

**Required Headers:**
- `X-Base-Url`: Confluence instance base URL
- `Authorization`: (Optional) Authentication token

## Confluence API Integration

The `ConfluenceProxy` class handles all Confluence API v2 interactions:
- Uses `body-format=view` for content retrieval
- Implements pagination for version history (250 items per page)
- Supports bulk user lookups
- Handles connection errors gracefully

## Deployment

Deployed on Vercel with CORS enabled for all origins. The `vercel.json` configuration handles redirects and cross-origin headers.