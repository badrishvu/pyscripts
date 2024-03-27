import csv
import requests
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Function to add scheme if not present
def add_scheme(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        return 'http://' + url
    return url

def fetch_url(url, session):
    url = add_scheme(url)  # Add scheme if not present
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        response = session.get(url, allow_redirects=True, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Handle 403 Forbidden client error
        if response.status_code == 403:
            print(f"Access to {url} is forbidden (HTTP 403 error).")
            return url, None, response.status_code

        # Get the final URL after following redirects
        final_url = response.url
        
        return final_url, response.text, response.status_code
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return url, None, None

def search_string_in_content(content, search_strings):
    for search_string, label in search_strings.items():
        if search_string in content:
            print(f"String '{search_string}' found")
            return label
    return "Not Found"

def process_row(row, search_strings, session):
    domain = row.get('Domain')
    try:
        url, content, status_code = fetch_url(domain, session)
        if content is not None:
            result = search_string_in_content(content, search_strings)
            row['SearchResult'] = result
            row['StatusCode'] = status_code
        else:
            row['SearchResult'] = "Error"
            row['StatusCode'] = status_code
    except Exception as e:
        print(f"An error occurred while processing row for domain {domain}: {e}")
        row['SearchResult'] = "Error"
        row['StatusCode'] = None
    return row

def process_csv(input_path, output_path, search_strings):
    try:
        with requests.Session() as session:
            with open(input_path, 'r', newline='') as input_file:
                reader = csv.DictReader(input_file)
                data = list(reader)

            with ThreadPoolExecutor() as executor:
                results = list(executor.map(lambda row: process_row(row, search_strings, session), data))

            header = ['Domain', 'SearchResult', 'StatusCode'] + list(data[0].keys())
            with open(output_path, 'w', newline='') as output_file:
                writer = csv.DictWriter(output_file, fieldnames=header)
                writer.writeheader()
                writer.writerows(results)

            print(f"Search results saved to '{output_path}'")
    except Exception as e:
        print(f"An error occurred during processing: {e}")

# Example usage:
input_csv_path = "./test.csv"
output_csv_path = "/Users/rentsher/Desktop/Search_Results.csv"
search_strings_to_search = {"vimeo.com": "Vimeo", "wistia.com": "Wistia","mux.com":"Mux","jwpcdn":"JW Player",}

process_csv(input_csv_path, output_csv_path, search_strings_to_search)
