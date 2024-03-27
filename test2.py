import concurrent.futures
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

# Load CSV file
csv_path = './test.csv'  # Change the input file path
df = pd.read_csv(csv_path)

# Create new columns for related topics and category values
df['Related Topics'] = ''
df['Category Values'] = ''

# Create a progress bar using tqdm
pbar = tqdm(total=len(df), desc="Fetching data")

# Create a new DataFrame for Unique Similar Sites
unique_similar_sites_df = pd.DataFrame(columns=['Domain', 'Unique Similar Site'])

# Set to keep track of visited domains across all depths
visited_domains = set()

# Function to fetch unique similar sites for a given domain recursively with 5 depths
def fetch_unique_similar_sites_recursive(domain, depth=1):  # Start from depth 1
    global unique_similar_sites_df
    global visited_domains

    if depth > 5 or domain in visited_domains:
        return

    print(f"Fetching unique similar sites for {domain} (Depth: {depth})")

    source_url = f'https://www.similarsites.com/site/{domain}'

    try:
        # Make a request to the source URL with a custom user-agent
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        r = requests.get(source_url, headers=headers)
        r.raise_for_status()  # Raise HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {domain}: {e}")
        return None

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')

    # Find Unique Similar Sites
    similar_sites_divs = soup.find_all('div', class_='SimilarSitesCard__Domain-zq2ozc-4 kuvZIX')
    similar_sites = [site.text.strip() for site in similar_sites_divs]

    # Remove duplicate Similar Sites and already visited domains using set
    unique_similar_sites = set(similar_sites) - visited_domains

    # Save unique similar sites for the current domain
    for unique_site in unique_similar_sites:
        unique_similar_sites_df = pd.concat([unique_similar_sites_df, pd.DataFrame({'Domain': [domain], 'Unique Similar Site': [unique_site]})], ignore_index=True)

        # Mark the domain as visited to avoid processing it again
        visited_domains.add(domain)

        # Fetch unique similar sites recursively for the new domain
        fetch_unique_similar_sites_recursive(unique_site, depth=depth + 1)

    print(f"Finished fetching unique similar sites for {domain} (Depth: {depth})")

    # Periodically save the DataFrame to CSV after every 100 rows
    if len(unique_similar_sites_df) % 100 == 0:
        save_path = f'/Users/rentsher/Desktop/Unique_Similar_Sites_{len(unique_similar_sites_df)}.csv'
        unique_similar_sites_df.to_csv(save_path, index=False)

# Use ThreadPoolExecutor for concurrent execution
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit tasks for each domain
    futures = [executor.submit(fetch_unique_similar_sites_recursive, row['Domain']) for _, row in df.iterrows()]

    # Process results as they complete
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            pbar.update(1)

# Save Unique Similar Sites DataFrame to a new CSV file
final_save_path = '/Users/rentsher/Desktop/Unique_Similar_Sites_Final.csv'  # Adjust the output file path
unique_similar_sites_df.to_csv(final_save_path, index=False)

# Close the progress bar
pbar.close()
