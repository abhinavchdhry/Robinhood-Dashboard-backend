from __future__ import print_function
from Robinhood import Robinhood
from profit_extractor import profit_extractor
import getpass
import collections
import argparse
import ast
from dotenv import load_dotenv, find_dotenv
import os
import PortfolioAnalyser
from trade import Trade

logged_in = False
CSV_SEPARATOR = '|'

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

parser = argparse.ArgumentParser(
    description='Export Robinhood trades to a CSV file')
parser.add_argument(
    '--debug', action='store_true', help='store raw JSON output to debug.json')
parser.add_argument(
    '--exportcsv', action='store_true', help='export as CSV file')
parser.add_argument(
    '--profit', action='store_true', help='calculate profit for each sale')
parser.add_argument(
    '--dividends', action='store_true', help='export dividend payments')
parser.add_argument(
    '--start', help='start date', required=True)
parser.add_argument(
    '--end', help='end date', required=True)

args = parser.parse_args()
load_dotenv(find_dotenv())

print("Pulling trades. Please wait...")

fields = collections.defaultdict(dict)
trade_count = 0
queued_count = 0

#holds instrument['symbols'] to reduce API ovehead {instrument_url:symbol}
cached_instruments = {}

# fetch order history and related metadata from the Robinhood API
orders = Robinhood.get_instance().get_endpoint('orders')

# load a debug file
# raw_json = open('debug.txt','rU').read()
# orders = ast.literal_eval(raw_json)

# store debug
if args.debug:
    # save the CSV
    try:
        with open("debug.txt", "w+") as outfile:
            outfile.write(str(orders))
            print("Debug infomation written to debug.txt")
    except IOError:
        print('Oops.  Unable to write file to debug.txt')

# do/while for pagination
paginated = True
page = 0
while paginated:
    for i, order in enumerate(orders['results']):
        executions = order['executions']

        symbol = cached_instruments.get(order['instrument'], False)
        if not symbol:
            symbol = Robinhood.get_instance().get_custom_endpoint(order['instrument'])['symbol']
            cached_instruments[order['instrument']] = symbol

        fields[i + (page * 100)]['symbol'] = symbol

        for key, value in enumerate(order):
            if value != "executions":
                fields[i + (page * 100)][value] = order[value]

        fields[i + (page * 100)]['num_of_executions'] = len(executions)
        fields[i + (page * 100)]['execution_state'] = order['state']

        if len(executions) > 0:
            trade_count += 1
            fields[i + (page * 100)]['execution_state'] = ("completed", "partially filled")[order['cumulative_quantity'] < order['quantity']]
            fields[i + (page * 100)]['first_execution_at'] = executions[0]['timestamp']
            fields[i + (page * 100)]['settlement_date'] = executions[0]['settlement_date']
        elif order['state'] == "queued":
            queued_count += 1
    # paginate
    if orders['next'] is not None:
        page = page + 1
        orders = Robinhood.get_instance().get_custom_endpoint(str(orders['next']))
    else:
        paginated = False

# for i in fields:
#   print fields[i]
#   print "-------"

# check we have trade data to export
if trade_count > 0 or queued_count > 0:
    print("%d queued trade%s and %d executed trade%s found in your account." %
          (queued_count, "s" [queued_count == 1:], trade_count,
           "s" [trade_count == 1:]))
    # print str(queued_count) + " queded trade(s) and " + str(trade_count) + " executed trade(s) found in your account."
else:
    print("No trade history found in your account.")
    quit()

print(Color.BOLD + Color.CYAN + Color.UNDERLINE + '| Time                        | Stock | Total      | Filled   |' + Color.END)

analyser = PortfolioAnalyser.PortfolioAnalyser()

for i in fields:
    analyser.addTrade(Trade.fromOrderedRow(fields[i]))

analyser.total_profit()


if args.exportcsv:
    # CSV headers
    keys = fields[0].keys()
    keys = sorted(keys)
    csv = CSV_SEPARATOR.join(keys) + "\n"

    # CSV rows
    for row in fields:
        for idx, key in enumerate(keys):
            if (idx > 0):
                csv += CSV_SEPARATOR
            try:
                csv += str(fields[row][key])
            except:
                csv += ""

        csv += "\n"

    # choose a filename to save to
    print("Choose a filename or press enter to save to `robinhood.csv`:")
    try:
        input = raw_input
    except NameError:
        pass
    filename = input().strip()
    if filename == '':
        filename = "robinhood.csv"

    try:
        with open(filename, "w+") as outfile:
            outfile.write(csv)
    except IOError:
        print("Oops.  Unable to write file to ", filename)


if args.dividends:
    fields=collections.defaultdict(dict)
    dividend_count = 0
    queued_dividends = 0

    # fetch order history and related metadata from the Robinhood API
    dividends = Robinhood.get_instance().get_endpoint('dividends')


    paginated = True
    page = 0
    while paginated:
        for i, dividend in enumerate(dividends['results']):
            symbol = cached_instruments.get(dividend['instrument'], False)
            if not symbol:
                symbol = Robinhood.get_instance().get_custom_endpoint(dividend['instrument'])['symbol']
                cached_instruments[dividend['instrument']] = symbol

            fields[i + (page * 100)]['symbol'] = symbol

            for key, value in enumerate(dividend):
                if value != "executions":
                    fields[i + (page * 100)][value] = dividend[value]

            fields[i + (page * 100)]['execution_state'] = order['state']

            if dividend['state'] == "pending":
                queued_dividends += 1
            elif dividend['state'] == "paid":
                dividend_count += 1
        # paginate
        if dividends['next'] is not None:
            page = page + 1
            orders = Robinhood.get_instance().get_custom_endpoint(str(dividends['next']))
        else:
            paginated = False

    # for i in fields:
    #   print fields[i]
    #   print "-------"

    # check we have trade data to export
    if dividend_count > 0 or queued_dividends > 0:
        print("%d queued dividend%s and %d executed dividend%s found in your account." %
              (queued_dividends, "s" [queued_count == 1:], dividend_count,
               "s" [trade_count == 1:]))
        # print str(queued_count) + " queded trade(s) and " + str(trade_count) + " executed trade(s) found in your account."
    else:
        print("No dividend history found in your account.")
        quit()

    # CSV headers
    keys = fields[0].keys()
    keys = sorted(keys)
    csv = ','.join(keys) + "\n"

    # CSV rows
    for row in fields:
        for idx, key in enumerate(keys):
            if (idx > 0):
                csv += ","
            try:
                csv += str(fields[row][key])
            except:
                csv += ""

        csv += "\n"

    # choose a filename to save to
    print("Choose a filename or press enter to save to `dividends.csv`:")
    try:
        input = raw_input
    except NameError:
        pass
    filename = input().strip()
    if filename == '':
        filename = "dividends.csv"

    # save the CSV
    try:
        with open(filename, "w+") as outfile:
            outfile.write(csv)
    except IOError:
        print("Oops.  Unable to write file to ", filename)

if args.profit:
    profit_csv = profit_extractor(csv, filename)

