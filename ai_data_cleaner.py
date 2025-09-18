import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import sys
import os
import logging
from dotenv import load_dotenv

from openai import OpenAI
from openai.types.responses import ResponseUsage, ParsedResponse, ParsedResponseOutputMessage, ParsedResponseOutputText

from typing import cast

from ai_schema_config import PlaceDataExtraction, SCHEMA_DESCRIPTION

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
        self.schema_description = SCHEMA_DESCRIPTION

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

    def call_openai_api(self, scraped_website_content: str) -> dict[str]:
        """Use OpenAI API to refine unstructured text data into structured format"""

        logger.info("Refining text data with OpenAI API...")

        try:
            response: ParsedResponse[PlaceDataExtraction] = self.client.responses.parse(
                model="gpt-4o-mini",
                input=[
                    {"role": "system", "content": self.schema_description},
                    {"role": "user", "content": scraped_website_content}
                ],
                text_format=PlaceDataExtraction
            )
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise

        # # The parsed object is directly available here
        # place: PlaceDataExtraction = response.output[0]
        # logger.info(f"Refined data: {place.model_dump_json(indent=2)}")

        # # Token usage (new field names)
        # input_tokens = response.usage.input_tokens
        # output_tokens = response.usage.output_tokens
        # total_tokens = response.usage.total_tokens

        # # Store the refined content and token usage information
        # llm_output = {
        #     "content": place,
        #     "input_tokens": input_tokens,
        #     "output_tokens": output_tokens,
        #     "total_tokens": total_tokens,
        # }

        usage_info: ResponseUsage = response.usage
        input_tokens = usage_info.input_tokens
        output_tokens = usage_info.output_tokens
        total_tokens = usage_info.total_tokens
        print(f"\nToken usage - Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}\n")

        response_message: ParsedResponseOutputMessage[PlaceDataExtraction] = response.output[0]
        # print(f"\nResponse message (response.output[0]): {response_message}\n")

        response_content: ParsedResponseOutputText[PlaceDataExtraction] = cast(
            ParsedResponseOutputText[PlaceDataExtraction], response_message.content[0]
        )
        # print(f"\nResponse content (response.output[0].content[0]): {response_content}\n")

        response_parsed: PlaceDataExtraction = response_content.parsed
        # print(f"\nResponse parsed (response.output[0].content[0].parsed): {response_parsed}\n")

        return response_parsed


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

        # Refine the collected content using LLM (currently gpt-4o-mini) and turn into python dict
        openai_output: PlaceDataExtraction = self.call_openai_api(scraped_website_content=scraped_website_content)
        structured_place_data_dict = openai_output.model_dump()

        # Include id and coordinates into structured_data from place_data and save as json object
        structured_place_data_dict["id"] = place_data.get("id")
        structured_place_data_dict["latitude"] = place_data.get("latitude")
        structured_place_data_dict["longitude"] = place_data.get("longitude")
        structured_place_data_json = json.dumps(structured_place_data_dict, ensure_ascii=False, indent=2)

        # if verbose: logger.info(f"\n------------\nTOKEN INFO\nPrompt: {llm_output.get('prompt_tokens', 'ERR')}\nCompletion: {llm_output.get('completion_tokens', 'ERR')}\nTotal: {llm_output.get('total_tokens', 'ERR')}\n------------\n")
        # TODO: Store/track/log token usage info
        # TODO: Compare to existing place data
        self._write_to_output_file(structured_place_data_json, output_filename)
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
