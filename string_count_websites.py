import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import time

def count_string_in_domain(domain, target_string, uppercase=False, timeout=60):
    try:
        # Construct the URL with the 'http://' or 'https://' prefix
        url = f"http://{domain}" if not domain.startswith(("http://", "https://")) else domain
        
        # Send an HTTP GET request to the URL with a timeout
        response = requests.get(url, timeout=timeout)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Get the content of the web page
            page_content = response.text
            
            # Optionally capitalize or uppercase the HTML content
            if uppercase:
                page_content = page_content.upper()
            
            # Count the occurrences of the target string
            count = page_content.count(target_string.upper())
            
            return count
        elif response.status_code == 403:
            print(f"URL '{url}' returned a '403 Forbidden' status code. Skipping.")
            return 0  # Return 0 to indicate that the URL was processed but no occurrences found
        else:
            print(f"Failed to fetch the URL '{url}'. Status code: {response.status_code}")
            return -1  # Return -1 to indicate an error
    except requests.Timeout:
        print(f"Timeout occurred while processing the URL '{url}'. Skipping.")
        return -1  # Return -1 to indicate a timeout error
    except Exception as e:
        print(f"An error occurred while processing the URL '{url}': {str(e)}")
        return -1  # Return -1 to indicate an error

# Path to the CSV file containing Domains (replace with your input CSV file path)
input_csv_file_path = "test.csv"  # Replace with the actual input path

# Read the CSV file into a DataFrame
try:
    df = pd.read_csv(input_csv_file_path)
except Exception as e:
    print(f"An error occurred while reading the CSV file: {str(e)}")
    df = pd.DataFrame()

if not df.empty:
    target_string = "akamai"
    
    # Create a list to store the results
    results = []

    # Replace "YourColumnName" with the actual column name containing the Domains
    domains = df["Domain"]

    # Configure tqdm with the total number of Domains for accurate progress tracking
    total_domains = len(domains)
    with tqdm(total=total_domains, desc="Processing Domains") as pbar:
        # Create a ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            # Wrap the loop for progress monitoring
            for domain in domains:
                start_time = time.time()
                future = executor.submit(count_string_in_domain, domain, target_string, uppercase=True)
                future.add_done_callback(lambda x: pbar.update(1))  # Update progress bar
                futures.append((domain, future))
            
            for domain, future in futures:
                count = future.result()
                if count is not None:
                    result_entry = {
                        "Domain": domain,
                        "Count": count
                    }
                    results.append(result_entry)

    # Create a DataFrame from the results
    df_results = pd.DataFrame(results)

    # Path to the output CSV file (replace with your desired output file path)
    output_csv_file_path = "/Users/rentsher/Desktop/output_results_with_counts_4.csv"  # Replace with the actual output path

    # Save the DataFrame with results to the output CSV file
    df_results.to_csv(output_csv_file_path, index=False)

    print(f"Results saved to '{output_csv_file_path}'.")
else:
    print("Empty DataFrame. No processing or saving was performed.")