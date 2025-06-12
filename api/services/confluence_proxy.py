import requests
from typing import Dict, List

class PageVersion:
    def __init__(self, version: int, authorId: str, createdAt: str):
        self.version = version
        self.authorId = authorId
        self.createdAt = createdAt

class ConfluenceUser:
    def __init__(self, accountId: str, email: str, publicName: str, displayName: str, avatarUrl: str):
        self.accountId = accountId
        self.email = email
        self.publicName = publicName
        self.displayName = displayName
        self.avatarUrl = avatarUrl

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

    def get_page_versions(self, page_id: str, headers: Dict[str, str]) -> List[PageVersion]:
        results = []
        url = f"{self.base_url}/wiki/api/v2/pages/{page_id}/versions?limit=250"
        
        def extract_versions(response_data):
            return [
                PageVersion(
                    version['number'],
                    version['authorId'],
                    version['createdAt']
                ) for version in response_data.get('results', [])
            ]
        
        try:
            while url:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                results.extend(extract_versions(data))
                
                # Check for next page link
                url = None
                if '_links' in data and 'next' in data.get('_links', {}):
                    url = f"{self.base_url}{data['_links']['next']}"
        
        except requests.RequestException as e:
            # Handle connection errors, timeouts, etc.
            print(f"Error fetching page versions: {e}")
        
        return results

    def get_users(self, user_ids: List[str], headers: Dict[str, str]) -> List[ConfluenceUser]:
        results = []
        url = f"{self.base_url}/wiki/api/v2/users-bulk"
        response = requests.post(url, headers=headers, json={'accountIds': user_ids})
        json_response = response.json()

        return [
            ConfluenceUser(
                user['accountId'],
                user['email'],
                user['publicName'],
                user['displayName'],
                f"{self.base_url}{user['profilePicture']['path']}"
            ) for user in json_response['results']
        ]