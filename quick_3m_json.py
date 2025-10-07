#!/usr/bin/env python3
"""
Run the proven 1-page 3M scrape (with details) and save results to JSON.
"""

from universal_job_scraper import UniversalJobScraper
from datetime import datetime
import json


def main():
    scraper = UniversalJobScraper()
    print("no-wait test (1 page, with details)")
    jobs = scraper.scrape_site('3m.yaml', max_pages=1, scrape_job_details=True)
    print("done, jobs:", len(jobs))

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out = f"3m_test_fixed_{ts}.json"
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    print("saved:", out)


if __name__ == '__main__':
    main()


