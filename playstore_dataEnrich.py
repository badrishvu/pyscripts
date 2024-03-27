import csv
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def extract_data(playstore_link):
    if not is_valid_url(playstore_link):
        logger.warning(f"Invalid URL: {playstore_link}")
        return 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'

    try:
        response = requests.get(playstore_link)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting data from specific div classes
        ratings_element = soup.find('div', class_='TT9eCd')
        ratings = ratings_element.text.strip() if ratings_element else 'N/A'

        downloads_elements = soup.find_all('div', class_='ClM7O')
        downloads = downloads_elements[1].text.strip() if len(downloads_elements) >= 2 else 'N/A'

        app_details_section = soup.find('a', class_='Si6A0c RrSxVb')
        app_details = app_details_section.text.strip() if app_details_section else 'N/A'

        app_name = soup.find('h1', class_='Fd93Bb F5UCq xwcR9d')
        app_name = app_name.text.strip() if app_name else 'N/A'

        app_company_name = soup.find('div', class_='Vbfug auoIOc')
        app_company_name = app_company_name.text.strip() if app_company_name else 'N/A'

        # Extracting href value
        website_link_element = soup.find('a', class_='Si6A0c RrSxVb')
        website_link = website_link_element['href'] if website_link_element and 'href' in website_link_element.attrs else 'N/A'

        return ratings, downloads, app_details, website_link, app_name, app_company_name

    except requests.RequestException as e:
        logger.error(f"Error while fetching data from {playstore_link}: {e}")
        return 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'
    except Exception as ex:
        logger.exception(f"An unexpected error occurred for {playstore_link}: {ex}")
        return 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'

def process_link(playstore_link):
    try:
        ratings, downloads, app_details, website_link, app_name, app_company_name = extract_data(playstore_link)
        return [playstore_link, ratings, downloads, app_details, website_link, app_name, app_company_name]
    except Exception as ex:
        logger.exception(f"An unexpected error occurred while processing {playstore_link}: {ex}")
        return [playstore_link, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']

# Input and output file paths
input_filename = './business_domain.csv'
output_filename = '/Users/rentsher/Desktop/Playstore_output.csv'

# Write header row with specified column order
header = ['Playstore_link', 'Ratings', 'Downloads', 'App_details', 'App Link', 'app_name', 'app_company_name']

with open(input_filename, 'r') as csv_file, open(output_filename, 'w', newline='') as output_csv_file:
    reader = csv.reader(csv_file)
    writer = csv.writer(output_csv_file)

    writer.writerow(header)

    playstore_links = [row[0] for row in reader if row and is_valid_url(row[0])]
    
    with ThreadPoolExecutor(max_workers=5) as executor, tqdm(total=len(playstore_links), desc="Processing Apps") as pbar:
        results = list(executor.map(process_link, playstore_links))
        for result in results:
            writer.writerow(result)
            pbar.update(1)

print("Data extraction and transformation complete.")
