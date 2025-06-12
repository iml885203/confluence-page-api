from api.handlers.base_handler import BaseConfluenceHandler
from api.services.confluence_proxy import ConfluenceProxy

class handler(BaseConfluenceHandler):
    def do_OPTIONS(self):
        self.send_success_response('')
        
    def do_GET(self):
        # Get page ID and validate headers
        result = self.get_page_context(page_id_position=-2)  # pageId is the second-to-last segment in the path
        if not result:
            return
        page_id, base_url, headers = result
        
        try:
            # use proxy to get version info
            confluence_proxy = ConfluenceProxy(base_url)
            version_info = confluence_proxy.get_page_version(page_id, headers)
            
            # send response
            self.send_success_response({'version': version_info})
            
        except Exception as e:
            self.send_error_response(500, str(e))