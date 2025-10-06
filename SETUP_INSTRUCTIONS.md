# Job Scraping Engine - Setup Instructions

## Quick Start

1. **Install Dependencies**:
   ```bash
   py -m pip install -r requirements.txt
   ```

2. **Run Demo with Sample Data**:
   ```bash
   py demo.py
   ```

3. **Start Web Dashboard**:
   ```bash
   py app.py
   ```
   Then open: http://localhost:5000

4. **Test Scraping**:
   ```bash
   # Test with ScraperAPI (using provided key)
   py test_caleres_api.py
   
   # Test the full engine
   py main.py --config caleres.yaml --use-scraperapi --save-to-db
   ```

## Project Structure

```
├── configs/                 # YAML configuration files
│   ├── caleres.yaml        # Caleres jobs portal
│   ├── indeed.yaml         # Indeed.com
│   ├── linkedin.yaml       # LinkedIn jobs
│   └── example_jobs.yaml   # Example template
├── engine/                  # Core scraping engine
│   └── scraper_engine.py
├── config/                  # Database configuration
│   └── database.py
├── templates/               # Web UI
│   └── index.html
├── main.py                  # Main scraping script
├── app.py                   # Flask web app
├── demo.py                  # Demo with sample data
└── test_caleres_api.py     # Test Caleres specifically
```

## Key Features

✅ **Configurable Scraping**: YAML files define how to scrape each site
✅ **Multiple Data Sources**: Support for various job portals
✅ **Database Storage**: SQLite database for job storage
✅ **Web Dashboard**: Beautiful interface to view and filter jobs
✅ **ScraperAPI Integration**: Uses provided API key for better success
✅ **Sample Data**: Demo includes 5 sample jobs for testing

## Caleres Scraping Results

The Caleres jobs portal (https://jobs.dayforcehcm.com/en-US/caleres/calerescorporate) is a **single-page application** that loads jobs dynamically via JavaScript. 

**Current Status**:
- ✅ ScraperAPI connection working (using provided key: `a6d4e94d7a28b565f7c83839f54926a5`)
- ✅ Successfully fetches page content (527,504 characters)
- ⚠️ Jobs are loaded dynamically via AJAX/JavaScript
- 💡 **Recommendation**: Use Selenium WebDriver for dynamic content or find API endpoints

## Next Steps for Production

1. **For Dynamic Sites**: Add Selenium WebDriver support
2. **API Discovery**: Find and use direct API endpoints
3. **More Sites**: Add configurations for other job portals
4. **Scheduling**: Set up automated scraping schedules
5. **Filtering**: Add n8n or similar workflow automation

## Configuration Example

```yaml
# configs/your_site.yaml
site_name: "Your Job Site"
start_url: "https://yoursite.com/jobs"

selectors:
  job_container: ".job-listing"
  title: ".job-title::text"
  company: ".company-name::text"
  location: ".location::text"
  apply_url: "a.apply-button::attr(href)"

pagination:
  next_page_selector: "a.next-page::attr(href)"
```

## Web Dashboard Features

- 📊 Statistics: Total jobs, recent jobs, sources, companies
- 🔍 Search: Full-text search across job titles and descriptions
- 🏢 Filter: By company, location, and source
- 📄 Pagination: Navigate through large result sets
- 📱 Responsive: Works on desktop and mobile

## Testing Commands

```bash
# Test configuration loading
py test_scraper.py

# Test Caleres with ScraperAPI
py test_caleres_api.py

# Run demo with sample data
py demo.py

# Start web interface
py app.py

# Scrape specific site
py main.py --config caleres.yaml --use-scraperapi --save-to-db

# Scrape all sites
py main.py --all --save-to-db --max-pages 5
```

## Environment Variables

Create a `.env` file (optional):
```
DATABASE_URL=sqlite:///jobs.db
SCRAPERAPI_KEY=your_scraperapi_key_here
```

The system works with the provided ScraperAPI key without additional configuration.
