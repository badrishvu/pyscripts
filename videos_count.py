import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import ffmpeg
import re

# Replace 'url' with the URL of the website you want to scrape
url = 'https://prepexpert.com/schedules/act129047/'  # Replace with your target URL

def count_videos_with_bs4(url):
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Count the number of video elements on the page
            video_elements = soup.find_all(['video', 'iframe', 'object', 'embed', 'a'])

            num_videos = 0

            for element in video_elements:
                if element.name == 'a' and 'href' in element.attrs:
                    if re.search(r'\.(mp4|mov|avi|mkv|flv|wmv|webm)$', element['href'], re.IGNORECASE):
                        num_videos += 1
                else:
                    num_videos += 1

            return num_videos

        else:
            print(f'Failed to retrieve content from {url}. Status code: {response.status_code}')
            return 0

    except Exception as e:
        print(f'An error occurred: {str(e)}')
        return 0

def count_videos_with_selenium(url):
    try:
        # Create a headless Chrome WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        
        # Load the web page
        driver.get(url)

        # Wait for the page to load (you may need to adjust the sleep time)
        driver.implicitly_wait(10)

        # Count the number of video elements on the page
        video_elements = driver.find_elements_by_tag_name('video')

        num_videos = len(video_elements)

        return num_videos

    except Exception as e:
        print(f'An error occurred: {str(e)}')
        return 0

def main():
    # Count videos using BeautifulSoup
    num_videos_bs4 = count_videos_with_bs4(url)

    # Count videos using Selenium
    num_videos_selenium = count_videos_with_selenium(url)

    print(f'Total number of videos using BeautifulSoup: {num_videos_bs4}')
    print(f'Total number of videos using Selenium: {num_videos_selenium}')

if __name__ == "__main__":
    main()
