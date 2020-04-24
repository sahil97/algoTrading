import pandas as pd
import requests
import json

from pyti.smoothed_moving_average import smoothed_moving_average as sma

from plotly.offline import plot
import plotly.graph_objs as go


class TradingModel:

    def __init__(self, symbol):
        self.symbol = symbol
        self.df = self.get_data()

    def get_data(self):
        # Defining Urls
        base = 'https://api.binance.com'
        endpoint = '/api/v3/klines'
        params = '?&symbol=' + self.symbol + '&interval=1h'

        url = base + endpoint + params

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

        # adding moving averages
        df['fast_sma'] = sma(df['close'].tolist(), 10)
        df['slow_sma'] = sma(df['close'].tolist(), 30)

        return df

    def plot_data(self, buy_signals = []):
        df = self.df

        # plotting candlestick
        candle = go.Candlestick(
            x = df['time'],
            open = df['open'],
            close = df['close'],
            high = df['high'],
            low = df['low'],
            name = "Candlesticks"
        )

        # plot FMA
        fsma = go.Scatter(
            x = df['time'],
            y = df['fast_sma'],
            name = "Fast sma",
            line = dict(color = ('rgba(102, 207, 255, 50)'))
        )

        # plot SMA
        ssma = go.Scatter(
            x = df['time'],
            y = df['slow_sma'],
            name = "Fast sma",
            line = dict(color = ('rgba(102, 207, 102, 50)'))
        )
        
        data = [candle, ssma, fsma]

        if buy_signals:
            buys = go.Scatter(
                x = [item[0] for item in buy_signals],
                y = [item[1] for item in buy_signals],
                name = "Buy Signals",
                mode = "markers"
            )

            sells = go.Scatter(
                x = [item[0] for item in buy_signals],
                y = [item[1]*1.02 for item in buy_signals],
                name = "Sell Signals",
                mode = "markers"
            )
            data = [candle, ssma, fsma, buys, sells]


        layout = go.Layout(title = self.symbol)
        fig = go.Figure(data = data, layout = layout)

        plot(fig, filename = self.symbol)

    def strategy(self):
        df = self.df
        
        buy_signals = []

        for i in range(1, len(df)):
            if df['slow_sma'][i] > df['low'][i] and (df['slow_sma'][i] - df['low'][i]) > 0.03 * df['low'][i]:
                buy_signals.append([df['time'][i], df['low'][i]])

        self.plot_data(buy_signals = buy_signals)


def Main():
    symbol = 'BTCUSDT'
    model  = TradingModel(symbol)
    model.strategy()

if __name__ == '__main__':
    Main()