import dateutil.parser

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class OptionOrder:

    FORMAT_STRING = "{:8} | {:10} | {:10} | {:20} | {:30}"

    def __init__(self, jsonData):
        self.chain_symbol = jsonData.get("chain_symbol")
        self.direction = jsonData.get("direction")
        self.opening_strategy = jsonData.get("opening_strategy")
        self.processed_premium = float(jsonData.get("processed_premium"))
        self.processed_quantity = float(jsonData.get("processed_quantity"))
        self.updated_at = dateutil.parser.parse(jsonData.get("updated_at"))

    def __str__(self):
        return Color.BOLD + self.FORMAT_STRING.format(self.chain_symbol, self.processed_quantity, self.processed_premium, self.direction, str(self.updated_at)) + Color.END

    @staticmethod
    def header():
        return Color.BOLD + Color.CYAN + Color.UNDERLINE + OptionOrder.FORMAT_STRING.format("Symbol", "Quantity", "Premium", "Direction", "Time") + Color.END