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

def extract_links(url, driver_path):
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print(f"Accessing URL: {url}")
        driver.get(url)

        print("Waiting for the page to load...")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//a[@class='JC71ub']")))

        for scroll_count in range(2):
            print(f"Scrolling #{scroll_count + 1}...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@class='JC71ub']")))

        print("Extracting links...")
        links = driver.find_elements(By.XPATH, "//a[@class='JC71ub']")
        extracted_links = [link.get_attribute("href") for link in links]
        return extracted_links

    finally:
        print("Quitting Chrome driver...")
        driver.quit()

def save_to_csv(file_path, links):
    existing_links = set()
    try:
        with open(file_path, 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)  # Skip header row
            existing_links = set(row[0] for row in csv_reader)
    except FileNotFoundError:
        pass  # Ignore if the file doesn't exist

    unique_links = [link for link in links if link not in existing_links]

    with open(file_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows([[link] for link in unique_links])

def process_url(url, driver_path, output_csv_path):
    links = extract_links(url, driver_path)
    print(f"Saving links to {output_csv_path}...")
    save_to_csv(output_csv_path, links)

if __name__ == "__main__":
    input_csv_path = "./business_domain.csv"
    output_csv_path = "/Users/rentsher/Desktop/AllLinksOutput.csv"
    driver_path = "/Users/rentsher/Downloads/Gumlet_leads_dump/chromedriver-mac-x64/chromedriver"

    with open(output_csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Link'])

    with open(input_csv_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        urls = [row['Domain'] for row in reader]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(process_url, urls, [driver_path] * len(urls), [output_csv_path] * len(urls))
