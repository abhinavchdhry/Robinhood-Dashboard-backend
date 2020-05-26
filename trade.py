from dateutil import parser as dateparser

class Trade:

    @staticmethod
    def fromOrderedRow(row):
        return Trade(
            row.get('symbol'),
            row.get('quantity'),
            row.get('average_price', 0.0),
            row.get('side'),
            row.get('last_transaction_at'),
            row.get('type'),
            row.get('state')
        )

    @staticmethod
    def cmpByTime(t1, t2):
        return (t1.update_time > t2.update_time) - (t1.update_time < t2.update_time)

    def __init__(self, symbol, quantity, avg_price, side, update_time, type, state):
        self.symbol = symbol
        self.quantity = float(quantity)
        self.avg_price = float(avg_price) if avg_price and avg_price != 'None' else None
        self.side = side
        self.update_time = dateparser.parse(update_time) if update_time else None
        self.type = type
        self.state = state

    def isFilled(self):
        return self.state == 'filled'

    def isCancelled(self):
        return self.state == 'cancelled'

    def isRejected(self):
        return self.state == 'rejected'

    def __str__(self):
        return "<Trade stock={} quantity={} price={} side={} type={} state={} time={} />".format(
            self.symbol,
            self.quantity,
            self.avg_price,
            self.side,
            self.type,
            self.state,
            self.update_time
        )
