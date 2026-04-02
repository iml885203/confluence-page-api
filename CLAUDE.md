# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a serverless Python API for Confluence page operations deployed on Vercel. The architecture follows a handler-based pattern with service classes for external API integration.

**Key Components:**
- `api/handlers/base_handler.py`: Base HTTP handler class providing common functionality for authentication, header validation, and response handling
- `api/services/confluence_proxy.py`: Service layer for Confluence API interactions with pagination support
- `api/services/oauth_config.py`: Shared OAuth 2.0 configuration, constants, and helper functions
- `api/pages/[pageId]/`: Dynamic route handlers for page-specific operations
- `api/auth/`: OAuth 2.0 (3LO) endpoints for Atlassian authentication

**Data Models:**
- `PageVersion`: Represents page version metadata (version, authorId, createdAt)
- `ConfluenceUser`: User information with avatar URLs

## Dual Authentication Modes

The API supports two authentication modes simultaneously:

1. **Pass-through (legacy)**: Client sends `X-Base-Url` (direct Confluence URL) + `Authorization` header. The API forwards credentials to Confluence as-is.

2. **OAuth 2.0**: Client obtains token via `/api/auth/login` flow, then sends `X-Base-Url: https://api.atlassian.com/ex/confluence/{cloudId}` + `Authorization: Bearer {token}`. The existing `ConfluenceProxy` works unchanged because the gateway URL follows the same `{base_url}/wiki/api/v2/...` pattern.

## Confluence API Integration

The `ConfluenceProxy` class handles all Confluence API v2 interactions:
- Uses `body-format=view` for content retrieval
- Implements pagination for version history (250 items per page)
- Supports bulk user lookups
- Handles connection errors gracefully
