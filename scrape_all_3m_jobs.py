#!/usr/bin/env python3
"""
Complete 3M Job Scraper - Scrapes all pages and all job details
"""

from universal_job_scraper import UniversalJobScraper
import json
import time
from datetime import datetime

def scrape_all_3m_jobs():
    print("=" * 60)
    print("3M COMPLETE JOB SCRAPER")
    print("=" * 60)
    print("This will scrape ALL 3M jobs with complete details")
    print("Estimated time: 2-3 hours for 690+ jobs")
    print("=" * 60)
    
    start_time = time.time()
    
    # Initialize scraper
    scraper = UniversalJobScraper()
    
    print(f"Starting comprehensive scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Configuration:")
    print("- Max pages: 50")
    print("- Scrape job details: True")
    print("- Delay between requests: 5 seconds")
    print("- Delay between job details: 3 seconds")
    print("- Using ScraperAPI with JavaScript rendering")
    print()
    
    # Start scraping
    jobs = scraper.scrape_site('3m.yaml', max_pages=50, scrape_job_details=True)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{'='*60}")
    print("SCRAPING COMPLETED!")
    print(f"{'='*60}")
    print(f"Total jobs found: {len(jobs)}")
    print(f"Total time: {duration/60:.1f} minutes")
    print(f"Average time per job: {duration/len(jobs):.1f} seconds" if jobs else "No jobs found")
    
    if jobs:
        # Save complete results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'3m_complete_jobs_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        print(f"Complete results saved to: {filename}")
        
        # Show statistics
        print(f"\nJob Statistics:")
        print(f"- Total jobs: {len(jobs)}")
        
        # Count jobs with details
        jobs_with_details = sum(1 for job in jobs if job.get('full_description'))
        print(f"- Jobs with full descriptions: {jobs_with_details}")
        
        # Count unique companies
        companies = set(job.get('company', '') for job in jobs if job.get('company'))
        print(f"- Unique companies: {len(companies)}")
        
        # Count unique locations
        locations = set(job.get('location', '') for job in jobs if job.get('location'))
        print(f"- Unique locations: {len(locations)}")
        
        # Show sample job
        print(f"\nSample job with complete details:")
        if jobs:
            job = jobs[0]
            print(f"Title: {job.get('title', 'N/A')}")
            print(f"Company: {job.get('company', 'N/A')}")
            print(f"Location: {job.get('location', 'N/A')}")
            print(f"Job Type: {job.get('job_type', 'N/A')}")
            print(f"Salary: {job.get('salary', 'N/A')}")
            print(f"Description: {job.get('full_description', 'N/A')[:200]}...")
            print(f"Requirements: {job.get('requirements', 'N/A')[:200]}...")
            print(f"URL: {job.get('apply_url', 'N/A')}")
    else:
        print("No jobs found. Check configuration and network connection.")

if __name__ == "__main__":
    scrape_all_3m_jobs()
