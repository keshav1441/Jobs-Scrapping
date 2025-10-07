# Job Scraping System

A universal job scraper that can scrape jobs from multiple sites using YAML configurations.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   - **REQUIRED:** Edit `config.env` and replace the placeholder with your actual ScraperAPI key:
   ```bash
   # Edit config.env and replace with your actual ScraperAPI key
   SCRAPERAPI_KEY=your_actual_scraperapi_key_here
   ```
   - **⚠️ IMPORTANT:** The scraper will fail to start without a valid ScraperAPI key

3. **Get ScraperAPI Key:**
   - Sign up at [ScraperAPI](https://www.scraperapi.com/)
   - Get your API key from the dashboard
   - Replace `your_scraperapi_key_here` in `config.env`

## Usage

### 3M Jobs Scraper
```bash
python run_3m_scraper.py
```

### Complete 3M Scraper (All Jobs with Details)
```bash
python scrape_all_3m_jobs.py
```

### Universal Scraper
```bash
python -c "from universal_job_scraper import UniversalJobScraper; scraper = UniversalJobScraper(); jobs = scraper.scrape_site('3m.yaml', max_pages=1, scrape_job_details=True)"
```

## Configuration Files

- `configs/3m.yaml` - 3M Workday configuration
- `configs/carlisle_companies.yaml` - Carlisle Companies configuration

## Output

- JSON files with job data
- SQLite database (if enabled)
- Log files for debugging

## Features

- ✅ ScraperAPI integration with IP rotation
- ✅ JavaScript rendering support
- ✅ Configurable delays and retries
- ✅ Complete job details scraping
- ✅ Multiple job site support
- ✅ Environment variable configuration