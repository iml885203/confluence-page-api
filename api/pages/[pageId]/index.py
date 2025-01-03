from bs4 import BeautifulSoup
from typing import List, Dict
from dataclasses import dataclass, asdict
import json
from urllib.parse import urlparse
from api.handlers.base_handler import BaseConfluenceHandler
from api.services.confluence_proxy import ConfluenceProxy

@dataclass
class SubLink:
    Title: str
    Link: str

@dataclass
class ConfluenceWeb:
    Icon: str
    Title: str
    Description: str
    Tags: List[str]
    Link: str
    SubLinks: List[SubLink]
    Category: str

@dataclass
class CategoryWeb:
    category: str
    webs: List[ConfluenceWeb]

def parse_content(page_html: str) -> List[CategoryWeb]:
    # parse html
    soup = BeautifulSoup(page_html, 'html.parser')
    
    # get categories(h2)
    categories = [h2.text for h2 in soup.find_all('h2')]
    
    # get tables
    tables = soup.find_all('table')
    category_webs = []
    
    for index, table in enumerate(tables):
        rows = table.select('tbody tr')
        webs = []
        
        for row in rows:
            columns = row.find_all('td')
            
            if len(columns) >= 6:
                icon_img = columns[0].find('img')
                icon = icon_img.get('src') if icon_img else ''
                title = columns[1].text.strip()
                description = columns[2].text.strip()
                tags = [tag.strip() for tag in columns[3].text.split(',') if tag.strip()]
                link = columns[4].text.strip()
                
                sub_links = []
                for p in columns[5].find_all('p'):
                    if not p.text:
                        continue
                    
                    title_parts = p.text.split(':')
                    if not title_parts:
                        continue
                        
                    sub_title = title_parts[0]
                    a_tag = p.find('a')
                    sub_link = a_tag.get('href') if a_tag else ''
                    
                    if sub_title and sub_link:
                        sub_links.append(SubLink(
                            Title=sub_title,
                            Link=sub_link
                        ))
                
                if title:
                    webs.append(ConfluenceWeb(
                        Icon=icon,
                        Title=title,
                        Description=description,
                        Tags=tags,
                        Link=link,
                        SubLinks=sub_links,
                        Category=categories[index]
                    ))
        
        category_webs.append(CategoryWeb(
            category=categories[index],
            webs=webs
        ))
    
    return category_webs

class handler(BaseConfluenceHandler):
    def do_OPTIONS(self):
        self.send_success_response('')
        
    def do_GET(self):
        # Parse URL more elegantly
        parsed_url = urlparse(self.path)
        page_id = parsed_url.path.split('/')[-1]
        
        # get and validate headers
        result = self.get_headers_and_validate()
        if not result:
            return
        base_url, headers = result

        try:
            # Use the proxy to get page content
            confluence_proxy = ConfluenceProxy(base_url)
            body_content = confluence_proxy.get_page_content(page_id, headers)
            
            # Parse the HTML content
            parsed_content = parse_content(body_content)
            
            # Convert dataclass objects to dictionaries
            result = [asdict(category) for category in parsed_content]
            
            # Send response
            self.send_success_response(result)
            
        except Exception as e:
            self.send_error_response(500, str(e))