import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import sys
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LLMCleaner:
    def __init__(self, api_key=None):
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
        
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.OUTPUT_DIR = "output_nearbySearch_ai_cleaned"

        # Desired output schema from AI API
        self.schema_description = """
Your job is to extract structured information from unstructured website text data.
Primarily, you should focus on identifying key details such including
business hours, contact information, descriptions, events and promotions.

For each unstructured text, a PlaceData object should be created. Additionally, if any 
information is available about the place's menu items, events, or promotions, the 
corresponding MenuData, EventData, or PromoData objects should be created for them.

Each day of the week should have it's own data for regular open hours or promotions.
Don't represent multiple promotions across different days as a single entry.

If deciding between categorizing something as an event or a promotion, events should be
one time or one-off occurrences, while promotions should be for ongoing or recurring occurrences.

One exception for daily hours is that if they have no time listed for a promotion or event and you conclude
the duration is for the entire day, set the open hour to 0 and close hour to 0 to represent that.


DailyHours = {
    day: "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday" | "Saturday" | "Sunday"; 
    open_hour: number; // 0-23 instead
    open_minute?: number; // Optional, for half-hour increments
    close_hour: number; // 0-23
    close_minute?: number; // Optional, for half-hour increments
}

type PlaceData = {
    name: string;
    street: string;
    city: string;
    state_code: string;
    zip: number;
    latitude: number;
    longitude: number;
    hours?: DailyHours[];
    amenity?: string; (e.g. "pool table", "patio", "darts", "board games")
    cuisine?: string[]; (e.g. "burger", "italian", "sushi")
    price_level?: string;
    rating?: number; (1-5)
    description?: string;
    phone?: string;
    email?: string;
    website?: string;
    profile_image_url?: string;
    image_urls?: string[];
    primary_type?: string; (e.g. "restaurant", "bar", "cafe", "pub", "night club")
    secondary_types?: string[];
};

type PromoData = [
{
    title: string;
    description?: string;
    hours?: DailyHours[];
}, ...
];

type MenuData = [
{
    name: string;
    description?: string;
    price: number;
    category: string;
}, ...
];

type EventData = [
{
    title: string;
    description?: string;
    startDate: string;
    endDate: string;
    eventType: string;
    hours?: DailyHours[];
}, ...
];
"""

    def _get_place_data(self, place_data_filepath: str) -> dict:
        """Load place data from a JSON file."""
        if not os.path.exists(place_data_filepath):
            logger.warning(f"Place data file not found: {place_data_filepath}")
            raise FileNotFoundError(f"Place data file not found: {place_data_filepath}")

        with open(place_data_filepath, "r") as f:
            return json.load(f)

    def _is_same_domain(self, link_url, root_url):
        """Check if link is from the same domain as root URL"""
        from urllib.parse import urlparse
        
        link_domain = urlparse(link_url.lower()).netloc
        root_domain = urlparse(root_url.lower()).netloc
        
        return link_domain == root_domain

    def _fetch_page_content(self, url):
        """Fetch text content and relevant links from a single page"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract visible text from important elements
            text_elements = soup.find_all(["p", "h1", "h2", "h3", "li", "span"])
            text = " ".join([element.get_text(separator=" ", strip=True) for element in text_elements])

            # Find relevant subpage (same domain) links
            subpage_links = []
            for link in soup.find_all("a", href=True):
                href = link["href"].lower()
                if (href.startswith('#') or href.startswith('javascript:')): 
                    continue

                full_url = urljoin(url, href)
                if self._is_same_domain(full_url, url): 
                    subpage_links.append(full_url)

            return text, list(set(subpage_links))

        except Exception as e:
            logger.error(f"Error fetching page content from {url}: {e}")
            return "", []

    def _collect_site_content(self, root_url, max_pages=10):
        """Collect text content from root URL and relevant subpages"""

        visited = set()
        to_visit = [root_url]
        all_content = []

        while to_visit and len(visited) < max_pages:
            current_url = to_visit.pop(0)

            #  Filter seen links and anchor links (e.g. 'https://www.example.com/#section')
            if (current_url in visited) or ('#' in current_url): continue        
            
            # Fetch and process new unseen link    
            visited.add(current_url)
            text, new_links = self._fetch_page_content(current_url)
            all_content.append(f"=== {current_url} ===\n{text}")

            # Add new unvisited, non-anchor links to queue
            for link in new_links:
                if (link not in visited) and (link not in to_visit) and (not '#' in link):
                    to_visit.append(link)

        

        return "\n".join(all_content)

    def refine_text_data_with_openai(self, scraped_website_content: str) -> dict[str]:
        """Use OpenAI API to refine unstructured text data into structured format"""

        #TODO: Switch to responses api
        # response = self.client.responses.create(
        #     model="gpt-4o-mini",
        #     instructions=self.schema_description,
        #     input=content
        # )

        
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {
                    "role": "system",
                    "content": self.schema_description
                },
                {
                    "role": "user",
                    "content": scraped_website_content
                }
            ],
            response_format={"type": "json_object"}  # Request JSON object response
        )
        
        # Refine the content from the completion (auto extract JSON object if extra text present)
        content = completion.choices[0].message.content
        print(f"\n\nRaw Content Returned from AI:\n\n{content}\n")
        # Attempt to extract JSON object from content
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1 and start < end:
            content = content[start:end+1]
            content = json.loads(content)
        else:
            raise ValueError("Could not find JSON object in the response content.")
        
        print(f"Content after json.loads():\n\n{content}\n")
        
        # Store the refined content and token usage information
        llm_output = {}
        llm_output["content"] = content
        llm_output["prompt_tokens"] = completion.usage.prompt_tokens
        llm_output["completion_tokens"] = completion.usage.completion_tokens
        llm_output["total_tokens"] = completion.usage.total_tokens

        return llm_output

    def _write_to_output_file(self, content:str, filename:str):
        """Write content to output file, with option to overwrite if file exists"""

        os.makedirs(self.OUTPUT_DIR, exist_ok=True) # Create directory if it doesn't exist
        full_path = os.path.join(self.OUTPUT_DIR, filename) # Full path to the output file

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse content as JSON.")

        if os.path.exists(full_path) and (input(f"File {filename} exists. Replace existing content? (y/n): ") == 'y'):
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False, indent=2)+"\n")
        else:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False, indent=2)+"\n")

    def process_url(self, place_data:dict, output_filename:str, verbose:bool=False):
        """Process a single URL and write results to output file"""
        website_url = place_data.get("website")
        if not website_url:
            raise ValueError("No valid website URL found in place data.")

        # Recursive crawler to collect text data from base url and subpages
        scraped_website_content:str = self._collect_site_content(root_url=website_url, max_pages=10)
        if verbose: logger.info(f"[process_url]: Collected content length: {len(scraped_website_content)} characters from base url: {website_url}")
        if (len(scraped_website_content) == 0): 
            raise ValueError("No content collected from base url")

        # Refine the collected content using LLM (currently gpt-4o-mini)
        llm_output = self.refine_text_data_with_openai(scraped_website_content=scraped_website_content)
        if verbose: logger.info(f"\n------------\nTOKEN INFO\nPrompt: {llm_output.get('prompt_tokens', 'ERR')}\nCompletion: {llm_output.get('completion_tokens', 'ERR')}\nTotal: {llm_output.get('total_tokens', 'ERR')}\n------------\n")

        # Include id and coordinates into structured_data from place_data and save as json object
        structured_place_data = llm_output["content"]
        print(f"\n\nType of content returned from 'completion.choices[0].message.content' (AI output): {type(structured_place_data)}\n")
        print(f"Place Data Collected from AI:\n\n{structured_place_data}\n")
        structured_place_data["id"] = place_data.get("id")
        structured_place_data["latitude"] = place_data.get("latitude")
        structured_place_data["longitude"] = place_data.get("longitude")
        # TODO: Compare to existing place data
        self._write_to_output_file(structured_place_data, output_filename)
        if verbose: logger.info(f"Finished processing {website_url}, saved as {output_filename}")


    def _get_ai_cleaned_filename(self, place_data_filepath:str) -> str:
        """Get the filename for the AI cleaned place data."""

        filename = os.path.basename(place_data_filepath)
        filename_removed_suffix = filename.split('.')[0] # Remove file extension (.json)
        ai_cleaned_filename = filename_removed_suffix + "_ai_cleaned.json"

        return ai_cleaned_filename

    def clean_place_data(self, place_data_filepath: str, verbose:bool = True):
        """Update place data by collecting website content and using
        LLM (gpt 4o) to extract and structure relevant information"""
        
        place_data: dict = self._get_place_data(place_data_filepath)

        new_filename = self._get_ai_cleaned_filename(place_data_filepath)
        if verbose: logger.info(f"Processing place website: {place_data['website']} into {new_filename}")

        try:
            self.process_url(place_data=place_data, output_filename=new_filename, verbose=verbose)
        except Exception as e:
            logger.error(f"Error occurred while processing place data: {e}")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python ai_data_cleaner.py <filepath_to_placedata>")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        cleaner = LLMCleaner()
        cleaner.clean_place_data(filepath, verbose=True)
    except Exception as e:
        logger.error(f"Error occurred while cleaning place data: {e}")

    # test_urls = [
    #     "https://www.kellyspub.com/",
    #     "https://www.codyschicago.com/",
    #     "https://www.lincolntaproom.com/",
    #     "http://www.willsnorthwoodsinn.com/",
    #     "https://www.parlaylincolnpark.com/",
    #     "https://www.birdsnestbar.com/",
    #     "https://www.delilahschicago.com/",
    #     "https://www.tapstertastingroom.com/",
    #     "https://www.lottiespub.com/"
    # ]
