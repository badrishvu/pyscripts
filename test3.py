import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
from datetime import datetime

# Load CSV file
csv_path = './test.csv'
df = pd.read_csv(csv_path)

# Create new columns
df['Website Traffic'] = ''
df['Business Category'] = ''
df['Title'] = ''
df['Fetched date_time'] = ''

# Set to keep track of visited domains at each depth
visited_domains_by_depth = {depth: set() for depth in range(1, 6)}

# Counter to limit the number of processed rows
processed_row_count = 0

# Function to fetch data for a given domain with recursive depth
def fetch_data(domain, depth=1):
    global visited_domains_by_depth
    global processed_row_count

    if processed_row_count >= 25 or domain in visited_domains_by_depth[depth]:
        print(f"Skipping {domain} at depth {depth} as it's already fetched or stopping process.")
        return

    print(f"Fetching data for {domain} (Depth: {depth})")

    source_url = f'https://www.similarsites.com/site/{domain}'

    try:
        # Make a request to the source URL with a custom user-agent
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        r = requests.get(source_url, headers=headers)
        r.raise_for_status()  # Raise HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {domain} (Depth: {depth}): {e}")
        return None

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(r.text, 'html.parser')

    # Find and update values for the new columns
    website_traffic = soup.find('div', {'data-testid': 'siteheader_monthlyvisits'})
    business_category = soup.find('div', class_='StatisticsCategoriesDistribution__CategoryTitleValueWrapper-fnuckk-5 dvxqnd')
    title = soup.title.string

    # Update values in the DataFrame
    df.loc[df['Domain'] == domain, 'Website Traffic'] = website_traffic.text if website_traffic else ''
    df.loc[df['Domain'] == domain, 'Business Category'] = business_category.text if business_category else ''
    df.loc[df['Domain'] == domain, 'Title'] = title if title else ''

    # Update current timestamp in the "Fetched date_time" column
    df.loc[df['Domain'] == domain, 'Fetched date_time'] = datetime.now()

    # Mark the domain as visited to avoid processing it again at this depth
    visited_domains_by_depth[depth].add(domain)

    print(f"Finished fetching data for {domain} (Depth: {depth})")

    # Increment the processed row count
    processed_row_count += 1

    # Fetch unique similar sites recursively for the new domain
    if depth < 5:
        similar_sites_divs = soup.find_all('div', class_='SimilarSitesCard__Domain-zq2ozc-4 kuvZIX')
        similar_sites = [site.text.strip() for site in similar_sites_divs]
        for unique_site in set(similar_sites) - set(df['Domain']):
            fetch_data(unique_site, depth=depth + 1)

# Start fetching data
for _, row in tqdm(df.iterrows(), total=len(df), desc="Fetching data"):
    fetch_data(row['Domain'])
    if processed_row_count >= 25:
        break

# Save the updated DataFrame to a new CSV file
final_save_path = './test_updated_first_25.csv'  # Adjust the output file path
unique_df = df.drop_duplicates(subset='Domain')
unique_df.to_csv(final_save_path, index=False)
