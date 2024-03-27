import requests
from bs4 import BeautifulSoup
import pandas as pd

def extract_content(url):
    print(f"Fetching content from URL: {url}")
    response = requests.get(url)
    print(f"Response status code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract content from class "htlgb"
    htlgb_elements = soup.find_all(class_='htlgb')
    htlgb_content = [element.get_text() for element in htlgb_elements]
    print(f"htlgb content: {htlgb_content}")

    # Extract content and href links from class "b8cIId ReQCgd Q9MA7b"
    wXUyZd_elements = soup.find_all(class_='b8cIId ReQCgd Q9MA7b')
    wXUyZd_content = []
    for element in wXUyZd_elements:
        content = element.get_text()
        link = element.find('a')['href'] if element.find('a') else ''
        wXUyZd_content.append({'content': content, 'link': "https://play.google.com"+link})

    print(f"b8cIId ReQCgd Q9MA7b content: {wXUyZd_content}")

    return htlgb_content, wXUyZd_content

def process_csv(input_csv, output_csv):
    print(f"Reading CSV file: {input_csv}")
    # Read CSV file
    df = pd.read_csv(input_csv)

    # Add new columns for extracted content
    print("Extracting content from each URL...")
    df[['htlgb_content', 'similar_apps_content']] = df['Domain'].apply(extract_content).apply(pd.Series)

    # Save the updated DataFrame to a new CSV file
    print(f"Saving updated DataFrame to: {output_csv}")
    df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    input_csv = "./test.csv"
    output_csv = "/Users/rentsher/Desktop/playstore_work_data_extractor.csv"

    process_csv(input_csv, output_csv)
