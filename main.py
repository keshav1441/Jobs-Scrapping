#!/usr/bin/env python3
"""
Main script to run the job scraping engine
"""

import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.scraper_engine import JobScraperEngine
from config.database import create_tables, SessionLocal, Job

load_dotenv()

def save_jobs_to_database(jobs_data: list, source_site: str):
    """Save scraped jobs to database"""
    db = SessionLocal()
    try:
        saved_count = 0
        for job_data in jobs_data:
            # Check if job already exists (based on title, company, and source)
            existing_job = db.query(Job).filter(
                Job.title == job_data.get('title', ''),
                Job.company == job_data.get('company', ''),
                Job.source_site == source_site
            ).first()
            
            if not existing_job:
                job = Job(
                    title=job_data.get('title', ''),
                    company=job_data.get('company', ''),
                    location=job_data.get('location', ''),
                    description=job_data.get('description', ''),
                    apply_url=job_data.get('apply_url', ''),
                    source_site=source_site,
                    salary=job_data.get('salary', ''),
                    job_type=job_data.get('job_type', ''),
                    experience_level=job_data.get('experience_level', '')
                )
                db.add(job)
                saved_count += 1
        
        db.commit()
        print(f"Saved {saved_count} new jobs from {source_site}")
        
    except Exception as e:
        print(f"Error saving jobs to database: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description='Job Scraping Engine')
    parser.add_argument('--config', '-c', help='Specific config file to run (e.g., caleres.yaml)')
    parser.add_argument('--all', '-a', action='store_true', help='Run all config files')
    parser.add_argument('--max-pages', '-p', type=int, default=5, help='Maximum pages to scrape per site')
    parser.add_argument('--output', '-o', help='Output file for JSON results')
    parser.add_argument('--use-scraperapi', action='store_true', help='Use ScraperAPI for scraping')
    parser.add_argument('--save-to-db', action='store_true', help='Save results to database')
    
    args = parser.parse_args()
    
    # Initialize the scraper engine
    engine = JobScraperEngine()
    
    # Create database tables if saving to DB
    if args.save_to_db:
        create_tables()
    
    # Get ScraperAPI key from environment
    scraperapi_key = os.getenv('SCRAPERAPI_KEY')
    
    if args.config:
        # Run specific config
        config_files = [args.config]
    elif args.all:
        # Run all config files
        config_files = [f for f in os.listdir('configs/') if f.endswith('.yaml')]
    else:
        # Default: run caleres config
        config_files = ['caleres.yaml']
    
    print(f"Starting job scraping for {len(config_files)} site(s)...")
    print(f"Config files: {config_files}")
    
    all_results = {}
    total_jobs = 0
    
    for config_file in config_files:
        print(f"\n{'='*50}")
        print(f"Scraping: {config_file}")
        print(f"{'='*50}")
        
        try:
            jobs = engine.scrape_site(
                config_file, 
                max_pages=args.max_pages,
                use_scraperapi=args.use_scraperapi,
                scraperapi_key=scraperapi_key
            )
            
            all_results[config_file] = jobs
            total_jobs += len(jobs)
            
            print(f"Found {len(jobs)} jobs from {config_file}")
            
            # Save to database if requested
            if args.save_to_db and jobs:
                save_jobs_to_database(jobs, config_file.replace('.yaml', ''))
            
        except Exception as e:
            print(f"Error scraping {config_file}: {e}")
            all_results[config_file] = []
    
    print(f"\n{'='*50}")
    print(f"SCRAPING COMPLETE")
    print(f"{'='*50}")
    print(f"Total jobs found: {total_jobs}")
    
    # Save to JSON file if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {args.output}")
    
    # Print summary
    for config_file, jobs in all_results.items():
        print(f"{config_file}: {len(jobs)} jobs")

if __name__ == "__main__":
    main()
