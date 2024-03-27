import csv
import concurrent.futures
import requests

input_csv_file = '/Users/rentsher/Desktop/analyse.csv'
output_csv_file = '/Users/rentsher/Desktop/Output.csv'

def process_row(row):
    domain = row['Domain']
    try:
        url = f'https://{domain}'
        print(f"Processing {domain}...")
        response = requests.get(url, timeout=15, allow_redirects=False)

        if 400 <= response.status_code < 500:
            row['Status code for that domain url'] = response.status_code

        if not url.startswith('https://'):
            row['secured'] = 'not secure'
        else:
            row['secured'] = 'secure'

        if response.status_code == 301:
            redirected_url = response.headers.get('Location')
            if redirected_url:
                row['redirected'] = redirected_url
            else:
                row['redirected'] = 'No Location Header'
        else:
            row['redirected'] = 'Not Redirected'

        print(f"Processed {domain}")
    except Exception as e:
        print(f"Error processing {domain}: {e}")
    return row

def main():
    results = []
    with open(input_csv_file, 'r') as input_csv, open(output_csv_file, 'w', newline='') as output_csv:
        reader = csv.DictReader(input_csv)
        fieldnames = reader.fieldnames + ['Status code for that domain url', 'secured', 'redirected']
        writer = csv.DictWriter(output_csv, fieldnames=fieldnames)
        writer.writeheader()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_row = {executor.submit(process_row, row): row for row in reader}
            for future in concurrent.futures.as_completed(future_to_row):
                row = future_to_row[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error processing {row['Domain']}: {e}")

        writer.writerows(results)

if __name__ == "__main__":
    main()
