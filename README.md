# ai-structured-scraper

A comprehensive Python project for fetching, cleaning, and structuring place information from multiple sources including Google Places API, web scraping, and LLM processing. The system provides end-to-end workflow from raw data collection to structured output and backend integration.

## Project Overview

* **`fetch_nearby_places.py`**: Fetches raw place data from Google Places NearbySearch API (NEW) using the PlacesFetcher class. Requires latitude/longitude coordinates.
* **`clean_nearby_places.py`**: Processes and normalizes raw Google Places data into backend-compatible format. Handles missing fields and data validation.
* **`ai_data_cleaner.py`**: Advanced web scraper and LLM processor. Takes place data with website URLs, scrapes content from multiple pages, and uses OpenAI to extract structured data including promotions, events, menus, and business details.
* **`ai_schema_config.py`**: Defines Pydantic models for structured data extraction including PlaceDataExtraction, PromotionData, EventData, MenuItem, and DailyHours schemas.
* **`BackendClient.py`**: Exportable class providing complete backend API integration with methods for CRUD operations on places and promotions.
* **`backend_CLI.py`**: Interactive command-line interface for backend operations including processing existing places, posting new data, and handling both nearby search and AI-cleaned data.
* **`config.py`**: Configuration constants for Google Places API field masks and included place types.

## Requirements

* Python 3.9+
* Required dependencies:
  * `requests` - HTTP requests for APIs and web scraping
  * `python-dotenv` - Environment variable management
  * `openai` - OpenAI API integration for LLM processing
  * `beautifulsoup4` - HTML parsing for web scraping
  * `pydantic` - Data validation and schema definition
* Environment variables:

  * `GOOGLE_PLACES_API_KEY` (for Google Places API access)
  * `OPENAI_API_KEY` (for OpenAI API integration and structured data extraction)
  * `BACKEND_API_URL` (for backend service integration)

## Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-structured-scraper.git
cd ai-structured-scraper

# Install dependencies (recommended: create virtual environment first)
python3 -m venv venv/
source venv/bin/activate
python -m pip install package-name

# Configure environment variables
cp .env.example .env
# edit .env to include keys for any of the desired features
```

## Usage

### 1. Fetch raw place data from Google Places API

```bash
python fetch_nearby_places.py <latitude> <longitude>
```

Example:
```bash
python fetch_nearby_places.py 41.8781 -87.6298  # Chicago coordinates
```

This saves raw data to `output_nearbySearch/` directory.

### 2. Clean and structure Google Places data

```bash
python clean_nearby_places.py <input_file>
```

Example:
```bash
python clean_nearby_places.py output_nearbySearch/41.8781--87.6298.json
```

This processes raw data and saves cleaned data to `output_nearbySearch_cleaned/` directory.

### 3. AI-powered web scraping and data extraction

```bash
python ai_data_cleaner.py <path_to_place_data_file>
```

Example:
```bash
python ai_data_cleaner.py output_nearbySearch_cleaned/IL/some_place.json
```

This scrapes the place's website and uses OpenAI to extract structured data, saving to `output_nearbySearch_ai_cleaned/` directory.

### 4. Backend operations via interactive CLI

```bash
python backend_CLI.py
```

Interactive menu with options:
- **'pe'**: Process Existing - interact with existing place data in backend
- **'pn'**: Post New - add new place data to backend  
- **'pns'**: Process Nearby Search - interact with local nearby search data
- **'q'**: Quit

### 5. Using BackendClient programmatically

```python
from BackendClient import BackendClient

client = BackendClient()
response = client.get_place_by_id(123)
client.create_place(place_data)
client.update_place(123, updated_data)
```

## Project Structure & Data Flow

```
Raw Google Places Data → Cleaned/Normalized Data → AI-Enhanced Data → Backend Storage
     (fetch_nearby_places.py)   (clean_nearby_places.py)   (ai_data_cleaner.py)   (backend_CLI.py)
```

### Output Directories

- `output_nearbySearch/` - Raw Google Places API responses
- `output_nearbySearch_cleaned/` - Cleaned and normalized place data organized by state  
- `output_nearbySearch_ai_cleaned/` - AI-processed data with extracted promotions, events, and menus

## Key Features

- **Class-based architecture**: Modular design with PlacesFetcher, LLMCleaner, and BackendClient classes
- **Comprehensive web scraping**: Multi-page crawling with same-domain filtering
- **Advanced LLM integration**: Structured data extraction using OpenAI with Pydantic schemas
- **Flexible backend operations**: Full CRUD operations with geographic bounds search
- **Interactive CLI**: User-friendly interface for batch processing and individual record management
- **Error handling**: Robust exception handling throughout the pipeline

## Improvements (future work)

* Add timestamps to requests for freshness tracking
* Implement retry logic with exponential backoff for failed API requests
* Add support for non-English place filtering  
* Expand CLI batch processing capabilities
* Add configuration file support for API parameters

## License

This project is provided as-is for internal and research purposes, though all help is welcome. Once this works for my purposes I intend to generalize it more such that it can be used to leverage inputting small amounts of incredibly unstructured text data from web content given certain prompting suggestions, outputting a strictly defined JSON or other form of output.
