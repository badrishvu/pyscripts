import requests
from bs4 import BeautifulSoup
import re

def extract_playstore_link(url):
    try:
        # Fetch the HTML content of the webpage
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find Play Store links in href attributes of <a> tags
        playstore_links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if 'play.google.com/store/apps/details?id=' in href:
                playstore_links.append(href)

        return playstore_links

    except Exception as e:
        print(f"Error: {e}")
        return None

# Example usage:
website_url = "https://www.smytten.com"
playstore_links = extract_playstore_link(website_url)

if playstore_links:
    for index, link in enumerate(playstore_links, start=1):
        print(f"Play Store link {index}: {link}")
else:
    print("Play Store links not found.")
