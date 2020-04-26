class Strategies:

    @staticmethod
    def maStrategy(df, i:int):
        """
        if price is below 10% below the slow MA, return True
        """

        buy_price = 1 * df['slow_sma'][i]
        if buy_price == df['close'][i]:
            return min(buy_price, df['high'][i])

        return False

    @staticmethod
    def bollStrategy(df, i:int):
        """
        If price is 5% below lower boll band, return True
        """
        
        buy_price = 1 * df['low_boll'][i]
        if buy_price == df['close'][i]:
            return min(buy_price, df['high'][i])

        return False