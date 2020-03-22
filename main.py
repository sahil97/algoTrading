import os
from os.path import join, dirname
from dotenv import load_dotenv

# Custom modules
from market import Market

# Loading API key from env
# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')
 
# Load file from the path.
try:
    load_dotenv(dotenv_path)
    API_KEY = os.getenv('API_KEY')
except Exception as e:
    print("Error in loading env file.")
    print(e)

if __name__ == '__main__':

    market = Market(API_KEY)
    print(market.get_market_data())