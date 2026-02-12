import requests
import time
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

class SportRadarClient:
    def __init__(self):
        self.api_key = os.getenv('SPORTRADAR_API_KEY')
        self.base_url = "https://api.sportradar.com/tennis/trial/v3/en"
        self.rate_limit_delay = 2.0  # Increased to 2 seconds
        self.last_request_time = None
        
    def _make_request(self, endpoint, retry_count=0, max_retries=3):
        """
        Make API request with error handling and rate limiting
        """
        # Enforce rate limiting
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - elapsed
                print(f"Rate limiting: waiting {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
        
        url = f"{self.base_url}/{endpoint}?api_key={self.api_key}"
        
        try:
            print(f"Requesting: {endpoint}")
            response = requests.get(url, timeout=30)
            self.last_request_time = time.time()
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                if retry_count < max_retries:
                    wait_time = 60 * (retry_count + 1)  # Exponential backoff
                    print(f"Rate limit hit. Waiting {wait_time} seconds... (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(wait_time)
                    return self._make_request(endpoint, retry_count + 1, max_retries)
                else:
                    print("Max retries reached. Please wait a few minutes and try again.")
                    raise
            else:
                print(f"HTTP Error {e.response.status_code}: {e}")
                raise
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def get_competitions(self):
        """Fetch all competitions data"""
        return self._make_request("competitions.json")
    
    def get_complexes(self):
        """Fetch all complexes data"""
        return self._make_request("complexes.json")
    
    def get_rankings(self):
        """Fetch competitor rankings (doubles)"""
        return self._make_request("rankings.json")