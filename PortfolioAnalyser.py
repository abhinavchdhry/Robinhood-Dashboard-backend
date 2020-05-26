from collections import defaultdict
from trade import Trade
from Robinhood import Robinhood

class PortfolioAnalyser:
    def __init__(self):
        self.portfolio = defaultdict(list)

    def addTrade(self, trade):
        if trade.isFilled():
            self.portfolio[trade.symbol].append(trade)

    def total_profit(self):
        profit = 0.0
        for symbol in self.portfolio:
            profit_for_symbol = 0.0
            share_quantity = 0.0

            trades = sorted(self.portfolio[symbol], key=lambda t: t.update_time)
            for trade in trades:
                print(trade)
                if trade.side == 'buy':
                    profit_for_symbol -= trade.quantity * trade.avg_price
                    share_quantity += trade.quantity
                elif share_quantity > 0.0:
                    profit_for_symbol += trade.quantity * trade.avg_price
                    share_quantity -= trade.quantity
                print('Profit for symbol: ' + str(profit_for_symbol))
            print('\n')
            if share_quantity > 0:
                last_price = float(Robinhood.get_instance().quote_data(symbol)['last_trade_price'])
                current_value = last_price * share_quantity
                profit_for_symbol += current_value

            profit += profit_for_symbol

        print("Total profit: " + str(profit))