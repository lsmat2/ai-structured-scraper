# ai-structured-scraper

A Python project for fetching, cleaning, and structuring place information from the Google Places API, LLM models, and interaction with a backend service. It provides scripts to gather raw data, normalize it into structured JSON, use a prompt to query LLM to scrape and structure data collected from web content given a base url, and query it with a backend system through a simple command-line interface.

## Project Overview

* **`fetch_nearby_places.py`**: Retrieves raw place data from the Google Places NearbySearch API and saves results to JSON.
* **`clean_nearby_places.py`**: Loads raw data, handles cleaning/structuring, and prepares consistent objects. Includes error handling for Google Places API issues.
* **`backend_CLI.py`**: Provides a command-line interface for fetching structured place data from the backend by ID.
* **`config.py`**: Holds various config variables for other features.
* **`ai_data_cleaner.py`**: Given placedata and a website base url, scrapes text data and uses LLM to structure place data, promo data, event data, menu data, and more

## Requirements

* Python 3.9+
* Dependencies listed in `requirements.txt` (common: `requests`, `python-dotenv`)
* Environment variables:

  * `GOOGLE_API_KEY` (for Google Places API access: requesting initial bar/restaurant data from google)
  * `OPENAI_API_KEY` (for openAI API integration: sanitizing old data and structuring new promo/event/menu data from website)
  * `BACKEND_API_URL` (for CLI to connect to backend service and update places)

## Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-structured-scraper.git
cd ai-structured-scraper

# Install dependencies
Create a venv

# Configure environment variables
cp .env.example .env
# edit .env to include keys for any of the desired features
```

## Usage

### 1. Fetch raw place data

```bash
python fetch_nearby_places.py --location "41.8781,-87.6298" --radius 1000 --output data/raw_places.json
```

### 2. Clean and structure the data

```bash
python clean_nearby_places.py data/raw_places.json data/clean_places.json
```

### 3. Query backend with CLI

```bash
python backend_CLI.py 12345
```

*(where `12345` is a place ID in the backend database)*

## Improvements (future work)

* Expand CLI functionality choose to create vs update vs delete.
* Expand CLI functionality to use only google api for place data vs web scraping and llm structuring
* Add timestamps to requests for freshness tracking.

## License

This project is provided as-is for internal and research purposes, though all help is welcome. Once this works for my purposes I intend to generalize it more such that it can be used to leverage inputting small amounts of incredibly unstructured text data from web content given certain prompting suggestions, outputting a strictly defined JSON or other form of output.
