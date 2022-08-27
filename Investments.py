#!/usr/bin/env python3
from calendar import c
import pandas as pd
import datetime as dt
import re

#Date Calculation

def timecalc(from_str, to_str):
    date_from = dt.datetime.strptime(from_str, '%Y-%m-%d')
    date_to = dt.datetime.strptime(to_str, '%Y-%m-%d')
    days = (date_to - date_from).days
    return days

#Options

def new():
    #For adding new investments

    code = input('Investment code: ').upper()
    amount = input('Amount of investment purchased: ')
    cost = input('Cost: ')
    date = input('Date of Purchase (YYYY-M-D): ')
    temp_data = {'Investment' : code, 'Amount' : float(amount), 'Cost' : float(cost), 'Date' : date}

    #Adding data to csv file
    temp_df = pd.DataFrame(temp_data, index = [0], columns = ['Investment', 'Amount', 'Cost', 'Date'])
    temp_df.to_csv('Assets.csv', mode = 'a', header = False, index = False)


def help():
    #Command List

    print('')
    print('add            | Lets you add an investment')
    print('exit           | Stops this script')
    print('assets         | Prints all current assets')
    print('remove         | Removes an investment')
    print('modify         | Modifies an investment')
    print('search         | searchs for and displays specified')
    print('total          | displays total amount of a specified asset')
    print('sell           | deletes sold assets and calculates profit / capital gains')

def remove(assets, code, date, cost):
    #Removes specified row

    investment = assets['Investment']
    datelist = assets['Date']
    cost_list = assets['Cost']

    for i in range(0, len(assets)):
        if investment[i] == code and datelist[i] == date and cost_list[i] == cost:
            #Removes row in CSV file
            assets = assets.drop(i)
            assets.to_csv('Assets.csv', mode = 'w', header = True, index = False)
        

def modify(assets, code, date, cost, new_amount, new_cost):
    #For modifying current investments
    
    investment = assets['Investment']
    datelist = assets['Date']
    cost_list = assets['Cost']

    for i in range(0, len(assets)):
        if investment[i] == code and datelist[i] == date and cost_list[i] == cost:
            assets.loc[i, ['Amount']] = new_amount
            assets.loc[i, ['Cost']] = new_cost
            assets.to_csv('Assets.csv', mode = 'w', header = True, index = False)
       

def search(assets):
    #Searches the CSV for a specified investment
    
    search_item = input('Search Query: ')
    datelist = assets['Date']
    counter = 0
    r = re.compile('.*-.*-.*')
    
    if r.match(search_item) is not None:
        print('')
        print(assets.loc[assets['Date'] == search_item])

    try:
        search_item = float(search_item)
    except:
        pass

    if type(search_item) == float:
        number_type = input('Amount or Cost?: ').lower()
        if number_type == 'amount':
            print(assets.loc[assets['Amount'] == search_item])
        elif number_type == 'cost':
            print(assets.loc[assets['Cost'] == search_item])
        else:
            print("Didn't type 'cost' or amount'")
    try:

        if r.match(search_item) is None and type(search_item) == str:
            search_item = search_item.upper()
            print('')
            print(assets.loc[assets['Investment'] == search_item])
    except:
        pass

def total(assets):
    #Returns total amount of an asset
    investment = input('Investment Code: ').upper()
    total_amount = 0

    for i in range(0, len(assets)):
        if assets.iloc[i]['Investment'] == investment:
            total_amount += assets.iloc[i]['Amount']
        
    print(total_amount)

def profit_calculator(assets):
    #Calculates profit

    investment = input('Investment Code: ').upper()
    sale_amount = float(input('Amount: '))
    sold_for = float(input('Amount Sold for (per investment):'))
    percent_fee = str(input('Is the broker fee a percentage? (yes or no): ')).lower()
    profit = float(0)
    total_amount = float(0)
    sorted = assets.sort_values(by = 'Date')
    price_array = []
    
    #broker fee
    if percent_fee == 'yes':
        broker_fee = float(input('Enter fee percentage as a decimal: '))
    else:
        broker_fee = float(input('Enter broker fee: '))

    #Calculates asset data for calculation
    for i in range(0, len(sorted) - 1):
        if sorted.iloc[i]['Investment'] == investment:
            if sorted.iloc[i]['Amount'] >= sale_amount:
                total_amount = sale_amount
                price_array.append([total_amount, sorted.iloc[i]['Cost'], sorted.iloc[i]['Date']])
                i = len(sorted) + 1

            elif sorted.iloc[i]['Amount'] < sale_amount:
                total_amount = sorted.iloc[i]['Amount']
                sale_amount = sale_amount - sorted.iloc[i]['Amount']
                price_array.append([total_amount, sorted.iloc[i]['Cost'], sorted.iloc[i]['Date']])

     #Actually calculates the profit of the sale   
    cost_sum = 0
    for i in range(0 , len(price_array) - 1):
        #'cost_sum' is the total cost of the assets being sold
        cost_sum += price_array[i][0]*price_array[i][1]
        #in this case variable 'profit' is just the total amount of stock sold
        profit += price_array[i][0]

    if percent_fee == 'yes':
        broker_fee = profit * broker_fee
    profit = profit * sold_for - cost_sum - broker_fee
    print('Estimated profit: ', profit)


def sell(assets):
    #Script to record the selling of assets and update the CSV sheet

    investment_code = input('Investment code: ').upper()
    sale_amount = float(input('Amount Sold: '))
    sold_for = float(input('Sold for (Per investment): '))
    percentage_fee = str(input('Is the broker fee a percentage? (yes or no): ')).lower
    change_amount = float(0)
    sorted_assets = assets.sort_values(by = 'Date')
    price_array = []

    #broker fee calculation
    if percentage_fee == 'yes':
        broker_fee = input('Enter broker fee percentage as a decimal: ')
    else:
        broker_fee = float(input('Enter broker fee: '))
    
    #Code that collects data and changes spreadsheet
    for i in range(0, len(sorted_assets) - 1):
        if sorted_assets.iloc[i]['Investment'] == investment_code:
            amount = sorted_assets.iloc[i]['Amount']
            if amount <= sale_amount:
                change_amount = amount
                sale_amount -= change_amount
                price_array.append([ change_amount, sorted_assets.iloc[i]['Cost'], sorted_assets.iloc[i]['Date']])
                #Modifying Spreadsheet
                sorted_assets = sorted_assets.drop(i)
                i -= 1
        
            elif amount > sale_amount:
                change_amount = amount - sale_amount
                price_array.append([sale_amount, sorted_assets.iloc[i]['Cost'], sorted_assets.iloc[i]['Date']])
                #modifying Spreadsheet
                sorted_assets.loc[i, ['Amount']] = change_amount
                break
    
    sorted_assets.to_csv('Assets.csv', mode = 'w', header = True, index = False)

    #Profit and capital gains calculations
    cost_sum = 0
    capital_gains = 0
    profit = 0

    for x in range(0, len(price_array) - 1):
        cost_sum = price_array[x][0] * price_array[x][1]
        profit += price_array[x][0] * sold_for
        temp_var = price_array[x][0] * sold_for
        days = timecalc(price_array[x][2], str(dt.date.today()))
        
        if days >= 365:
            capital_gains += (temp_var - cost_sum) / 2
        else:
            capital_gains += temp_var - cost_sum
    
    if percentage_fee == 'yes':
        broker_fee = broker_fee * profit
        
    profit = profit - cost_sum - broker_fee

    print('Profit made: ', profit)
    print('Reported capital gains: ', capital_gains)



#Starting prompt
i = 1
print('\nWelcome to your investment storage and capital gains tracker!')
print('Type "help" to list commands')
while i == 1:
    #Reloads / Loads CSV Data or creates a new csv if one doesn't already exist
    try:
        assets = pd.read_csv('Assets.csv')
    except:
        open('Assets.csv', 'w')
        assets = pd.DataFrame(columns = ['Investment', 'Amount', 'Cost', 'Date'])
        assets.to_csv('Assets.csv', mode = 'w', header = True, index = False)

    print('')
    option = input('What would you like to do?: ').lower()
    if option == 'exit':
        exit()
    if option == 'add':
        new()
    if option == 'assets':
        print(assets)
        print('\nTotal Investments:', len(assets))
    if option == 'help':
        help()
    if option == 'remove':
        code = input('Investment code: ').upper()
        date = input('Investment date (YYYY-M-D): ')
        cost = float(input('Cost of investment: '))
        remove(assets, code, date, cost)
    if option == 'modify':
        code = input('Investment code: ').upper()
        date = input('Investment date (YYYY-M-D): ')
        cost = float(input('Original Cost: '))
        new_amount = input('New Investment Amount: ')
        new_cost = input('New Investment Cost: ')
        modify(assets, code, date, cost, new_amount, new_cost)
    if option == 'search':
        search(assets)
    if option == 'total':
        total(assets)
    if option == 'profit calculator':
        profit_calculator(assets)
    if option == 'sell':
        sell(assets)
    
    