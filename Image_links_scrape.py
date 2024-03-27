import csv
import concurrent.futures
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import base64
import requests

def extract_images(url, min_image_size_kb=300):
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        image_links = []
        for img_tag in driver.find_elements(By.TAG_NAME, 'img'):
            img_src = img_tag.get_attribute('src')

            if img_src and (img_src.startswith('data:image') or img_src.startswith('http')):
                if img_src.startswith('data:image'):
                    img_data = img_src.split(',')[1]
                    img_bytes = base64.b64decode(img_data)
                else:
                    img_response = requests.get(img_src)
                    img_bytes = img_response.content

                img_size_kb = len(img_bytes) / 1024

                if img_size_kb > min_image_size_kb:
                    image_links.append(img_src)
                    print(f'Image URL (Size: {img_size_kb} KB): {img_src}')

        return image_links

    except Exception as e:
        print(f"Error extracting images from {url}: {e}")
        return []

    finally:
        driver.quit()

def process_csv(input_path, output_path):
    with open(input_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(extract_images, row['Domain']): row for row in rows}

        for future in concurrent.futures.as_completed(futures):
            row = futures[future]
            try:
                extracted_images = future.result()
                row['Extracted_Images'] = ';'.join(extracted_images)
            except Exception as e:
                print(f"Error processing {row['Domain']}: {e}")

    with open(output_path, 'w', newline='') as csv_output_file:
        fieldnames = list(reader.fieldnames) + ['Extracted_Images']
        writer = csv.DictWriter(csv_output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    input_path = Path("./test.csv")
    output_path = Path("/Users/rentsher/Desktop/extracted_img_links.csv")

    process_csv(input_path, output_path)
