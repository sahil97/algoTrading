import requests
import json
import time
import decimal
import hmac
import pandas as pd
import hashlib


binance_keys = {
    'api_key': '',
    'secret_key': ''
}

class Binance:

    def __init__(self):
        self.base = 'https://api.binance.com'

        self.endpoints = {
            'order': '',
            'testOrder': '',
            'allOrder': '',
            'klines': '/api/v3/klines',
            'exchangeInfo': '/api/v3/exchangeInfo'
        }

        self.headers = {'X-MBX-APIKEY': binance_keys['api_key']}

    def GetTradingSymbols(self, quoteAssets: list = None):
        url = self.base + self.endpoints['exchangeInfo']

        try:
            response = requests.get(url)
            data = json.loads(response.text)
        except Exception as e:
            print("Exception occured when trying to access: " + url)
            print(e)
            return []
        
        symbols_list = []
        
        for pair in data['symbols']:
            if pair['status'] == 'TRADING':
                if quoteAssets != None and pair['quoteAsset'] in quoteAssets:
                    symbols_list.append(pair['symbol'])
        return symbols_list
        
    def GetSymbolData(self, symbol: str, interval: str):
        """
        Gets trading data for one symbol

        params:
        __
            symbol str:     The symbol for which to get the trading data

            interval str:   The interval on which to get the trading data
                minutes     '1m', '3m', '5m', '15m', '30m'
                hours       '1h', '2h', '4h', '6h', '8h', '12h'
                days        '1d', '3d'
                weeks       '1w'
                months      '1M'
        """


        # Defining Urls
        params = '?&symbol=' + symbol + '&interval=' + interval

        url = self.base + self.endpoints['klines'] + params

        # downloading data
        data = requests.get(url)
        dictionary = json.loads(data.text)

        # converting data into dataframe and dropping unncessary columns
        df = pd.DataFrame.from_dict(dictionary)
        df = df.drop(range(6,12), axis=1)

        # renaming columns
        col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
        df.columns = col_names

        for col in col_names:
            df[col] = df[col].astype(float)

        df['data'] = pd.to_datetime(df['time'] * 1000000, infer_datetime_format = True)


        return df

    def PlaceOrder(self, symbol:str, side:str, type:str, quantity:float = 0, price:float = 0, test:bool = True):
        """
        Places order on the Exchange

        params:
        __
            
            Symbol str:     The symbol for which to get the trading data

            side str:       The side of the order 'BUY' or 'SELL'
            
            type str:       The type, 'LIMIT', 'MARKET', 'STOP_LOSS'

            quantity float: ....

        """

        params = {
            'symbol': symbol,
            'side': side,       # BUY / SELL
            'type': type,       # MARKET, LIMIT, STOP LOSS etc.
            'quantity': quantity,
            'price': self.floatToString(price),
            'recvWindow': 5000,
            'timestamp': int(round(time.time() * 1000))
        }


        if type != 'MARKET':
            params['timeInForce'] = 'GTC'
            params['prce'] = self.floatToString(price)

        self.signRequest(params)

        if test:
            url = self.base + self.endpoints['testOrder']
        else:
            url = self.base + self.endpoints['order']

        try:
            response = requests.post(
                url,
                params=params,
                headers = self.headers
            )
            data = response.text

        except Exception as e:
            print("Exception occured when trying to place order")
            print(e)
            data = {'code': -1, 'msg': e}
            return None

        return json.loads(data)
        
    def CancelOrder(self, symbol: str, orderId: str):
        """
        Cancels order based on orderId
        """

        params = {
            'symbol': symbol,
            'orderId': orderId,
            'recvWindow': 5000,
            'timestamp': int(round(time.time() * 1000))
        }

        self.signRequest(params)

        url = self.base + self.endpoints['order']

        try:
            response = requests.delete(
                url,
                params = params,
                headers = self.headers
            )
            data = response.text
        except Exception as e:
            print("Exception occured when trying to place order")
            print(e)
            data = {'code': -1, 'msg': e}
            return None

        return json.loads(data)
        

    def GetOrderInfo(self, symbol: str, orderId: str):
        """
        Gets info about an order on a symbol based on orderId
        """
        
        params = {
            'symbol': symbol,
            'orderId' : orderId,
            'recvWindow': 5000,
            'timestamp': int(round(time.time()*1000))
		}
        
        self.signRequest(params)
        
        url = self.base + self.endpoints['order']

        try:
            response = requests.get(
                url,
                params = params,
                headers = self.headers
            )
            data = response.text
        except Exception as e:
            print("Exception occured when trying to place order")
            print(e)
            data = {'code': -1, 'msg': e}
            return None
            
        return json.loads(data)
        
    def GetAllOrderInfo(self, symbol:str):
        """
        Gets info about all order on a symbol
        """
        
        params = {
            'symbol': symbol,
            'timestamp': int(round(time.time()*1000))
        }
        self.signRequest(params)
        
        url = self.base + self.endpoints['allOrders']
        
        try: 
            response = requests.get(
                url,
                params = params,
                headers = self.headers
            )
            data = response.text
        except Exception as e:
            print("Exception occured when trying to place order")
            print(e)
            data = {'code': -1, 'msg': e}
            return None
        
        return json.loads(data)


    def floatToString(self, f:float):
        """
        Converts the given float to a string,
        without resorting to the scientific notation
        """
        ctx = decimal.Context()
        ctx.prec = 12
        d1 = ctx.create_decimal(repr(f))
        return format(d1, 'f')
        
    def signRequest(self, params:dict):
        """
        Signs the request to the Binance API
        """
        query_string = '&'.join(["{}={}".format(d, params[d]) for d in params])
        signature = hmac.new(binance_keys['secret_key'].encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        params['signature'] = signature.hexdigest()