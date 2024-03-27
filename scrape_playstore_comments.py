import csv
import multiprocessing
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def extract_links(url, driver_path, result_queue):
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Set to False if you want to see the browser in action

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print(f"Accessing URL: {url}")
        driver.get(url)

        # Wait for the page to load, adjust the timeout as needed
        print("Waiting for the page to load...")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//a[@class='JC71ub']")))

        # Scroll up to two times
        for scroll_count in range(2):
            print(f"Scrolling #{scroll_count + 1}...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@class='JC71ub']")))
            time.sleep(2)  # Add a sleep to allow content to load

        # Extract all links with class 'JC71ub'
        print("Extracting links...")
        links = driver.find_elements(By.XPATH, "//a[@class='JC71ub']")
        extracted_links = [link.get_attribute("href") for link in links]

        result_queue.put(extracted_links)

    finally:
        print("Quitting Chrome driver...")
        driver.quit()

def save_to_csv(file_path, links):
    with open(file_path, 'a', newline='') as csvfile:  # Use 'a' for append mode
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows([[link] for link in links])

def process_urls(input_csv_path, output_csv_path):
    with open(input_csv_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        urls = [row['Domain'] for row in reader]

    result_queue = multiprocessing.Queue()

    processes = []
    for url in urls:
        process = multiprocessing.Process(target=extract_links, args=(url, driver_path, result_queue))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    # Collect results from the queue
    all_links = []
    while not result_queue.empty():
        all_links.extend(result_queue.get())

    print(f"Saving links to {output_csv_path}...")
    save_to_csv(output_csv_path, all_links)

if __name__ == "__main__":
    input_csv_path = "./test.csv"
    output_csv_path = "/Users/rentsher/Desktop/AllLinksOutput.csv"
    driver_path = "/Users/rentsher/Downloads/Gumlet_leads_dump/chromedriver-mac-x64/chromedriver"

    # Truncate the existing output file or create a new one
    with open(output_csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Link'])

    process_urls(input_csv_path, output_csv_path)
    