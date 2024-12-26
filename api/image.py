from http.server import BaseHTTPRequestHandler
import urllib.parse
import requests
import base64
import os
from urllib.parse import parse_qs, urlencode

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        # Get url and token from query parameters
        encoded_url = query_params.get('url', [''])[0]
        token = query_params.get('token', [''])[0]
        
        if not encoded_url or not token:
            self.send_response(400)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Missing required parameters: url and token")
            return
            
        try:
            # Decode URL properly
            url = urllib.parse.unquote(encoded_url)
            
            # Parse the URL to preserve all query parameters
            parsed_url = urllib.parse.urlparse(url)
            url_query_params = parse_qs(parsed_url.query)
            
            # Rebuild the URL with all parameters
            final_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            if url_query_params:
                # Convert multi-value dict to single-value dict
                single_params = {k: v[0] for k, v in url_query_params.items()}
                final_url = f"{final_url}?{urlencode(single_params)}"
            
            # Make request to the actual image URL with Authorization header
            headers = {
                'Authorization': f'Basic {token}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(final_url, headers=headers, stream=True)
            
            # Check if the request was successful
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', 'image/png')
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                if 'Content-Length' in response.headers:
                    self.send_header('Content-Length', response.headers['Content-Length'])
                self.end_headers()
                
                # Stream the response content
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        self.wfile.write(chunk)
            else:
                print(f"Failed to fetch image. Status: {response.status_code}")
                if response.status_code != 200:
                    print("Error response:", response.text[:200])
                
                self.send_response(response.status_code)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                error_message = f"Failed to fetch image (Status: {response.status_code})"
                self.wfile.write(error_message.encode('utf-8'))
                
        except Exception as e:
            import traceback
            print(f"Error occurred: {str(e)}")
            print(traceback.format_exc())
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            error_message = f"Internal server error: {str(e)}"
            self.wfile.write(error_message.encode('utf-8'))
