#! /usr/bin/env python

import sqlite3 as sq
import datetime as dt
import numpy as np
import os
import random

### SQL ###

exist_boolean = os.path.exists('investments.db')
if exist_boolean == False:
    connection = sq.connect('investments.db')
    cursor = connection.cursor()

    sql_command = """CREATE TABLE investments (
        investment_number INTEGER PRIMARY KEY,
        investment_code VARCHAR(3),
        investment_amount FLOAT,
        investment_cost FLOAT,
        date DATE
    );"""

    cursor.execute(sql_command)

else:
    connection = sq.connect('investments.db')
    cursor = connection.cursor()

### FUNCTIONS ###

def help():
    print('help     | Displays list of commands')
    print('add      | Adds investment to database')
    print('remove   | Removes an investment from database using investment key')
    print('display  | shows all current assets in database')
    print('exit     | exits program')

def timecalc(from_str, to_str):
    date_from = dt.datetime.strptime(from_str, '%Y-%m-%d')
    date_to = dt.datetime.strptime(to_str, '%Y-%m-%d')
    days = (date_to - date_from).days
    return days

def add_investment():
    try:
        cursor.execute("SELECT investment_number FROM investments")
        investment_code = str(input("Investment code: ")).upper()
        investment_amount = float(input("Investment amount: "))
        investment_cost = float(input("Cost of investment: "))
        investment_date = str(input("Date investment was purchased (YYYY-MM-DD): "))
        
    except:
        print('Invalid Value')
        pass

    #Generating Random Investment Key
    key_generated = False
    match = False
    data = cursor.fetchall()
    data = np.array(data, dtype = int).flatten()
    print(data)
        
    while key_generated == False:
        print("Generating investment key...")
        investment_key = random.randint(1, 10000)

        for row in range(0, len(data)):
            key_check = int(data[row])
            if key_check == investment_key:
                match = True

            if match != True:
                key_generated = True

    #Inserting Data
    print('Inserting into database...')
    cursor.execute('SELECT * FROM investments')
    cursor.execute('INSERT INTO investments VALUES(?, ?, ?, ?, ?)', (investment_key, investment_code, investment_amount, investment_cost, investment_date))
    connection.commit()
    

def display():
    cursor.execute("SELECT * FROM investments")
    sql_length = cursor.fetchall()
    print("Key | Code | Amount | Cost | Date")
    for row in sql_length:
        print(row)


def remove():
    i = 1
    while i == 1:
        try:
            investment_key = int(input("Investment key: "))
            confirmation = str(input("Is this correct? (Y/N): ")).upper()
            if confirmation == "Y":
                i = 0
        except:
            print("Invalid Value")
    investment_key = str(investment_key)
    cursor.execute("DELETE FROM investments WHERE investment_number=?", (investment_key,))
    connection.commit()
 
def sell():
    try:
        investment_code = str(input('Investment code:')).upper()
        sold_amount = float(input('Amount sold:'))
        sold_for = float(input('Sold for:'))
        date_sold = input("Date sold (YYYY-MM-DD): ")
        fee_type = str(input('Is the broker fee a percentage or fixed?: ')).lower()
    except:
        print('Invalid Value')
        pass
    
    cursor.execute('SELECT * FROM investments ORDER BY date DESC')
    data = cursor.fetchall()

    data_array = np.array(data)
    data_array = data_array[data_array[:, 4].argsort()]
    days_array = []
    sell_array = np.array([['Amount', 'Cost']])
    row = 0

    for row in range(0 , len(data_array)):
        if str(data_array[row][1]) == str(investment_code):
            if float(data_array[row][2]) <= sold_amount:
                temp_array = np.array([[data_array[row][2], data_array[row][3]]])
                sell_array = np.append(sell_array, temp_array, axis=0)
                days_array = np.append(days_array, timecalc(data_array[row][4], date_sold))
                sold_amount -= float(data_array[row][2])
                to_be_deleted = str(data_array[row][0])
                cursor.execute("DELETE FROM investments WHERE investment_number=?", (to_be_deleted,))
            else:
                temp_array = np.array([[data_array[row][2], data_array[row][3]]])
                sell_array = np.append(sell_array, temp_array, axis=0)
                days_array = np.append(days_array, timecalc(data_array[row][4], date_sold))
                cursor.execute("UPDATE investments SET investment_amount=? WHERE investment_number=?", ((float(data_array[row][2]) - sold_amount), str(data_array[row][0])))
    connection.commit()

    total_cost = 0
    total_sold = 0
    tax = 0
    print(sell_array)

    for i in range(1, len(sell_array)):
        
        amount = float(sell_array[i][0])
        cost = float(sell_array[i][1])

        total_cost += amount * cost
        total_sold += amount * sold_for

        if int(days_array[i - 1]) >= 365:
            tax += (amount * sold_for - amount * cost) * 0.5
        else:
            tax += amount * sold_for - amount * cost
        print("days ", days_array[i - 1], "total cost ", total_cost, "total sold ", total_sold)

    if fee_type == 'percentage':
        fee = float(input("Fee percentage (decimal): "))
        profit = total_sold - total_cost - (total_sold * fee)
    elif fee_type == 'fixed':
        fee = float(input("Dollar value of fee: "))
        profit = total_sold - total_cost - fee
    else:
        print("Invalid fee type. Assuming fee = $0...")
        profit = total_sold - total_cost
    print('Profit: ', profit)
    print('Tax record: ', tax)  
    
        

### MENU ###

loop = True

while loop == True:
    user_command = input("Command: ").lower()

    if user_command == 'add':
        add_investment()
    if user_command == 'exit':
        connection.close()
        exit()
    if user_command == 'display':
        display()
    if user_command == 'remove':
        remove()
    if user_command == 'sell':
        sell()
    if user_command == 'help':
        help()
        