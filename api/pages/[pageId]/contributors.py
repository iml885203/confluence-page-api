from urllib.parse import urlparse, parse_qs
from api.handlers.base_handler import BaseConfluenceHandler
from api.services.confluence_proxy import ConfluenceProxy
from datetime import datetime
from collections import defaultdict

class handler(BaseConfluenceHandler):
    def do_OPTIONS(self):
        self.send_success_response('')
        
    def do_GET(self):
        result = self.get_page_context(page_id_position=-2)
        if not result:
            return
        page_id, base_url, headers = result
        
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            # Get limit parameters with defaults
            contributors_limit = int(query_params.get('contributors_limit', ['10'])[0])
            contributions_limit = int(query_params.get('contributions_limit', ['20'])[0])
            
            # Create the confluence proxy
            confluence_proxy = ConfluenceProxy(base_url)
            
            # Get all page versions
            page_versions = confluence_proxy.get_page_versions(page_id, headers)
            
            # Extract unique contributor IDs
            contributor_ids = list(set(version.authorId for version in page_versions))
            
            # Get contributor details
            contributors = confluence_proxy.get_users(contributor_ids, headers)
            
            # Create a lookup map for contributors
            contributor_map = {c.accountId: c for c in contributors}
            
            # Process versions to get contributions with timestamps
            contributions = []
            for version in page_versions:
                contributor_id = version.authorId
                if contributor_id not in contributor_map:
                    continue
                    
                contributor = contributor_map[contributor_id]
                created_at = version.createdAt
                
                contributions.append({
                    'version': version.version,
                    'contributorId': contributor_id,
                    'contributorName': contributor.displayName,
                    'contributorEmail': contributor.email,
                    'contributorAvatar': contributor.avatarUrl,
                    'timestamp': created_at
                })
            
            # Sort contributions by timestamp (newest first)
            contributions.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Count contributions per contributor
            contributor_counts = defaultdict(int)
            for contribution in contributions:
                contributor_counts[contribution['contributorId']] += 1
            
            # Build contributor list with counts
            contributor_list = []
            for contributor in contributors:
                contributor_list.append({
                    'accountId': contributor.accountId,
                    'email': contributor.email,
                    'publicName': contributor.publicName,
                    'displayName': contributor.displayName,
                    'avatarUrl': contributor.avatarUrl,
                    'contributionCount': contributor_counts[contributor.accountId]
                })
            
            # Sort contributors by contribution count (descending)
            contributor_list.sort(key=lambda x: x['contributionCount'], reverse=True)
            
            # Apply limits
            limited_contributors = contributor_list[:contributors_limit]
            limited_contributions = contributions[:contributions_limit]
            
            # Return the limited data
            response = {
                'contributors': limited_contributors,
                'contributions': limited_contributions,
                'totalVersions': len(page_versions),
                'totalContributors': len(contributor_list),
                'meta': {
                    'contributorsLimit': contributors_limit,
                    'contributionsLimit': contributions_limit,
                    'totalContributionsAvailable': len(contributions)
                }
            }
            
            # Send the successful response
            self.send_success_response(response)
            
        except Exception as e:
            self.send_error_response(500, f"Failed to get page contributors: {str(e)}")
        