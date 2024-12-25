from http.server import BaseHTTPRequestHandler
import requests
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Get pageId from path
        path_parts = self.path.split('/')
        page_id = path_parts[-1]  # Get the last part of the path
        
        # Get Authorization header from request
        auth_header = self.headers.get('Authorization')
        
        # Set up headers for the Atlassian API request
        headers = {
            'Accept': 'application/json'
        }
        
        # Add Authorization header if provided
        if auth_header:
            headers['Authorization'] = auth_header
            
        # Construct the Atlassian API URL
        base_url = 'https://ironman.atlassian.net/wiki/api/v2/pages'
        url = f'{base_url}/{page_id}'
        
        try:
            # Make request to Atlassian API
            response = requests.get(url, headers=headers)
            
            # Set response status code
            self.send_response(response.status_code)
            
            # Set response headers
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Send response body
            self.wfile.write(response.content)
            
        except Exception as e:
            # Handle errors
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(str(e).encode()) 