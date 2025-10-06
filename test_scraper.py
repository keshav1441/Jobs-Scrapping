#!/usr/bin/env python3
"""
Test script for the job scraping engine
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.scraper_engine import JobScraperEngine

load_dotenv()

def test_caleres_scraping():
    """Test scraping Caleres jobs using ScraperAPI"""
    print("Testing Caleres job scraping...")
    
    # Initialize the scraper engine
    engine = JobScraperEngine()
    
    # Get ScraperAPI key from environment
    scraperapi_key = os.getenv('SCRAPERAPI_KEY', 'a6d4e94d7a28b565f7c83839f54926a5')
    
    # Test with Caleres config
    try:
        jobs = engine.scrape_site(
            'caleres.yaml',
            max_pages=2,
            use_scraperapi=True,
            scraperapi_key=scraperapi_key
        )
        
        print(f"Found {len(jobs)} jobs from Caleres")
        
        if jobs:
            print("\nFirst job sample:")
            print(json.dumps(jobs[0], indent=2))
            
            # Save to file for inspection
            with open('caleres_test_results.json', 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to: caleres_test_results.json")
        else:
            print("No jobs found. This might be due to:")
            print("1. Incorrect CSS selectors in the config")
            print("2. Website structure changes")
            print("3. Anti-bot protection")
            print("4. Network issues")
            
    except Exception as e:
        print(f"Error during scraping: {e}")

def test_config_loading():
    """Test loading configuration files"""
    print("\nTesting configuration loading...")
    
    engine = JobScraperEngine()
    
    config_files = ['caleres.yaml', 'indeed.yaml', 'linkedin.yaml']
    
    for config_file in config_files:
        try:
            config = engine.load_config(config_file)
            if config:
                print(f"✓ {config_file}: {config.get('site_name', 'Unknown')}")
            else:
                print(f"✗ {config_file}: Failed to load")
        except Exception as e:
            print(f"✗ {config_file}: Error - {e}")

def test_single_page_scraping():
    """Test scraping a single page"""
    print("\nTesting single page scraping...")
    
    engine = JobScraperEngine()
    scraperapi_key = os.getenv('SCRAPERAPI_KEY', 'a6d4e94d7a28b565f7c83839f54926a5')
    
    # Test the specific URL provided by user
    test_url = "https://jobs.dayforcehcm.com/en-US/caleres/calerescorporate"
    
    print(f"Testing URL: {test_url}")
    
    # Get page content
    html_content = engine.get_page_content(test_url, use_scraperapi=True, scraperapi_key=scraperapi_key)
    
    if html_content:
        print(f"✓ Successfully fetched page content ({len(html_content)} characters)")
        
        # Try to scrape jobs from the page
        config = engine.load_config('caleres.yaml')
        if config:
            jobs = engine.scrape_jobs_from_page(html_content, config)
            print(f"✓ Found {len(jobs)} jobs on the page")
            
            if jobs:
                print("\nSample job data:")
                print(json.dumps(jobs[0], indent=2))
        else:
            print("✗ Failed to load Caleres config")
    else:
        print("✗ Failed to fetch page content")

if __name__ == "__main__":
    print("Job Scraping Engine Test Suite")
    print("=" * 50)
    
    # Test configuration loading
    test_config_loading()
    
    # Test single page scraping
    test_single_page_scraping()
    
    # Test full site scraping
    test_caleres_scraping()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")
