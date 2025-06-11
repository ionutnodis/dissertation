#Function to search for a ticker symbol using the Alpha Vantage SYMBOL_SEARCH endpoint
""

import requests
import csv
from io import StringIO
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")

def ticker_search_csv(keywords: str, api_key: str):
    """
    Perform a ticker symbol search using Alpha Vantage SYMBOL_SEARCH endpoint.
    Parses CSV results into a list of dictionaries.
    """
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'SYMBOL_SEARCH',
        'keywords': keywords,
        'apikey': api_key,
        'datatype': 'csv'  # explicitly request CSV format
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")

    csv_data = response.text
    reader = csv.DictReader(StringIO(csv_data))
    results = [row for row in reader]

    return results

#Example usage
api_key = os.getenv("API_KEY")
keyword = "apple"
matches = ticker_search_csv(keyword, api_key)

for match in matches:
    print(f"{match['symbol']} — {match['name']} ({match['region']})")