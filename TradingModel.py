import pandas as pd
import requests
import json

from pyti.smoothed_moving_average import smoothed_moving_average as sma
from pyti.bollinger_bands import lower_bollinger_band as lbb


from plotly.offline import plot
import plotly.graph_objs as go

from Binance import Binance

class TradingModel:

    def __init__(self, symbol, timeframe: str = '4h'):
        self.symbol = symbol
        self.exchange = Binance()
        self.timeframe = timeframe
        self.df = self.exchange.GetSymbolData(symbol, self.timeframe)
        self.last_price = self.df['close'][len(self.df['close']) - 1]

        try:
            self.df['fast_sma'] = sma(self.df['close'].tolist(), 10)
            self.df['slow_sma'] = sma(self.df['close'].tolist(), 30)
            self.df['low_boll'] = sma(self.df['close'].tolist(), 14)
        except Exception as e:
            print("Exception occured in computing identifiers on ", self.symbol)
            print(e)
            return None

    def plot_data(self, buy_signals = False, sell_signals = False, plot_title = "", indicators = []):
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

        data = [candle]

        if indicators.__contains__('fast_sma'):
            # plot FMA
            fsma = go.Scatter(
                x = df['time'],
                y = df['fast_sma'],
                name = "Fast sma",
                line = dict(color = ('rgba(102, 207, 255, 50)'))
            )
            data.append(fsma)

        if indicators.__contains__('slow_sma'):
            # plot SMA
            ssma = go.Scatter(
                x = df['time'],
                y = df['slow_sma'],
                name = "Fast sma",
                line = dict(color = ('rgba(102, 207, 102, 50)'))
            )
            data.append(ssma)

        if indicators.__contains__('low_boll'):
            lowbb = go.Scatter(
                x = df['time'],
                y = df['low_boll'],
                name = "Lower Bollinger Band",
                line = dict(color = ('rgba(255, 102, 207, 50)'))
            )
            data.append(lowbb)
    
        if buy_signals:
            buys = go.Scatter(
                x = [item[0] for item in buy_signals],
                y = [item[1] for item in buy_signals],
                name = "Buy Signals",
                mode = "markers",
                marker_size = 20
            )
            data.append(buys)

        if sell_signals:
            sells = go.Scatter(
                x = [item[0] for item in sell_signals],
                y = [item[1] for item in sell_signals],
                name = "Sell Signals",
                mode = "markers",
                marker_size = 20
            )
            data.append(sells)


        layout = go.Layout(title = plot_title)
        fig = go.Figure(data = data, layout = layout)

        plot(fig, filename = 'graphs/' + plot_title + '.html')