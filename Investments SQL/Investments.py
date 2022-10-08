import sqlite3 as sq
import datetime as dt
import numpy as np
import os

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

def timecalc(from_str, to_str):
    date_from = dt.datetime.strptime(from_str, '%Y-%m-%d')
    date_to = dt.datetime.strptime(to_str, '%Y-%m-%d')
    days = (date_to - date_from).days
    return days

def add_investment():
    try:
        cursor.execute("SELECT * FROM investments")
        investment_code = str(input("Investment code: ")).upper()
        investment_amount = float(input("Investment amount: "))
        investment_cost = float(input("Cost of investment: "))
        investment_date = input("Date investment was purchased (YYYY-MM-DD): ")
        
        #using sum of assets as 'uniqe' key
        cursor.execute('SELECT investment_amount FROM investments')
        data = cursor.fetchall()

        number = 0
        for row in data:
            number += row[0]
        investment_key = int(number)

        #Inserting Data
        cursor.execute('SELECT * FROM investments')
        cursor.execute('INSERT INTO investments VALUES(?, ?, ?, ?, ?)', (investment_key, investment_code, investment_amount, investment_cost, investment_date))
        connection.commit()
    except:
        print('Invalid Value')

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
    cursor.execute('DELETE FROM investments WHERE investment_number=?', str(investment_key))
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
    sell_array = np.array([])
    key_array = np.array([])
    days_array = []
    row = 0

    for row in range(0 , len(data_array)):
        if str(data_array[row][1]) == str(investment_code):
            if float(data_array[row][2]) <= sold_amount:
                np.append(sell_array,[data_array[row][2],data_array[row][3]])
                np.append(days_array, timecalc(data_array[row][4], date_sold))
                sold_amount -= float(data_array[row][2])
                print(sold_amount)
                delete_var = str(data_array[row][0])
                cursor.execute("DELETE FROM investments WHERE investment_number=?", (delete_var,))
            else:
                np.append(sell_array, [data_array[row][2],data_array[row][3]])
                np.append(days_array, timecalc(data_array[row][4], date_sold))
                cursor.execute("UPDATE investments SET investment_amount=? WHERE investment_number=?", ((float(data_array[row][2]) - sold_amount), str(data_array[row][0])))
    connection.commit()

    total_cost = 0
    total_sold = 0
    tax = 0
    print(sell_array)

    for i in sell_array:
        total_cost += sell_array[i][0] * sell_array[i][1]
        total_sold += sell_array[i][0] * sold_for
        if days_array[i] >= 365:
            tax += (sell_array[i][0] * sold_for - sell_array[i][0] * sell_array[i][1]) * 0.5
        else:
            tax += sell_array[i][0] * sold_for - sell_array[i][0] * sell_array[i][1]
        print("days ", days_array[i], "total cost ", total_cost, "total sold ", total_sold)

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

Loop = True

while Loop == True:
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
        