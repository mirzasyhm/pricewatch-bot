import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BookScraper:
    BASE_URL = "http://books.toscrape.com/"

    def __init__(self):
        self.session = requests.Session()

    def fetch_page(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"Error fetching page {url}: {e}")
            return None

    def parse_books(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        books_data = []
        
        books = soup.select('article.product_pod')
        for book in books:
            try:
                title = book.h3.a['title']
                # Price is usually in format "£51.77"
                price_text = book.select_one('p.price_color').text
                price = float(price_text.replace('£', '').replace('Â', ''))
                
                # Rating mapping
                rating_class = book.select_one('p.star-rating')['class'][1]
                ratings = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
                rating = ratings.get(rating_class, 0)
                
                availability = book.select_one('p.instock.availability').text.strip()
                
                books_data.append({
                    'title': title,
                    'price': price,
                    'currency': 'GBP', # Site default
                    'rating': rating,
                    'availability': availability,
                    'scraped_at': datetime.now().isoformat()
                })
            except Exception as e:
                logging.warning(f"Skipping a book due to parse error: {e}")
                continue
                
        return books_data

    def run(self, output_file='data/books_data.json'):
        logging.info(f"Starting scrape of {self.BASE_URL}")
        html = self.fetch_page(self.BASE_URL)
        if html:
            data = self.parse_books(html)
            logging.info(f"Extracted {len(data)} books.")
            
            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Save to local file (NDJSON format for BigQuery)
            with open(output_file, 'w') as f:
                for entry in data:
                    json.dump(entry, f)
                    f.write('\n')
            logging.info(f"Data saved to {output_file}")
            return data
        else:
            logging.error("Failed to retrieve data.")
            return []

if __name__ == "__main__":
    scraper = BookScraper()
    scraper.run()
