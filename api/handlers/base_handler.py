from http.server import BaseHTTPRequestHandler
import json
from typing import Dict, Any, Optional
from api.services.confluence_proxy import ConfluenceProxy

class BaseConfluenceHandler(BaseHTTPRequestHandler):
    def get_headers_and_validate(self) -> Optional[tuple[str, str, Dict[str, str]]]:
        """Get and validate required headers, returns (page_id, base_url, headers) if valid"""
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
