from __future__ import print_function
from Robinhood import Robinhood
from login_data import collect_login_data
from dataclasses import make_dataclass
import collections
import argparse
import datetime
from dotenv import load_dotenv, find_dotenv
import pandas as pd
from option_order import OptionOrder

logged_in = False

parser = argparse.ArgumentParser(
    description='Export Robinhood trades to a CSV file')
parser.add_argument(
    '--debug', action='store_true', help='store raw JSON output to debug.json')
parser.add_argument(
    '--username', default='', help='your Robinhood username')
parser.add_argument(
    '--password', default='', help='your Robinhood password')
parser.add_argument(
    '--mfa_code', help='your Robinhood mfa_code')
parser.add_argument(
    '--device_token', help='your device token')
parser.add_argument(
    '--profit', action='store_true', help='calculate profit for each sale')
args = parser.parse_args()
username = args.username
password = args.password
mfa_code = args.mfa_code
device_token = args.device_token

load_dotenv(find_dotenv())

robinhood = Robinhood()

# login to Robinhood
logged_in = collect_login_data(robinhood_obj=robinhood, username=username, password=password, device_token=device_token, mfa_code=mfa_code)

print("Pulling trades. Please wait...")

fields = collections.defaultdict(dict)
trade_count = 0
queued_count = 0

# fetch order history and related metadata from the Robinhood API
orders = robinhood.get_endpoint('optionsOrders');

# do/while for pagination
paginated = True
page = 0
row = 0
total_profit = 0.0

OptionOrderDataclass = make_dataclass("OptionOrderDataclass", [("Symbol", str), ("Premium", float), ("Time", datetime.datetime), ("Week", int)])

print(OptionOrder.header())
df_data = []
while paginated:
    for i, order in enumerate(orders['results']):
        order = OptionOrder(order)
        print(order)
        profit = (0-order.processed_premium) if order.direction == "debit" else order.processed_premium
        total_profit += profit
        df_data.append(OptionOrderDataclass(order.chain_symbol, profit, order.updated_at, order.updated_at.isocalendar()[1]))

    # paginate
    if orders['next'] is not None:
        page = page + 1
        orders = robinhood.get_custom_endpoint(str(orders['next']))
    else:
        paginated = False

print(OptionOrder({"chain_symbol": "Total", "processed_premium": total_profit, "direction": "debit", "processed_quantity": 0.0, "updated_at": str(datetime.datetime.utcnow())}))

df = pd.DataFrame(df_data)
df.groupby("Week").sum().unstack().plot()