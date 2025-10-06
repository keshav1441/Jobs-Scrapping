# Job Scraping Engine

A configurable job scraping engine that can scrape jobs from multiple websites using YAML configuration files. The system includes a web dashboard to view and filter scraped jobs.

## Features

- **Configurable Scraping**: Use YAML files to configure scraping for different job sites
- **Multiple Data Sources**: Support for various job portals (Indeed, LinkedIn, company sites, etc.)
- **Database Storage**: SQLite database to store scraped jobs
- **Web Dashboard**: Beautiful web interface to view and filter jobs
- **ScraperAPI Integration**: Optional integration with ScraperAPI for better scraping success
- **Pagination Support**: Automatic handling of multi-page results
- **Real-time Filtering**: Search and filter jobs by company, location, source, etc.

## Project Structure

```
├── configs/                 # YAML configuration files for different sites
│   ├── caleres.yaml
│   ├── indeed.yaml
│   └── linkedin.yaml
├── engine/                  # Core scraping engine
│   └── scraper_engine.py
├── config/                  # Database configuration
│   └── database.py
├── templates/               # Web UI templates
│   └── index.html
├── main.py                  # Main scraping script
├── app.py                   # Flask web application
├── requirements.txt         # Python dependencies
└── README.md
```

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional):
   ```bash
   cp env.example .env
   # Edit .env with your ScraperAPI key if you have one
   ```

## Usage

### 1. Running the Scraper

**Scrape a specific site**:
```bash
python main.py --config caleres.yaml --save-to-db
```

**Scrape all configured sites**:
```bash
python main.py --all --save-to-db --max-pages 5
```

**Use ScraperAPI** (recommended for better success rates):
```bash
python main.py --config caleres.yaml --use-scraperapi --save-to-db
```

**Save results to JSON file**:
```bash
python main.py --config caleres.yaml --output results.json
```

### 2. Running the Web Dashboard

```bash
python app.py
```

Then open your browser to `http://localhost:5000`

### 3. Command Line Options

- `--config, -c`: Specific config file to run
- `--all, -a`: Run all config files
- `--max-pages, -p`: Maximum pages to scrape per site (default: 5)
- `--output, -o`: Output file for JSON results
- `--use-scraperapi`: Use ScraperAPI for scraping
- `--save-to-db`: Save results to database

## Configuration Files

Each job site requires a YAML configuration file in the `configs/` directory. Here's the structure:

```yaml
# Configuration for Jobs Portal
site_name: "Portal Name"
start_url: "https://example.com/jobs"

# Selectors to find the data on the page
selectors:
  job_container: ".job-listing-card"  # Main container for job posts
  title: ".job-title::text"          # Job title
  company: ".company-name a::text"   # Company name
  location: ".location-pin span::text" # Job location
  date_posted: ".date-posted-class::attr(datetime)" # Date posted
  apply_url: "a.apply-button::attr(href)" # Apply URL
  description: ".job-description::text" # Job description
  salary: ".salary::text" # Salary information

# Pagination configuration
pagination:
  next_page_selector: "a.pagination-next::attr(href)"

# Additional options
scraping_options:
  use_scraperapi: true
  delay_between_requests: 2
  max_pages: 10
```

### Selector Syntax

- `::text` - Extract text content from element
- `::attr(attribute_name)` - Extract attribute value (e.g., `href`, `datetime`)
- Regular CSS selectors work for element selection

## Example: Caleres Scraping

The project includes a configuration for Caleres jobs portal. To test it:

```bash
# Using ScraperAPI (recommended)
python main.py --config caleres.yaml --use-scraperapi --save-to-db

# View results in web dashboard
python app.py
```

## Web Dashboard Features

- **Statistics**: View total jobs, recent jobs, sources, and companies
- **Search**: Search jobs by title or description
- **Filters**: Filter by company, location, and source
- **Pagination**: Navigate through large result sets
- **Responsive Design**: Works on desktop and mobile devices

## Database Schema

The system uses SQLite database with the following job table structure:

- `id`: Primary key
- `title`: Job title
- `company`: Company name
- `location`: Job location
- `description`: Job description
- `apply_url`: URL to apply for the job
- `date_posted`: When the job was posted
- `source_site`: Which site the job was scraped from
- `scraped_at`: When the job was scraped
- `is_active`: Whether the job is still active
- `salary`: Salary information
- `job_type`: Type of job (full-time, part-time, etc.)
- `experience_level`: Required experience level

## Adding New Job Sites

1. **Create a new YAML config file** in the `configs/` directory
2. **Inspect the target website** to find the correct CSS selectors
3. **Test the configuration** with a small number of pages
4. **Add the config file** to your scraping runs

## Troubleshooting

### Common Issues

1. **No jobs found**: Check if the CSS selectors in your config file are correct
2. **Scraping blocked**: Use ScraperAPI or add delays between requests
3. **Database errors**: Ensure the database file has write permissions

### Debug Mode

Run with verbose logging:
```bash
python main.py --config your_config.yaml --save-to-db
```

## Contributing

1. Add new job site configurations to the `configs/` directory
2. Test configurations thoroughly before submitting
3. Follow the existing YAML structure and naming conventions

## License

This project is for educational and POC purposes. Please respect website terms of service and robots.txt files when scraping.
