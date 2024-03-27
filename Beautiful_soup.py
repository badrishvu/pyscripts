import pandas as pd
import requests
from bs4 import BeautifulSoup

# Function to fetch data from the given domain URL
def fetch_data(domain_url):
    try:
        response = requests.get(domain_url)
        response.raise_for_status()  # Raise an exception for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extracting data using BeautifulSoup logic
        data = [a['href'] for a in soup.find_all('a', class_='sc-fUnMCh lhDdjp')]
        return data
    except Exception as e:
        print(f"Error fetching data from {domain_url}: {e}")
        return None

# Read CSV file using pandas
csv_path = './test.csv'
df = pd.read_csv(csv_path)

# Iterate through each row and fetch data
for index, row in df.iterrows():
    domain_url = row['Domain']
    data = fetch_data(domain_url)

    # Print or process the fetched data as needed
    if data:
        print(f"Data for {domain_url}: {data}")
    else:
        print(f"No data fetched for {domain_url}")
