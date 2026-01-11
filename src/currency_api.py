import requests
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CurrencyFetcher:
    API_URL = "https://api.frankfurter.app/latest"

    def __init__(self, from_currency="USD", to_currency="EUR"):
        self.from_currency = from_currency
        self.to_currency = to_currency

    def fetch_rate(self):
        try:
            params = {'from': self.from_currency, 'to': self.to_currency}
            response = requests.get(self.API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            rate = data['rates'].get(self.to_currency)
            return rate
        except requests.RequestException as e:
            logging.error(f"Error fetching currency rate: {e}")
            return None

    def run(self, output_file='data/currency_rate.json'):
        rate = self.fetch_rate()
        if rate:
            output_data = {
                'base': self.from_currency,
                'target': self.to_currency,
                'rate': rate,
                'fetched_at': datetime.now().isoformat()
            }
            
            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(output_data, f)
                f.write('\n')
            logging.info(f"Rate {rate} saved to {output_file}")
            return output_data
        else:
            return None

if __name__ == "__main__":
    fetcher = CurrencyFetcher()
    fetcher.run()
