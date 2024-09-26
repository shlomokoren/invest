import tkinter as tk
from tkinter import ttk, messagebox
import json


# Load the JSON data from stocks.json file
def load_json_data():
    with open("data_invest.json", "r") as f:
        return json.load(f)


# Save the JSON data to stocks.json file
def save_json_data(data):
    with open("data_invest.json", "w") as f:
        json.dump(data, f, indent=4)


# Populate the listbox based on selected action
def populate_symbols(event):
    selected_action = action_combobox.get()
    symbol_listbox.delete(0, tk.END)

    for stock in stocks_data:
        if stock['action'] == selected_action:
            symbol_listbox.insert(tk.END, stock['symbol'])


# Display the stock details when a symbol is selected
def display_stock_details(event):
    if symbol_listbox.curselection():
        selected_symbol = symbol_listbox.get(symbol_listbox.curselection())

        for stock in stocks_data:
            if stock['symbol'] == selected_symbol:
                range_entry.delete(0, tk.END)
                range_entry.insert(0, stock['range'])

                profit_entry.delete(0, tk.END)
                profit_entry.insert(0, stock.get('takeProfitPercentage', ''))

                check_profit_var.set(stock['isNeedToCheckTakeProfit'])

                quantity_entry.delete(0, tk.END)
                quantity_entry.insert(0, stock.get('quantity', ''))

                account_entry.delete(0, tk.END)
                account_entry.insert(0, stock['account'])
                break


# Update the stock details and save to JSON file
def update_stock():
    if symbol_listbox.curselection():
        selected_symbol = symbol_listbox.get(symbol_listbox.curselection())
        updated = False

        for stock in stocks_data:
            if stock['symbol'] == selected_symbol:
                stock['range'] = int(range_entry.get()) if range_entry.get() else 0
                stock['takeProfitPercentage'] = int(profit_entry.get()) if profit_entry.get() else 0
                stock['isNeedToCheckTakeProfit'] = check_profit_var.get()
                stock['quantity'] = int(quantity_entry.get()) if quantity_entry.get() else 0
                stock['account'] = account_entry.get()
                updated = True
                break

        if updated:
            save_json_data(stocks_data)
            messagebox.showinfo("Success", "Stock information updated successfully!")
        else:
            messagebox.showerror("Error", "No symbol selected!")
    else:
        messagebox.showerror("Error", "No symbol selected!")


# Add a new symbol to the list and JSON file
def add_symbol():
    new_symbol = symbol_entry.get()
    selected_action = action_combobox.get()

    if not new_symbol:
        messagebox.showerror("Error", "Symbol cannot be empty!")
        return

    # Add new symbol to the stocks_data list
    new_stock = {
        "symbol": new_symbol,
        "action": selected_action,
        "range": 0,
        "takeProfitPercentage": 0,
        "isNeedToCheckTakeProfit": False,
        "quantity": 0,
        "account": ""
    }
    stocks_data.append(new_stock)
    save_json_data(stocks_data)

    # Clear entry and update the listbox
    symbol_entry.delete(0, tk.END)
    populate_symbols(None)
    messagebox.showinfo("Success", "Symbol added successfully!")


# Delete the selected symbol from the list and JSON file
def delete_symbol():
    if symbol_listbox.curselection():
        selected_symbol = symbol_listbox.get(symbol_listbox.curselection())
        stocks_data[:] = [stock for stock in stocks_data if stock['symbol'] != selected_symbol]
        save_json_data(stocks_data)

        populate_symbols(None)
        messagebox.showinfo("Success", "Symbol deleted successfully!")
    else:
        messagebox.showerror("Error", "No symbol selected!")


# GUI setup
root = tk.Tk()
root.geometry("400x700")
root.title("Stock Manager")

# Load stocks data
stocks_data = load_json_data()

# Action combobox (sell, buy, trace)
action_label = tk.Label(root, text="Action:")
action_label.pack(pady=5)

action_combobox = ttk.Combobox(root, values=["sell", "buy", "trace"])
action_combobox.pack(pady=5)
action_combobox.current(0)
action_combobox.bind("<<ComboboxSelected>>", populate_symbols)

# Symbol listbox
symbol_label = tk.Label(root, text="Symbol:")
symbol_label.pack(pady=5)

symbol_frame = tk.Frame(root)
symbol_frame.pack(pady=5, fill=tk.BOTH, expand=True)

symbol_listbox = tk.Listbox(symbol_frame, height=8)
symbol_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar for listbox
scrollbar = tk.Scrollbar(symbol_frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
symbol_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=symbol_listbox.yview)

symbol_listbox.bind("<<ListboxSelect>>", display_stock_details)

# Symbol entry for adding a new symbol
symbol_entry_label = tk.Label(root, text="Add Symbol:")
symbol_entry_label.pack(pady=5)
symbol_entry = tk.Entry(root)
symbol_entry.pack(pady=5)

# Add and Delete buttons
add_button = tk.Button(root, text="Add Symbol", command=add_symbol)
add_button.pack(pady=5)

delete_button = tk.Button(root, text="Delete Selected Symbol", command=delete_symbol)
delete_button.pack(pady=5)

# Range entry
range_label = tk.Label(root, text="Range:")
range_label.pack(pady=5)
range_entry = tk.Entry(root)
range_entry.pack(pady=5)

# Take Profit Percentage entry
profit_label = tk.Label(root, text="Take Profit Percentage:")
profit_label.pack(pady=5)
profit_entry = tk.Entry(root)
profit_entry.pack(pady=5)

# Checkbox for checking take profit
check_profit_var = tk.BooleanVar()
check_profit_checkbutton = tk.Checkbutton(root, text="Check Take Profit", variable=check_profit_var)
check_profit_checkbutton.pack(pady=5)

# Quantity entry
quantity_label = tk.Label(root, text="Quantity:")
quantity_label.pack(pady=5)
quantity_entry = tk.Entry(root)
quantity_entry.pack(pady=5)

# Account entry
account_label = tk.Label(root, text="Account:")
account_label.pack(pady=5)
account_entry = tk.Entry(root)
account_entry.pack(pady=5)

# Update button
update_button = tk.Button(root, text="Update Stock", command=update_stock)
update_button.pack(pady=10)

# Populate initial symbols for the default action (sell)
populate_symbols(None)

root.mainloop()
