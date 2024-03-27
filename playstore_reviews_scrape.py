import csv
from google_play_scraper import app, reviews

def get_app_info(playstore_id):
    print("Fetching app information...")
    app_info = app(playstore_id)
    print(f"App information: {app_info}")
    return app_info

def save_reviews_to_csv(playstore_id, filepath, num_reviews=100):
    # Get app info
    app_info = get_app_info(playstore_id)
    print(f"Fetching reviews for {app_info['title']}...")

    # Get total number of reviews
    total_reviews = app_info['reviews']
    print(f"Total reviews to fetch: {total_reviews}")

    # Fetch reviews
    print(f"Fetching {num_reviews} reviews...")
    review_data, _ = reviews(playstore_id, lang='en', count=num_reviews)
    print(f"Fetched {len(review_data)} reviews.")

    # Extract specific fields
    extracted_data = []
    for review in review_data:
        extracted_review = {
            'userName': review['userName'],
            'content': review['content'],
            'score': review['score'],
            'reviewCreatedVersion': review.get('reviewCreatedVersion', ''),
            'at': review['at']
        }
        extracted_data.append(extracted_review)

    # Save extracted data to a CSV file
    with open(filepath, 'w', encoding='utf-8', newline='') as csvfile:
        fieldnames = ['userName', 'content', 'score', 'reviewCreatedVersion', 'at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()

        # Write extracted data
        writer.writerows(extracted_data)

    print(f"Extracted data saved to {filepath}")

if __name__ == "__main__":
    # Replace 'com.example.app' with the actual playstore_id of the app you want to scrape
    playstore_id = 'com.example.app'
    
    # Specify the number of reviews you want to fetch
    num_reviews = 1000  # Increase the number based on your requirements

    # Specify the output file path
    output_path = '/Users/rentsher/Desktop/Playstore_reviews_extracted.csv'

    # Save reviews to a CSV file with only the specified fields
    save_reviews_to_csv(playstore_id, filepath=output_path, num_reviews=num_reviews)
