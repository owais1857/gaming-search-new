import json
import time
import re
import os
from urllib.parse import urlparse, urljoin, urlunparse
from collections import deque
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

class GamingDeepCrawler:
    def __init__(self, base_urls, max_depth=2, delay=2, max_pages=200, pages_per_site=30):
        self.base_urls = base_urls
        self.max_depth = max_depth
        self.visited = set()
        self.data = []
        self.delay = delay
        self.max_pages = max_pages
        self.pages_per_site = pages_per_site
        self.site_data_counts = {}
        self.gaming_keywords = [
            'game', 'gaming', 'gamer', 'review', 'preview', 'trailer',
            'gameplay', 'developer', 'publisher', 'console', 'pc',
            'xbox', 'playstation', 'nintendo', 'steam', 'epic',
            'mod', 'dlc', 'patch', 'update', 'release', 'esports',
            'twitch', 'streamer', 'gaming news', 'indie game'
        ]
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def is_gaming_related(self, text):
        """Check if content is gaming-related"""
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.gaming_keywords)
    
    def is_valid_url(self, url):
        """Validate URL structure and gaming relevance"""
        if not url:
            return False
            
        parsed = urlparse(url)
        if not parsed.scheme.startswith('http'):
            return False
        
        # Skip unwanted file types
        skip_extensions = ['.pdf', '.jpg', '.png', '.gif', '.zip', '.exe', '.mp4', '.avi']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip social media and irrelevant paths
        skip_patterns = [
            '/login', '/register', '/cart', '/checkout', '/privacy',
            '/terms', '/contact', '/about', '/careers'
        ]
        if any(pattern in url.lower() for pattern in skip_patterns):
            return False
            
        return True
    
    def normalize_url(self, url, base):
        """Normalize and clean URLs"""
        if not url:
            return None
            
        try:
            normalized = urljoin(base, url)
            parsed = urlparse(normalized)
            cleaned = urlunparse(parsed._replace(fragment=''))
            return cleaned
        except Exception:
            return None
    
    def extract_metadata(self, soup, url):
        """Extract metadata in format compatible with existing crawlers"""
        try:
            # Title extraction
            title = ""
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            elif soup.find('h1'):
                title = soup.find('h1').get_text().strip()
            
            # Meta description for summary
            summary = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if not meta_desc:
                meta_desc = soup.find('meta', attrs={'property': 'og:description'})
            if meta_desc:
                summary = meta_desc.get('content', '').strip()
            
            # Main content extraction
            content_selectors = [
                'article', '.article-content', '.post-content', '.content',
                '.entry-content', '.article-body', 'main', '.main-content'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content_parts = []
                    for elem in elements:
                        for script in elem(["script", "style", "nav", "header", "footer"]):
                            script.decompose()
                        text = elem.get_text().strip()
                        if text and len(text) > 50:
                            content_parts.append(text)
                    content = ' '.join(content_parts)
                    break
            
            # Fallback to paragraphs
            if not content or len(content) < 100:
                paragraphs = soup.find_all('p')
                para_texts = []
                for p in paragraphs:
                    text = p.get_text().strip()
                    if text and len(text) > 20:
                        para_texts.append(text)
                content = ' '.join(para_texts)
            
            # Extract date
            date = ""
            date_selectors = [
                'time[datetime]', '.date', '.published', '.post-date',
                '.article-date', '[class*="date"]'
            ]
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date = (date_elem.get('datetime') or 
                           date_elem.get('content') or 
                           date_elem.get_text().strip())
                    if date:
                        break
            
            # Get source domain
            source_domain = urlparse(url).netloc
            source_name = source_domain.replace('www.', '').replace('.com', '').title()
            
            # Return in compatible format (flat structure like other crawlers)
            return {
                'title': title,
                'summary': summary[:500] if summary else content[:200] + "..." if content else "",
                'content': content[:2000],  # Limit for processing
                'url': url,
                'date': date,
                'source': source_name
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata from {url}: {str(e)}")
            return None
    
    def find_links(self, soup, base_url):
        """Extract and filter relevant links"""
        links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            normalized = self.normalize_url(href, base_url)
            
            if not normalized or normalized in self.visited:
                continue
            
            parsed_link = urlparse(normalized)
            
            # Prioritize same-domain links
            if parsed_link.netloc == base_domain:
                link_text = link.get_text().strip().lower()
                
                if self.is_gaming_related(link_text) or self.is_gaming_related(href):
                    links.insert(0, normalized)
                else:
                    links.append(normalized)
        
        return links[:10]  # Limit links per page
    
    def crawl_page(self, url, depth):
        """Crawl a single page with site limits"""
        site_domain = urlparse(url).netloc
        current_site_count = self.site_data_counts.get(site_domain, 0)
        
        if (depth > self.max_depth or 
            url in self.visited or 
            not self.is_valid_url(url) or 
            len(self.data) >= self.max_pages or
            current_site_count >= self.pages_per_site):
            return
        
        try:
            self.logger.info(f"Crawling: {url} (depth: {depth})")
            time.sleep(self.delay)
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                return
            
            self.visited.add(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract page data
            page_data = self.extract_metadata(soup, url)
            
            if not page_data:
                return
            
            # Check content quality
            content_check = (page_data.get('title', '') + ' ' + 
                           page_data.get('content', '')).strip()
            
            # Save if gaming-related and substantial
            if (self.is_gaming_related(content_check) and len(content_check) > 100):
                self.data.append(page_data)
                self.site_data_counts[site_domain] = current_site_count + 1
                self.logger.info(f"✓ Saved from {site_domain} ({self.site_data_counts[site_domain]} pages)")
            
            # Crawl deeper if within limits
            if depth < self.max_depth:
                links = self.find_links(soup, url)
                for link in links:
                    if len(self.data) < self.max_pages:
                        self.crawl_page(link, depth + 1)
        
        except Exception as e:
            self.logger.error(f"Error crawling {url}: {str(e)}")
    
    def start_crawl(self):
        """Start balanced crawling"""
        self.logger.info("Starting balanced gaming crawl...")
        start_time = time.time()
        
        for i, url in enumerate(self.base_urls):
            site_domain = urlparse(url).netloc
            self.logger.info(f"Site {i+1}/{len(self.base_urls)}: {site_domain}")
            
            initial_count = len(self.data)
            self.crawl_page(url, 0)
            
            pages_added = len(self.data) - initial_count
            self.logger.info(f"Added {pages_added} pages from {site_domain}")
            
            if len(self.data) >= self.max_pages:
                break
        
        end_time = time.time()
        self.logger.info(f"Crawl completed: {len(self.data)} pages in {end_time - start_time:.1f}s")
    
    def save_to_json(self, filepath, append_mode=True):
        """Save data in format compatible with existing crawlers"""
        try:
            existing_data = []
            
            # Load existing data if appending
            if append_mode and os.path.exists(filepath):
                self.logger.info(f"Loading existing data from {filepath}")
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        # Handle both array format and line-by-line JSON
                        if content.startswith('['):
                            existing_data = json.loads(content)
                        else:
                            # Line-by-line JSON format
                            for line in content.split('\n'):
                                if line.strip():
                                    try:
                                        existing_data.append(json.loads(line))
                                    except json.JSONDecodeError:
                                        continue
            
            # Get existing URLs to avoid duplicates
            existing_urls = {item.get('url') for item in existing_data if item.get('url')}
            
            # Filter new data to avoid duplicates
            new_data = [item for item in self.data if item.get('url') not in existing_urls]
            
            # Combine data
            all_data = existing_data + new_data
            
            # Save in array format (compatible with pandas)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✓ Saved {len(new_data)} new items to {filepath}")
            self.logger.info(f"✓ Total items in file: {len(all_data)}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving JSON: {str(e)}")
            # Fallback: save only new data
            try:
                backup_file = f"backup_{filepath}"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
                self.logger.info(f"Saved to backup file: {backup_file}")
                return backup_file
            except:
                return None

# Usage
if __name__ == "__main__":
    gaming_urls = [
        "https://www.ign.com/",
        "https://www.pcgamer.com/",
        "https://www.gamespot.com/",
        "https://www.polygon.com/",
        "https://kotaku.com/",
        "https://www.rockpapershotgun.com/",
        "https://www.destructoid.com/",
        "https://www.eurogamer.net/"
    ]
    
    crawler = GamingDeepCrawler(
        base_urls=gaming_urls,
        max_depth=2,
        delay=2,
        max_pages=160,     # Total across all sites
        pages_per_site=20  # Per site limit for balance
    )
    
    crawler.start_crawl()
    
    # Save in compatible format
    output_file = crawler.save_to_json('gaming_content_crawl.json', append_mode=True)
    
    if output_file:
        print(f"\n✅ Crawling Complete!")
        print(f"📄 Total pages: {len(crawler.data)}")
        print(f"💾 Saved to: {output_file}")
        print(f"🌐 Sites crawled: {len(crawler.site_data_counts)}")
        
        for site, count in crawler.site_data_counts.items():
            print(f"   {site}: {count} pages")
    else:
        print("❌ Failed to save data")
