import csv
import requests
from bs4 import BeautifulSoup
import concurrent.futures

def fetch_similar_domain_info(similar_domain):
    print(f"Fetching info for similar domain: {similar_domain}")
    domain_info = {'Traffic': None, 'Category': None}

    # Constructing the URL
    similar_domain_url = f'https://www.similarsites.com/site/{similar_domain}'

    # Fetching the page content
    response = requests.get(similar_domain_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Finding traffic
        traffic_element = soup.find('div', class_='SiteHeader__MetricValue-sc-1ybnx66-14 cLauOv')
        if traffic_element:
            domain_info['Traffic'] = traffic_element.text.strip()

        # Finding category
        category_element = soup.find('div', class_='StatisticsCategoriesDistribution__CategoryWrapper-fnuckk-4 eKvgan')
        if category_element:
            domain_info['Category'] = category_element.text.strip()

    print(f"Info fetched for {similar_domain}: {domain_info}")
    return domain_info

def fetch_similar_domains(domain, processed_domains):
    print(f"Fetching similar domains for source domain: {domain}")
    similar_domains_info = {}

    # Constructing the URL
    source_url = f'https://www.similarsites.com/site/{domain}'

    # Fetching the page content
    response = requests.get(source_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Finding similar domains
        similar_section = soup.find_all('div', class_='SimilarSitesCard__Domain-zq2ozc-4 kuvZIX')
        if similar_section:
            similar_domains = [link.text.strip() for link in similar_section]

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_domain_info = {}
                for similar_domain in similar_domains:
                    if similar_domain not in processed_domains:
                        future = executor.submit(fetch_similar_domain_info, similar_domain)
                        future_to_domain_info[future] = similar_domain

                for future in concurrent.futures.as_completed(future_to_domain_info):
                    similar_domain = future_to_domain_info[future]
                    try:
                        similar_domains_info[similar_domain] = future.result()
                    except Exception as e:
                        print(f"Error fetching info for {similar_domain}: {e}")

    print(f"Fetched similar domains for {domain}: {similar_domains_info}")
    return similar_domains_info

def main():
    input_file = "./test.csv"
    output_file = "/Users/rentsher/Desktop/sm.csv"

    # Read domains from CSV
    domains = []
    with open(input_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            domains.append(row['Domain'])

    # Fetch similar domains and create output data
    output_data = []
    processed_domains = set()  # To keep track of processed domains
    for domain in domains:
        similar_domains_info = fetch_similar_domains(domain, processed_domains)
        for similar_domain, info in similar_domains_info.items():
            output_data.append({
                'Source Domain': domain,
                'Similar Domain': similar_domain,
                'Traffic': info['Traffic'],
                'Category': info['Category']
            })
            processed_domains.add(similar_domain)

    # Write output data to CSV
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Source Domain', 'Similar Domain', 'Traffic', 'Category']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_data)

    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
