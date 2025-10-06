#!/usr/bin/env python3
"""
Demo script to show the job scraping engine functionality
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.scraper_engine import JobScraperEngine
from config.database import create_tables, SessionLocal, Job

def create_sample_jobs():
    """Create sample jobs for demonstration"""
    db = SessionLocal()
    try:
        # Clear existing jobs
        db.query(Job).delete()
        
        # Create sample jobs
        sample_jobs = [
            {
                'title': 'Senior Software Engineer',
                'company': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'description': 'We are looking for a senior software engineer to join our team...',
                'apply_url': 'https://techcorp.com/jobs/senior-engineer',
                'source_site': 'caleres',
                'salary': '$120,000 - $150,000',
                'job_type': 'Full-time',
                'experience_level': 'Senior'
            },
            {
                'title': 'Frontend Developer',
                'company': 'StartupXYZ',
                'location': 'Remote',
                'description': 'Join our fast-growing startup as a frontend developer...',
                'apply_url': 'https://startupxyz.com/careers/frontend',
                'source_site': 'indeed',
                'salary': '$80,000 - $100,000',
                'job_type': 'Full-time',
                'experience_level': 'Mid-level'
            },
            {
                'title': 'Data Scientist',
                'company': 'DataCorp',
                'location': 'New York, NY',
                'description': 'We need a data scientist to help us build ML models...',
                'apply_url': 'https://datacorp.com/jobs/data-scientist',
                'source_site': 'linkedin',
                'salary': '$100,000 - $130,000',
                'job_type': 'Full-time',
                'experience_level': 'Senior'
            },
            {
                'title': 'Product Manager',
                'company': 'ProductCo',
                'location': 'Austin, TX',
                'description': 'Lead product development for our flagship application...',
                'apply_url': 'https://productco.com/careers/pm',
                'source_site': 'caleres',
                'salary': '$110,000 - $140,000',
                'job_type': 'Full-time',
                'experience_level': 'Senior'
            },
            {
                'title': 'UX Designer',
                'company': 'DesignStudio',
                'location': 'Seattle, WA',
                'description': 'Create beautiful and intuitive user experiences...',
                'apply_url': 'https://designstudio.com/jobs/ux-designer',
                'source_site': 'indeed',
                'salary': '$70,000 - $90,000',
                'job_type': 'Full-time',
                'experience_level': 'Mid-level'
            }
        ]
        
        for job_data in sample_jobs:
            job = Job(**job_data)
            db.add(job)
        
        db.commit()
        print(f"Created {len(sample_jobs)} sample jobs")
        
    except Exception as e:
        print(f"Error creating sample jobs: {e}")
        db.rollback()
    finally:
        db.close()

def demo_scraper_engine():
    """Demonstrate the scraper engine functionality"""
    print("Job Scraping Engine Demo")
    print("=" * 50)
    
    # Initialize the engine
    engine = JobScraperEngine()
    
    # Show available configurations
    print("\n1. Available Configuration Files:")
    config_files = [f for f in os.listdir('configs/') if f.endswith('.yaml')]
    for config_file in config_files:
        config = engine.load_config(config_file)
        print(f"   - {config_file}: {config.get('site_name', 'Unknown')}")
    
    # Show configuration structure
    print("\n2. Configuration Structure Example:")
    if config_files:
        config = engine.load_config(config_files[0])
        print(json.dumps(config, indent=2))
    
    # Show how to use the engine
    print("\n3. How to Use the Engine:")
    print("   # Scrape a specific site")
    print("   python main.py --config caleres.yaml --save-to-db")
    print("   ")
    print("   # Scrape all sites")
    print("   python main.py --all --save-to-db --max-pages 5")
    print("   ")
    print("   # Use ScraperAPI")
    print("   python main.py --config caleres.yaml --use-scraperapi --save-to-db")
    print("   ")
    print("   # Save to JSON file")
    print("   python main.py --config caleres.yaml --output results.json")

def demo_web_interface():
    """Show how to start the web interface"""
    print("\n4. Web Interface:")
    print("   # Start the web dashboard")
    print("   python app.py")
    print("   ")
    print("   # Then open your browser to: http://localhost:5000")
    print("   ")
    print("   Features:")
    print("   - View all scraped jobs")
    print("   - Search and filter jobs")
    print("   - Statistics dashboard")
    print("   - Responsive design")

def main():
    """Main demo function"""
    # Create database tables
    create_tables()
    
    # Create sample data
    create_sample_jobs()
    
    # Show engine demo
    demo_scraper_engine()
    
    # Show web interface info
    demo_web_interface()
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print("You can now:")
    print("1. Run 'python app.py' to start the web interface")
    print("2. Run 'python main.py --config caleres.yaml --save-to-db' to test scraping")
    print("3. Check the README.md for more detailed instructions")

if __name__ == "__main__":
    main()
