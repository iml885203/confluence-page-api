import requests
from typing import Dict, List


class ConfluenceApiError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


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

    def _check_response(self, response: requests.Response):
        if not response.ok:
            try:
                error_data = response.json()
                message = error_data.get('message', error_data.get('error', response.text))
            except ValueError:
                message = response.text
            raise ConfluenceApiError(response.status_code, message)

    def get_page_content(self, page_id: str, headers: dict) -> str:
        confluence_url = f"{self.base_url}/wiki/api/v2/pages/{page_id}?body-format=view"
        response = requests.get(confluence_url, headers=headers)
        self._check_response(response)

        json_response = response.json()
        return json_response.get('body', {}).get('view', {}).get('value', '')

    def get_page_version(self, page_id: str, headers: Dict[str, str]) -> int:
        confluence_url = f"{self.base_url}/wiki/api/v2/pages/{page_id}"
        response = requests.get(confluence_url, headers=headers)
        self._check_response(response)

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
                self._check_response(response)

                data = response.json()
                results.extend(extract_versions(data))

                url = None
                if '_links' in data and 'next' in data.get('_links', {}):
                    url = f"{self.base_url}{data['_links']['next']}"
        except requests.RequestException as e:
            print(f"Error fetching page versions: {e}")

        return results

    def get_users(self, user_ids: List[str], headers: Dict[str, str]) -> List[ConfluenceUser]:
        url = f"{self.base_url}/wiki/api/v2/users-bulk"
        response = requests.post(url, headers=headers, json={'accountIds': user_ids})
        self._check_response(response)

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
