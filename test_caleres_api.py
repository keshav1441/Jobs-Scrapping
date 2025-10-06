#!/usr/bin/env python3
"""
Test script specifically for Caleres using the provided ScraperAPI key
"""

import requests
import json
from bs4 import BeautifulSoup

def test_caleres_with_scraperapi():
    """Test Caleres scraping with the provided ScraperAPI key"""
    print("Testing Caleres with ScraperAPI...")
    
    # The provided ScraperAPI key and URL
    api_key = 'a6d4e94d7a28b565f7c83839f54926a5'
    url = 'https://jobs.dayforcehcm.com/en-US/caleres/calerescorporate'
    
    payload = {
        'api_key': api_key,
        'url': url
    }
    
    try:
        print(f"Fetching: {url}")
        response = requests.get('https://api.scraperapi.com/', params=payload, timeout=30)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Response length: {len(response.text)} characters")
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for any job-related content
        print("\n=== Analyzing page content ===")
        
        # Check for any text that might indicate jobs
        page_text = soup.get_text().lower()
        job_keywords = ['engineer', 'manager', 'analyst', 'developer', 'position', 'role', 'career', 'job']
        
        found_keywords = []
        for keyword in job_keywords:
            if keyword in page_text:
                found_keywords.append(keyword)
        
        print(f"Found job-related keywords: {found_keywords}")
        
        # Look for any forms or search elements
        forms = soup.find_all('form')
        inputs = soup.find_all('input')
        buttons = soup.find_all('button')
        
        print(f"Found {len(forms)} forms, {len(inputs)} inputs, {len(buttons)} buttons")
        
        # Look for any JavaScript that might load content
        scripts = soup.find_all('script')
        print(f"Found {len(scripts)} script elements")
        
        # Check for any data attributes
        elements_with_data = soup.find_all(attrs={'data-testid': True})
        print(f"Found {len(elements_with_data)} elements with data-testid")
        
        # Save the response for inspection
        with open('caleres_scraperapi_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\nResponse saved to: caleres_scraperapi_response.html")
        
        # Try to find any job listings using common patterns
        print("\n=== Looking for job listings ===")
        
        # Common job listing selectors
        job_selectors = [
            'div[class*="job"]',
            'div[class*="position"]',
            'div[class*="listing"]',
            'div[class*="result"]',
            'article',
            '.search-result',
            '[data-testid*="job"]',
            '[data-testid*="position"]'
        ]
        
        for selector in job_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    text_preview = elem.get_text().strip()[:100]
                    if text_preview:
                        print(f"  {i+1}. {text_preview}...")
        
        # Check if this is a single-page application
        if 'next' in response.text.lower() or 'react' in response.text.lower():
            print("\nThis appears to be a single-page application (SPA)")
            print("Jobs are likely loaded dynamically via JavaScript/AJAX")
            print("Consider using Selenium or finding API endpoints")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    print("Caleres ScraperAPI Test")
    print("=" * 40)
    
    success = test_caleres_with_scraperapi()
    
    if success:
        print("\n" + "=" * 40)
        print("Test completed successfully!")
        print("Check caleres_scraperapi_response.html for the full response")
    else:
        print("\n" + "=" * 40)
        print("Test failed. Check the error message above.")

if __name__ == "__main__":
    main()
