import requests
from typing import Dict

class ConfluenceProxy:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_page_content(self, page_id: str, headers: dict) -> str:
        # Always add body-format=view when calling Confluence API
        confluence_url = f"{self.base_url}/wiki/api/v2/pages/{page_id}?body-format=view"
        response = requests.get(confluence_url, headers=headers)
        
        json_response = response.json()
        return json_response.get('body', {}).get('view', {}).get('value', '')

    def get_page_version(self, page_id: str, headers: Dict[str, str]) -> int:
        # Get page version from Confluence API
        confluence_url = f"{self.base_url}/wiki/api/v2/pages/{page_id}"
        response = requests.get(confluence_url, headers=headers)
        json_response = response.json()
        return json_response['version']['number'] 