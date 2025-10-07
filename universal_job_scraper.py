#!/usr/bin/env python3
"""
Universal Job Scraper - A standardized system for scraping job sites
Supports 100+ different job sites using YAML configurations
"""

import requests
import yaml
import json
import time
import logging
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime
import os
import re
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class JobData:
    """Standardized job data structure"""
    url: str = ""
    title: str = ""
    company: str = ""
    location: str = ""
    description: str = ""
    full_description: str = ""
    requirements: str = ""
    posted_date: str = ""
    job_type: str = ""
    department: str = ""
    experience_level: str = ""
    salary: str = ""
    benefits: str = ""
    closing_date: str = ""
    work_arrangement: str = ""
    travel_required: str = ""
    eligibility: str = ""
    clearance: str = ""
    physical_requirements: str = ""
    equal_opportunity: str = ""
    job_id: str = ""
    source_site: str = ""
    scraped_at: str = ""

class UniversalJobScraper:
    """Universal job scraper that works with YAML configurations"""
    
    def __init__(self, config_dir: str = "configs/", scraperapi_key: str = None):
        # Load environment variables
        load_dotenv('.env')
        
        self.config_dir = config_dir
        self.scraperapi_key = scraperapi_key or os.getenv('SCRAPERAPI_KEY')
        if not self.scraperapi_key:
            raise ValueError("SCRAPERAPI_KEY not found in environment variables. Please set it in .env file.")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Initialize database
        self.init_database()
        
    def _sanitize_job_fields(self, job_data: Dict) -> Dict:
        """Map/clean fields to match JobData and drop unknown keys."""
        try:
            # Map date_posted -> posted_date
            if 'date_posted' in job_data:
                if not job_data.get('posted_date') and job_data['date_posted']:
                    job_data['posted_date'] = job_data['date_posted']
                # Remove original to avoid unexpected kwargs
                job_data.pop('date_posted', None)

            # Ensure url is present if apply_url exists
            if job_data.get('apply_url') and not job_data.get('url'):
                job_data['url'] = job_data['apply_url']

            # Keep only fields defined in JobData
            allowed_fields = set(JobData.__dataclass_fields__.keys())
            cleaned = {k: v for k, v in job_data.items() if k in allowed_fields}
            return cleaned
        except Exception:
            # Fallback: at least remove date_posted
            job_data.pop('date_posted', None)
            return job_data

    def init_database(self):
        """Initialize SQLite database for storing jobs"""
        self.db_path = "jobs_database.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                title TEXT,
                company TEXT,
                location TEXT,
                description TEXT,
                full_description TEXT,
                requirements TEXT,
                posted_date TEXT,
                job_type TEXT,
                department TEXT,
                experience_level TEXT,
                salary TEXT,
                benefits TEXT,
                closing_date TEXT,
                work_arrangement TEXT,
                travel_required TEXT,
                eligibility TEXT,
                clearance TEXT,
                physical_requirements TEXT,
                equal_opportunity TEXT,
                job_id TEXT,
                source_site TEXT,
                scraped_at TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def load_config(self, config_file: str) -> Dict:
        """Load YAML configuration file"""
        try:
            config_path = os.path.join(self.config_dir, config_file)
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                logger.info(f"Loaded config: {config.get('site_name', 'Unknown')}")
                return config
        except Exception as e:
            logger.error(f"Error loading config {config_file}: {e}")
            return {}
    
    def get_page_content(self, url: str, use_scraperapi: bool = True) -> Optional[str]:
        """Fetch page content with ScraperAPI"""
        try:
            if use_scraperapi:
                payload = {
                    'api_key': self.scraperapi_key,
                    'url': url,
                    'render': 'true',  # Enable JavaScript rendering for SPAs
                    'country_code': 'us',
                    'wait': 5000,  # Wait 5 seconds for page to load
                    'session_number': 1  # Use session for consistency
                }
                response = requests.get('https://api.scraperapi.com/', params=payload, timeout=60)
            else:
                response = self.session.get(url, timeout=30)
            
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_text_from_selector(self, soup: BeautifulSoup, selector: str, element: BeautifulSoup = None) -> str:
        """Extract text from CSS selector"""
        try:
            target = element if element else soup
            
            # Handle multiple selectors separated by commas
            selectors = [s.strip() for s in selector.split(',')]
            
            for sel in selectors:
                try:
                    if '::text' in sel:
                        css_selector = sel.replace('::text', '')
                        elem = target.select_one(css_selector)
                        if elem:
                            return elem.get_text(strip=True)
                    elif '::attr(' in sel:
                        attr_match = re.search(r'::attr\(([^)]+)\)', sel)
                        if attr_match:
                            attr_name = attr_match.group(1)
                            css_selector = sel.split('::attr(')[0]
                            elem = target.select_one(css_selector)
                            if elem:
                                return elem.get(attr_name, "")
                    else:
                        elem = target.select_one(sel)
                        if elem:
                            return elem.get_text(strip=True)
                except Exception as e:
                    logger.debug(f"Error with selector '{sel}': {e}")
                    continue
            
            return ""
        except Exception as e:
            logger.error(f"Error extracting from selector {selector}: {e}")
            return ""
    
    def scrape_job_listings(self, html_content: str, config: Dict) -> List[Dict]:
        """Scrape job listings from a search page"""
        jobs = []
        seen_urls = set()  # Track URLs to prevent duplicates
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            selectors = config.get('selectors', {})
            
            # Find all job containers
            job_containers = soup.select(selectors.get('job_container', ''))
            logger.info(f"Found {len(job_containers)} job containers")
            
            for container in job_containers:
                job_data = {}
                
                # Extract basic job data
                for field, selector in selectors.items():
                    if field not in ['job_container', 'job_detail_selectors']:
                        # Map field names to match JobData class
                        if field == 'date_posted':
                            job_data['posted_date'] = self.extract_text_from_selector(soup, selector, container)
                        else:
                            job_data[field] = self.extract_text_from_selector(soup, selector, container)
                
                # Convert relative URLs to absolute URLs
                if job_data.get('apply_url') and job_data['apply_url'].startswith('/'):
                    base_url = config.get('start_url', '')
                    if 'wd1.myworkdayjobs.com' in base_url:
                        from urllib.parse import urlparse
                        parsed = urlparse(base_url)
                        job_data['apply_url'] = f"{parsed.scheme}://{parsed.netloc}{job_data['apply_url']}"
                    else:
                        job_data['apply_url'] = urljoin(base_url, job_data['apply_url'])
                
                # Add metadata and map URL field
                job_data['source_site'] = config.get('site_name', 'Unknown')
                job_data['scraped_at'] = datetime.utcnow().isoformat()
                
                # Map apply_url to url for JobData class
                if job_data.get('apply_url'):
                    job_data['url'] = job_data['apply_url']
                
                # Clean and validate job data - prevent duplicates
                if job_data.get('title') and job_data.get('apply_url'):
                    # Use URL as unique identifier to prevent duplicates
                    if job_data['apply_url'] not in seen_urls:
                        seen_urls.add(job_data['apply_url'])
                        jobs.append(job_data)
                    else:
                        logger.debug(f"Skipping duplicate job: {job_data['title']}")
                    
        except Exception as e:
            logger.error(f"Error scraping job listings: {e}")
            
        return jobs
    
    def scrape_job_details(self, job_url: str, config: Dict) -> Dict:
        """Scrape detailed information from individual job page"""
        try:
            # Convert relative URLs to absolute URLs
            if job_url.startswith('/'):
                base_url = config.get('start_url', '')
                if 'wd1.myworkdayjobs.com' in base_url:
                    # Extract the base domain
                    from urllib.parse import urlparse
                    parsed = urlparse(base_url)
                    job_url = f"{parsed.scheme}://{parsed.netloc}{job_url}"
                else:
                    job_url = urljoin(base_url, job_url)
            
            html_content = self.get_page_content(job_url)
            if not html_content:
                return {}
            
            soup = BeautifulSoup(html_content, 'html.parser')
            selectors = config.get('selectors', {}).get('job_detail_selectors', {})
            
            job_details = {}
            
            # Extract detailed job information
            for field, selector in selectors.items():
                job_details[field] = self.extract_text_from_selector(soup, selector)
            
            return job_details
            
        except Exception as e:
            logger.error(f"Error scraping job details from {job_url}: {e}")
            return {}
    
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
            
            # Handle JavaScript-based pagination
            if pagination.get('use_javascript', False):
                return self.handle_javascript_pagination(current_url, config)
                        
        except Exception as e:
            logger.error(f"Error getting next page URL: {e}")
            
        return None
    
    def handle_javascript_pagination(self, current_url: str, config: Dict) -> Optional[str]:
        """Handle JavaScript-based pagination (for SPAs like Workday)"""
        try:
            pagination = config.get('pagination', {})
            
            # Extract current page number from URL
            current_page = 1
            if 'page=' in current_url:
                page_match = re.search(r'page=(\d+)', current_url)
                if page_match:
                    current_page = int(page_match.group(1))
            
            # Construct next page URL
            next_page = current_page + 1
            if '?' in current_url:
                next_url = f"{current_url}&page={next_page}"
            else:
                next_url = f"{current_url}?page={next_page}"
            
            # Check if we've reached max pages
            max_pages = pagination.get('max_pages', 10)
            if next_page > max_pages:
                return None
                
            return next_url
            
        except Exception as e:
            logger.error(f"Error handling JavaScript pagination: {e}")
            return None
    
    def save_job_to_database(self, job_data: Dict):
        """Save job data to database"""
        try:
            job_data = self._sanitize_job_fields(dict(job_data))
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert job_data to JobData object
            job = JobData(**job_data)
            
            cursor.execute('''
                INSERT OR REPLACE INTO jobs 
                (url, title, company, location, description, full_description, requirements,
                 posted_date, job_type, department, experience_level, salary, benefits,
                 closing_date, work_arrangement, travel_required, eligibility, clearance,
                 physical_requirements, equal_opportunity, job_id, source_site, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job.url, job.title, job.company, job.location, job.description, job.full_description,
                job.requirements, job.posted_date, job.job_type, job.department, job.experience_level,
                job.salary, job.benefits, job.closing_date, job.work_arrangement, job.travel_required,
                job.eligibility, job.clearance, job.physical_requirements, job.equal_opportunity,
                job.job_id, job.source_site, job.scraped_at
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving job to database: {e}")
    
    def scrape_site(self, config_file: str, max_pages: int = 5, scrape_job_details: bool = True) -> List[Dict]:
        """Scrape all jobs from a site based on configuration"""
        config = self.load_config(config_file)
        if not config:
            return []
        
        all_jobs = []
        seen_urls = set()  # Track URLs across all pages to prevent duplicates
        start_url = config.get('start_url', '')
        current_url = start_url
        pages_scraped = 0
        
        logger.info(f"Starting to scrape {config.get('site_name', 'Unknown')} from {start_url}")
        
        while current_url and pages_scraped < max_pages:
            logger.info(f"Scraping page {pages_scraped + 1}: {current_url}")
            
            # Get page content
            html_content = self.get_page_content(current_url)
            if not html_content:
                break
            
            # Scrape job listings from current page
            page_jobs = self.scrape_job_listings(html_content, config)
            logger.info(f"Found {len(page_jobs)} jobs on page {pages_scraped + 1}")
            
            # Filter out duplicates across pages
            unique_page_jobs = []
            for job in page_jobs:
                if job.get('apply_url') and job['apply_url'] not in seen_urls:
                    seen_urls.add(job['apply_url'])
                    unique_page_jobs.append(job)
                else:
                    logger.debug(f"Skipping duplicate job across pages: {job.get('title', 'Unknown')}")
            
            logger.info(f"Added {len(unique_page_jobs)} unique jobs from page {pages_scraped + 1}")
            
            # Scrape detailed information for each job
            if scrape_job_details:
                for i, job in enumerate(unique_page_jobs):
                    if job.get('apply_url'):
                        logger.info(f"Scraping job details {i+1}/{len(unique_page_jobs)}: {job.get('title', 'Unknown')}")
                        job_details = self.scrape_job_details(job['apply_url'], config)
                        job.update(job_details)
                        
                        # Save to database
                        self.save_job_to_database(job)
                        
                        # Optional delay between job detail requests (now defaults to 0)
                        jd_delay = config.get('scraping_options', {}).get('delay_between_job_details', 0) or 0
                        if jd_delay > 0:
                            time.sleep(jd_delay)
            
            # Sanitize before returning/collecting to avoid stray keys in output
            for j in unique_page_jobs:
                sanitized = self._sanitize_job_fields(j)
                all_jobs.append(sanitized)
            
            # Get next page URL
            current_url = self.get_next_page_url(html_content, config, current_url)
            pages_scraped += 1
            
            # Optional delay between pages (now defaults to 0)
            page_delay = config.get('scraping_options', {}).get('delay_between_requests', 0) or 0
            if page_delay > 0:
                time.sleep(page_delay)
        
        logger.info(f"Completed scraping {config.get('site_name', 'Unknown')}. Total jobs: {len(all_jobs)}")
        return all_jobs
    
    def scrape_multiple_sites(self, config_files: List[str], max_pages_per_site: int = 5) -> Dict[str, List[Dict]]:
        """Scrape multiple sites and return results organized by site"""
        results = {}
        
        for config_file in config_files:
            try:
                logger.info(f"Starting to scrape {config_file}")
                site_jobs = self.scrape_site(config_file, max_pages_per_site)
                results[config_file] = site_jobs
                logger.info(f"Completed {config_file}: {len(site_jobs)} jobs")
            except Exception as e:
                logger.error(f"Error scraping {config_file}: {e}")
                results[config_file] = []
        
        return results
    
    def export_results(self, results: Dict[str, List[Dict]], format: str = 'json') -> str:
        """Export results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == 'json':
            filename = f"job_results_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        elif format.lower() == 'csv':
            import pandas as pd
            filename = f"job_results_{timestamp}.csv"
            
            # Flatten results
            all_jobs = []
            for site, jobs in results.items():
                for job in jobs:
                    job['source_site'] = site
                    all_jobs.append(job)
            
            df = pd.DataFrame(all_jobs)
            df.to_csv(filename, index=False, encoding='utf-8')
        
        logger.info(f"Results exported to {filename}")
        return filename

def main():
    """Main function for testing"""
    scraper = UniversalJobScraper()
    
    # Test with 3M config
    config_files = ['3m.yaml']
    
    print("Starting universal job scraper...")
    results = scraper.scrape_multiple_sites(config_files, max_pages_per_site=3)
    
    # Export results
    export_file = scraper.export_results(results, 'json')
    
    print(f"\nScraping completed!")
    print(f"Results exported to: {export_file}")
    
    # Print summary
    for site, jobs in results.items():
        print(f"{site}: {len(jobs)} jobs")

if __name__ == "__main__":
    main()
