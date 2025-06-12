from http.server import BaseHTTPRequestHandler
import json
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse
from api.services.confluence_proxy import ConfluenceProxy

class BaseConfluenceHandler(BaseHTTPRequestHandler):
    def get_headers_and_validate(self) -> Optional[Tuple[str, Dict[str, str]]]:
        """Get and validate required headers, returns (base_url, headers) if valid"""
        # Get headers from request
        auth_header = self.headers.get('Authorization')
        base_url = self.headers.get('X-Base-Url')
        
        if not base_url:
            self.send_error_response(400, 'X-Base-Url header is required')
            return None
            
        # Set up headers for the Atlassian API request
        headers = {
            'Accept': 'application/json'
        }
        if auth_header:
            headers['Authorization'] = auth_header
            
        return base_url, headers
    
    def parse_page_id(self, position: int = -1) -> str:
        """
        Extract page ID from the URL path
        
        Args:
            position: Position of page ID in the path (default: -1 for last segment)
                     Use -2 for paths like /[pageId]/version where pageId is second to last
        
        Returns:
            The extracted page ID
        """
        parsed_url = urlparse(self.path)
        segments = parsed_url.path.split('/')
        return segments[position]
    
    def get_page_context(self, page_id_position: int = -1) -> Optional[Tuple[str, str, Dict[str, str]]]:
        """
        Common method to extract page ID and validate headers
        
        Args:
            page_id_position: Position of page ID in the path
        
        Returns:
            Tuple of (page_id, base_url, headers) if successful, None otherwise
        """
        page_id = self.parse_page_id(page_id_position)
        
        result = self.get_headers_and_validate()
        if not result:
            return None
            
        base_url, headers = result
        return page_id, base_url, headers
    
    def send_error_response(self, status_code: int, message: str) -> None:
        """Send error response with given status code and message"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error_response = {'error': message}
        self.wfile.write(json.dumps(error_response).encode())
        
    def send_success_response(self, data: Any) -> None:
        """Send success response with given data"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
