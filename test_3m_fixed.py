#!/usr/bin/env python3
"""
Test the fixed 3M scraper with deduplication and improved selectors
"""

from universal_job_scraper import UniversalJobScraper
import json
import time


def test_3m_scraper():
    print("Testing Fixed 3M Scraper")
    print("=" * 50)

    try:
        scraper = UniversalJobScraper()
    except ValueError as e:
        print(f"ERROR: {e}")
        return

    print("Starting 3M scraping test...")
    start_time = time.time()

    jobs = scraper.scrape_site('3m.yaml', max_pages=1, scrape_job_details=True)

    end_time = time.time()
    duration = end_time - start_time

    print(f"\nTest completed in {duration:.2f} seconds")
    print(f"Total jobs found: {len(jobs)}")

    if jobs:
        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"3m_test_fixed_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)

        print(f"Results saved to: {filename}")
    else:
        print("No jobs found - selectors still need work")


if __name__ == "__main__":
    test_3m_scraper()

 