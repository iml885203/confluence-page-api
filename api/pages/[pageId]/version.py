from urllib.parse import urlparse
from api.handlers.base_handler import BaseConfluenceHandler
from api.services.confluence_proxy import ConfluenceProxy

class handler(BaseConfluenceHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.process_request()
        
    def do_GET(self):
        # parse url to get pageId
        parsed_url = urlparse(self.path)
        page_id = parsed_url.path.split('/')[-2]  # get pageId from /[pageId]/version
        
        # get and validate headers
        result = self.get_headers_and_validate()
        if not result:
            return
        base_url, headers = result
        
        try:
            # use proxy to get version info
            confluence_proxy = ConfluenceProxy(base_url)
            version_info = confluence_proxy.get_page_version(page_id, headers)
            
            # send response
            self.send_success_response({'version': version_info})
            
        except Exception as e:
            self.send_error_response(500, str(e))