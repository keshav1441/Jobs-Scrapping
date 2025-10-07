#!/usr/bin/env python3
"""
Simple script to run the 3M job scraper
"""

from universal_job_scraper import UniversalJobScraper
import json
import time

def main():
    """Run the 3M scraper"""
    print("3M Job Scraper")
    print("=" * 40)
    
    # Initialize scraper
    scraper = UniversalJobScraper()
    
    # Scrape 3M jobs (use proven working approach: 1 page, with details)
    print("Starting to scrape 3M jobs (test-fixed approach)...")
    start_time = time.time()
    
    jobs = scraper.scrape_site('3m.yaml', max_pages=1, scrape_job_details=True)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nScraping completed in {duration:.2f} seconds")
    print(f"Total jobs found: {len(jobs)}")
    
    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"3m_jobs_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to: {filename}")
    print(f"Jobs also saved to database: {scraper.db_path}")
    
    # Show sample results
    if jobs:
        print(f"\nSample jobs:")
        for i, job in enumerate(jobs[:5], 1):
            print(f"{i}. {job.get('title', 'N/A')}")
            print(f"   URL: {job.get('apply_url', 'N/A')}")
            print()

if __name__ == "__main__":
    main()

