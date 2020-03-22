from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

class Market:
    """ Market class which will contain all the necessary methods to get live market prices and may further support adding trades. """

    def __init__(self, API_KEY:str = None):
        if(API_KEY):
            self.API_KEY = API_KEY
        else:
            raise Exception("NO Api Key. Please provide an API key. ")
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.parameters = {
            'start':'1',
            'limit':'5',
            'convert':'USD'
        }
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': str(self.API_KEY),
        }

    def get_market_data(self):
        """ Method to get current data for crypto currencies from market. """
        session = Session()
        session.headers.update(self.headers)
        
        try:
            response = session.get(self.url, params= self.parameters)
            data = json.loads(response.text)
            return data
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)