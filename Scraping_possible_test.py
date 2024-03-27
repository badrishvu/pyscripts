import csv
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def extract_content(driver_path):
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Set to False if you want to see the browser in action

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        url = "https://jwplayer.com/video-delivery/"

        print(f"Accessing URL: {url}")
        driver.get(url)

        # Wait for the page to load, adjust the timeout as needed
        print("Waiting for the page to load...")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='top']")))

        # Extract all content from div elements with class 'sc-gEvEer gWlAOS'
        print("Extracting content...")
        elements = driver.find_elements(By.XPATH, "//div[@class='top']")
        extracted_content = [element.text for element in elements]

        for i, content in enumerate(extracted_content, 1):
            print(f"Content #{i}: {content}")

        return extracted_content

    finally:
        print("Quitting Chrome driver...")
        driver.quit()

def save_to_csv(file_path, content):
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:  # Use 'a' for append mode
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows([[item] for item in content])

def process_content(output_csv_path):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(extract_content, driver_path)]
        concurrent.futures.wait(futures)
        results = [future.result() for future in futures]

    all_content = [item for sublist in results for item in sublist]

    print(f"Saving content to {output_csv_path}...")
    save_to_csv(output_csv_path, all_content)

if __name__ == "__main__":
    output_csv_path = "/Users/rentsher/Desktop/AllContentOutput.csv"
    driver_path = "/Users/rentsher/Downloads/Gumlet_leads_dump/chromedriver-mac-x64/chromedriver"

    # Truncate the existing output file or create a new one
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Content'])

    process_content(output_csv_path)


