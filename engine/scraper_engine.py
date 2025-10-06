import requests
from bs4 import BeautifulSoup
import yaml
import time
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import re
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobScraperEngine:
    def __init__(self, config_path: str = "configs/"):
        self.config_path = config_path
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    def load_config(self, config_file: str) -> Dict:
        """Load YAML configuration file"""
        try:
            with open(f"{self.config_path}{config_file}", 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"Loaded config: {config.get('site_name', 'Unknown')}")
                return config
        except Exception as e:
            logger.error(f"Error loading config {config_file}: {e}")
            return {}
    
    def get_page_content(self, url: str, use_scraperapi: bool = False, scraperapi_key: str = None) -> Optional[str]:
        """Fetch page content with optional ScraperAPI integration"""
        try:
            if use_scraperapi and scraperapi_key:
                payload = {
                    'api_key': scraperapi_key,
                    'url': url
                }
                response = requests.get('https://api.scraperapi.com/', params=payload, timeout=30)
            else:
                response = self.session.get(url, timeout=30)
            
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_text_from_selector(self, soup: BeautifulSoup, selector: str) -> str:
        """Extract text from CSS selector"""
        try:
            if '::text' in selector:
                # Extract text content
                css_selector = selector.replace('::text', '')
                element = soup.select_one(css_selector)
                return element.get_text(strip=True) if element else ""
            elif '::attr(' in selector:
                # Extract attribute value
                attr_match = re.search(r'::attr\(([^)]+)\)', selector)
                if attr_match:
                    attr_name = attr_match.group(1)
                    css_selector = selector.split('::attr(')[0]
                    element = soup.select_one(css_selector)
                    return element.get(attr_name, "") if element else ""
            else:
                # Regular selector
                element = soup.select_one(selector)
                return element.get_text(strip=True) if element else ""
        except Exception as e:
            logger.error(f"Error extracting from selector {selector}: {e}")
            return ""
    
    def scrape_jobs_from_page(self, html_content: str, config: Dict) -> List[Dict]:
        """Scrape jobs from a single page"""
        jobs = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            selectors = config.get('selectors', {})
            
            # Find all job containers
            job_containers = soup.select(selectors.get('job_container', ''))
            
            for container in job_containers:
                job_data = {}
                
                # Extract job data using selectors
                for field, selector in selectors.items():
                    if field != 'job_container':
                        job_data[field] = self.extract_text_from_selector(container, selector)
                
                # Add metadata
                job_data['source_site'] = config.get('site_name', 'Unknown')
                job_data['scraped_at'] = datetime.utcnow().isoformat()
                
                # Clean and validate job data
                if job_data.get('title') and job_data.get('company'):
                    jobs.append(job_data)
                    
        except Exception as e:
            logger.error(f"Error scraping jobs from page: {e}")
            
        return jobs
    
    def get_next_page_url(self, html_content: str, config: Dict, current_url: str) -> Optional[str]:
        """Get the next page URL for pagination"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            pagination = config.get('pagination', {})
            next_page_selector = pagination.get('next_page_selector', '')
            
            if next_page_selector:
                next_element = soup.select_one(next_page_selector)
                if next_element:
                    if '::attr(' in next_page_selector:
                        attr_match = re.search(r'::attr\(([^)]+)\)', next_page_selector)
                        if attr_match:
                            attr_name = attr_match.group(1)
                            next_url = next_element.get(attr_name, "")
                    else:
                        next_url = next_element.get('href', "")
                    
                    if next_url:
                        return urljoin(current_url, next_url)
                        
        except Exception as e:
            logger.error(f"Error getting next page URL: {e}")
            
        return None
    
    def scrape_site(self, config_file: str, max_pages: int = 5, use_scraperapi: bool = False, scraperapi_key: str = None) -> List[Dict]:
        """Scrape all jobs from a site based on configuration"""
        config = self.load_config(config_file)
        if not config:
            return []
        
        all_jobs = []
        start_url = config.get('start_url', '')
        current_url = start_url
        pages_scraped = 0
        
        logger.info(f"Starting to scrape {config.get('site_name', 'Unknown')} from {start_url}")
        
        while current_url and pages_scraped < max_pages:
            logger.info(f"Scraping page {pages_scraped + 1}: {current_url}")
            
            # Get page content
            html_content = self.get_page_content(current_url, use_scraperapi, scraperapi_key)
            if not html_content:
                break
            
            # Scrape jobs from current page
            page_jobs = self.scrape_jobs_from_page(html_content, config)
            all_jobs.extend(page_jobs)
            logger.info(f"Found {len(page_jobs)} jobs on page {pages_scraped + 1}")
            
            # Get next page URL
            current_url = self.get_next_page_url(html_content, config, current_url)
            pages_scraped += 1
            
            # Add delay between requests
            time.sleep(2)
        
        logger.info(f"Completed scraping {config.get('site_name', 'Unknown')}. Total jobs: {len(all_jobs)}")
        return all_jobs
    
    def scrape_multiple_sites(self, config_files: List[str], max_pages_per_site: int = 5, use_scraperapi: bool = False, scraperapi_key: str = None) -> Dict[str, List[Dict]]:
        """Scrape multiple sites and return results organized by site"""
        results = {}
        
        for config_file in config_files:
            try:
                site_jobs = self.scrape_site(config_file, max_pages_per_site, use_scraperapi, scraperapi_key)
                results[config_file] = site_jobs
            except Exception as e:
                logger.error(f"Error scraping {config_file}: {e}")
                results[config_file] = []
        
        return results
