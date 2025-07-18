import pytest
import requests
from unittest.mock import Mock, patch
from api.services.confluence_proxy import ConfluenceProxy, PageVersion, ConfluenceUser


class TestConfluenceProxy:
    
    def setup_method(self):
        self.proxy = ConfluenceProxy('https://example.atlassian.net')
        self.headers = {'Authorization': 'Bearer token123', 'Accept': 'application/json'}
    
    @patch('requests.get')
    def test_get_page_content_success(self, mock_get):
        """Test successful page content retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'body': {
                'view': {
                    'value': '<h1>Test Content</h1>'
                }
            }
        }
        mock_get.return_value = mock_response
        
        result = self.proxy.get_page_content('12345', self.headers)
        
        assert result == '<h1>Test Content</h1>'
        mock_get.assert_called_once_with(
            'https://example.atlassian.net/wiki/api/v2/pages/12345?body-format=view',
            headers=self.headers
        )
    
    @patch('requests.get')
    def test_get_page_content_empty_body(self, mock_get):
        """Test page content retrieval with empty body"""
        mock_response = Mock()
        mock_response.json.return_value = {'body': {}}
        mock_get.return_value = mock_response
        
        result = self.proxy.get_page_content('12345', self.headers)
        
        assert result == ''
    
    @patch('requests.get')
    def test_get_page_version_success(self, mock_get):
        """Test successful page version retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'version': {
                'number': 42
            }
        }
        mock_get.return_value = mock_response
        
        result = self.proxy.get_page_version('12345', self.headers)
        
        assert result == 42
        mock_get.assert_called_once_with(
            'https://example.atlassian.net/wiki/api/v2/pages/12345',
            headers=self.headers
        )
    
    @patch('requests.get')
    def test_get_page_versions_single_page(self, mock_get):
        """Test page versions retrieval with single page"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {
                    'number': 1,
                    'authorId': 'user1',
                    'createdAt': '2023-01-01T00:00:00Z'
                },
                {
                    'number': 2,
                    'authorId': 'user2',
                    'createdAt': '2023-01-02T00:00:00Z'
                }
            ],
            '_links': {}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.proxy.get_page_versions('12345', self.headers)
        
        assert len(result) == 2
        assert result[0].version == 1
        assert result[0].authorId == 'user1'
        assert result[0].createdAt == '2023-01-01T00:00:00Z'
        assert result[1].version == 2
        assert result[1].authorId == 'user2'
        assert result[1].createdAt == '2023-01-02T00:00:00Z'
    
    @patch('requests.get')
    def test_get_page_versions_pagination(self, mock_get):
        """Test page versions retrieval with pagination"""
        # First page response
        first_response = Mock()
        first_response.json.return_value = {
            'results': [
                {
                    'number': 1,
                    'authorId': 'user1',
                    'createdAt': '2023-01-01T00:00:00Z'
                }
            ],
            '_links': {
                'next': '/wiki/api/v2/pages/12345/versions?cursor=abc123'
            }
        }
        first_response.raise_for_status.return_value = None
        
        # Second page response
        second_response = Mock()
        second_response.json.return_value = {
            'results': [
                {
                    'number': 2,
                    'authorId': 'user2',
                    'createdAt': '2023-01-02T00:00:00Z'
                }
            ],
            '_links': {}
        }
        second_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [first_response, second_response]
        
        result = self.proxy.get_page_versions('12345', self.headers)
        
        assert len(result) == 2
        assert mock_get.call_count == 2
        mock_get.assert_any_call(
            'https://example.atlassian.net/wiki/api/v2/pages/12345/versions?limit=250',
            headers=self.headers
        )
        mock_get.assert_any_call(
            'https://example.atlassian.net/wiki/api/v2/pages/12345/versions?cursor=abc123',
            headers=self.headers
        )
    
    @patch('requests.get')
    def test_get_page_versions_request_exception(self, mock_get):
        """Test page versions retrieval with request exception"""
        mock_get.side_effect = requests.RequestException("Connection error")
        
        result = self.proxy.get_page_versions('12345', self.headers)
        
        assert result == []
    
    @patch('requests.post')
    def test_get_users_success(self, mock_post):
        """Test successful users retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {
                    'accountId': 'user1',
                    'email': 'user1@example.com',
                    'publicName': 'User One',
                    'displayName': 'User One',
                    'profilePicture': {
                        'path': '/avatar/user1.png'
                    }
                },
                {
                    'accountId': 'user2',
                    'email': 'user2@example.com',
                    'publicName': 'User Two',
                    'displayName': 'User Two',
                    'profilePicture': {
                        'path': '/avatar/user2.png'
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        user_ids = ['user1', 'user2']
        result = self.proxy.get_users(user_ids, self.headers)
        
        assert len(result) == 2
        assert result[0].accountId == 'user1'
        assert result[0].email == 'user1@example.com'
        assert result[0].avatarUrl == 'https://example.atlassian.net/avatar/user1.png'
        assert result[1].accountId == 'user2'
        assert result[1].email == 'user2@example.com'
        assert result[1].avatarUrl == 'https://example.atlassian.net/avatar/user2.png'
        
        mock_post.assert_called_once_with(
            'https://example.atlassian.net/wiki/api/v2/users-bulk',
            headers=self.headers,
            json={'accountIds': user_ids}
        )


class TestPageVersion:
    
    def test_page_version_creation(self):
        """Test PageVersion object creation"""
        version = PageVersion(1, 'user123', '2023-01-01T00:00:00Z')
        
        assert version.version == 1
        assert version.authorId == 'user123'
        assert version.createdAt == '2023-01-01T00:00:00Z'


class TestConfluenceUser:
    
    def test_confluence_user_creation(self):
        """Test ConfluenceUser object creation"""
        user = ConfluenceUser(
            'user123',
            'user@example.com',
            'User Name',
            'User Display Name',
            'https://example.com/avatar.png'
        )
        
        assert user.accountId == 'user123'
        assert user.email == 'user@example.com'
        assert user.publicName == 'User Name'
        assert user.displayName == 'User Display Name'
        assert user.avatarUrl == 'https://example.com/avatar.png'