import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import json
import sys


from invest_moving_average_rule_handle import enableLogFile
datainvestjson = ""


def quit_application():
    root.destroy()
    sys.exit()


def load_json_data():
    global datainvestjson

    # Open a file dialog to select a JSON file
    datainvestjson = askopenfilename(
        title="Select a JSON file",
        filetypes=[("JSON files", "*.json")]
    )

    # Check if a file was selected
    if not datainvestjson:
        print("No file selected.")
        return None

    with open(datainvestjson, "r") as f:
        return json.load(f)


# Save the JSON data to data_invest.json file
def save_json_data(data):
    global datainvestjson
    sorted_data = sorted(data, key=lambda x: (x['symbol'], x['action']))
    with open(datainvestjson, "w") as f:
        json.dump(sorted_data, f, indent=4)

# Load the JSON data from data_invest.json file
def load_json_general_parameters():
    with open("general_parameters.json", "r") as f:
        return json.load(f)
# Save the JSON data to data_invest.json file
def save_json_general_parameters(data):
    with open("general_parameters.json", "w") as f:
        json.dump(data, f, indent=4)

# Populate the listbox based on selected action
def populate_symbols(event):
    selected_action = action_combobox.get()
    symbol_listbox.delete(0, tk.END)

    for stock in stocks_data:
        if stock['action'] == selected_action:
            symbol_listbox.insert(tk.END, stock['symbol'])

# Display the details of the selected symbol on the right panel
def display_symbol_details(event):
    # Clear the fields first
    clear_symbol_details()

    if not symbol_listbox.curselection():
        return

    selected_symbol = symbol_listbox.get(symbol_listbox.curselection())
    selected_action = action_combobox.get()

    # Find selected stock data
#    selected_stock = next((stock for stock in stocks_data if stock['symbol'] == selected_symbol), None)
    selected_stock = next ((stock for stock in stocks_data if
                      stock['symbol'] == selected_symbol and stock['action'] == selected_action), None)


    if selected_stock:
        symbol_value_var.set(selected_stock['symbol'])
        action_value_var.set(selected_stock['action'])
        range_value_var.set(selected_stock.get('range', ''))
        take_profit_value_var.set(selected_stock.get('takeProfitPercentage', ''))
        check_profit_value_var.set("Yes" if selected_stock.get('isNeedToCheckTakeProfit', False) else "No")
        quantity_value_var.set(selected_stock.get('quantity', ''))
        account_value_var.set(selected_stock.get('account', ''))

# Clear the symbol details when no selection is made
def clear_symbol_details():
    symbol_value_var.set("")
    action_value_var.set("")
    range_value_var.set("")
    take_profit_value_var.set("")
    check_profit_value_var.set("")
    quantity_value_var.set("")
    account_value_var.set("")

# Add new symbol pop-up window
def add_symbol_popup():
    def save_symbol():
        new_symbol = symbol_entry.get()
        new_action = action_combobox_popup.get()
        new_range = int(range_entry_popup.get()) if range_entry_popup.get() else 0
        new_profit = int(profit_entry_popup.get()) if profit_entry_popup.get() else 0
        new_check_profit = check_profit_var_popup.get()
        new_quantity = int(quantity_entry_popup.get()) if quantity_entry_popup.get() else 0
        new_account = account_entry_popup.get()

        if not new_symbol:
            messagebox.showerror("Error", "Symbol cannot be empty!")
            return

        # Add new symbol to the stocks_data list
        new_stock = {
            "symbol": new_symbol,
            "action": new_action,
            "range": new_range,
            "takeProfitPercentage": new_profit,
            "isNeedToCheckTakeProfit": new_check_profit,
            "quantity": new_quantity,
            "account": new_account
        }
        stocks_data.append(new_stock)
        save_json_data(stocks_data)

        # Update the listbox and close the popup
        populate_symbols(None)
        add_window.destroy()

    # Popup window for adding symbol
    add_window = tk.Toplevel(root)
    add_window.title("Add New Symbol")

    tk.Label(add_window, text="Symbol:").pack(pady=5)
    symbol_entry = tk.Entry(add_window)
    symbol_entry.pack(pady=5)

    tk.Label(add_window, text="Action:").pack(pady=5)
    action_combobox_popup = ttk.Combobox(add_window, values=["sell", "buy", "trace"])
    action_combobox_popup.pack(pady=5)
    action_combobox_popup.current(0)

    tk.Label(add_window, text="Range:").pack(pady=5)
    range_entry_popup = tk.Entry(add_window)
    range_entry_popup.pack(pady=5)

    tk.Label(add_window, text="Take Profit Percentage:").pack(pady=5)
    profit_entry_popup = tk.Entry(add_window)
    profit_entry_popup.pack(pady=5)

    check_profit_var_popup = tk.BooleanVar()
    check_profit_checkbutton_popup = tk.Checkbutton(add_window, text="Check Take Profit", variable=check_profit_var_popup)
    check_profit_checkbutton_popup.pack(pady=5)

    tk.Label(add_window, text="Quantity:").pack(pady=5)
    quantity_entry_popup = tk.Entry(add_window)
    quantity_entry_popup.pack(pady=5)

    tk.Label(add_window, text="Account:").pack(pady=5)
    account_entry_popup = tk.Entry(add_window)
    account_entry_popup.pack(pady=5)

    # Save and Cancel buttons
    save_button = tk.Button(add_window, text="Save", command=save_symbol)
    save_button.pack(side=tk.LEFT, padx=20, pady=10)

    cancel_button = tk.Button(add_window, text="Cancel", command=add_window.destroy)
    cancel_button.pack(side=tk.RIGHT, padx=20, pady=10)

# Edit symbol pop-up window
def edit_symbol_popup():
    selected_symbol = symbol_listbox.get(symbol_listbox.curselection())
    selected_action = action_combobox.get()
    #selected_stock = next((stock for stock in stocks_data if stock['symbol'] == selected_symbol), None)
    selected_stock = next ((stock for stock in stocks_data if
                      stock['symbol'] == selected_symbol and stock['action'] == selected_action), None)

    if selected_stock:
        def save_edited_symbol():
            edited_action = action_combobox_popup.get()
            edited_range = int(range_entry_popup.get()) if range_entry_popup.get() else 0
            edited_profit = int(profit_entry_popup.get()) if profit_entry_popup.get() else 0
            edited_check_profit = check_profit_var_popup.get()
            edited_quantity = int(quantity_entry_popup.get()) if quantity_entry_popup.get() else 0
            edited_account = account_entry_popup.get()

            # Update selected stock with new values
            selected_stock['action'] = edited_action
            selected_stock['range'] = edited_range
            selected_stock['takeProfitPercentage'] = edited_profit
            selected_stock['isNeedToCheckTakeProfit'] = edited_check_profit
            selected_stock['quantity'] = edited_quantity
            selected_stock['account'] = edited_account

            save_json_data(stocks_data)
            populate_symbols(None)
            edit_window.destroy()

        # Popup window for editing symbol
        edit_window = tk.Toplevel(root)
        edit_window.title("Edit Symbol")

        tk.Label(edit_window, text="Symbol (Read-only):").pack(pady=5)
        symbol_entry = tk.Entry(edit_window)
        symbol_entry.insert(0, selected_stock['symbol'])
        symbol_entry.config(state='readonly')
        symbol_entry.pack(pady=5)

        tk.Label(edit_window, text="Action:").pack(pady=5)
        action_combobox_popup = ttk.Combobox(edit_window, values=["sell", "buy", "trace"])
        action_combobox_popup.set(selected_stock['action'])
        action_combobox_popup.pack(pady=5)

        tk.Label(edit_window, text="Range:").pack(pady=5)
        range_entry_popup = tk.Entry(edit_window)
        range_entry_popup.insert(0, selected_stock.get('range', ''))
        range_entry_popup.pack(pady=5)

        tk.Label(edit_window, text="Take Profit Percentage:").pack(pady=5)
        profit_entry_popup = tk.Entry(edit_window)
        profit_entry_popup.insert(0, selected_stock.get('takeProfitPercentage', ''))
        profit_entry_popup.pack(pady=5)

        check_profit_var_popup = tk.BooleanVar(value=selected_stock.get('isNeedToCheckTakeProfit', False))
        check_profit_checkbutton_popup = tk.Checkbutton(edit_window, text="Check Take Profit", variable=check_profit_var_popup)
        check_profit_checkbutton_popup.pack(pady=5)

        tk.Label(edit_window, text="Quantity:").pack(pady=5)
        quantity_entry_popup = tk.Entry(edit_window)
        quantity_entry_popup.insert(0, selected_stock.get('quantity', ''))
        quantity_entry_popup.pack(pady=5)

        tk.Label(edit_window, text="Account:").pack(pady=5)
        account_entry_popup = tk.Entry(edit_window)
        account_entry_popup.insert(0, selected_stock.get('account', ''))
        account_entry_popup.pack(pady=5)

        # Save and Cancel buttons
        save_button = tk.Button(edit_window, text="Save", command=save_edited_symbol)
        save_button.pack(side=tk.LEFT, padx=20, pady=10)

        cancel_button = tk.Button(edit_window, text="Cancel", command=edit_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=20, pady=10)
    else:
        messagebox.showerror("Error", "No symbol selected!")

# Delete the selected symbol from the list and JSON file
def delete_symbol():
    if symbol_listbox.curselection():
        selected_symbol = symbol_listbox.get(symbol_listbox.curselection())
        selected_action = action_combobox.get()
        stocks_data[:] = [stock for stock in stocks_data if
                          not (stock['symbol'] == selected_symbol and stock['action'] == selected_action)]

        save_json_data(stocks_data)

        populate_symbols(None)
        messagebox.showinfo("Success", "Symbol deleted successfully!")
        clear_symbol_details()
    else:
        messagebox.showerror("Error", "No symbol selected!")

# Load stocks data
stocks_data = load_json_data()

# Create the main window
root = tk.Tk()
root.title("Stock Management Tool")

# Bind the close event
root.protocol("WM_DELETE_WINDOW", quit_application)

# Create the notebook (tab container)
notebook = ttk.Notebook(root)

# Create the frames for the two tabs
portfolio_tab = ttk.Frame(notebook)
general_params_tab = ttk.Frame(notebook)

# Add the frames as tabs in the notebook
notebook.add(portfolio_tab, text="Portfolio")
notebook.add(general_params_tab, text="General Parameters")

# Place the notebook using grid
notebook.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Configure the root window to expand properly
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Action combobox (sell, buy, trace)
tk.Label(portfolio_tab, text="Select Action:").grid(row=0, column=0, padx=10, pady=10)
action_combobox = ttk.Combobox(portfolio_tab, values=["sell", "buy", "trace"])
action_combobox.grid(row=0, column=1, padx=10, pady=10)
action_combobox.current(0)
action_combobox.bind("<<ComboboxSelected>>", populate_symbols)

# Symbol listbox
symbol_listbox = tk.Listbox(portfolio_tab, height=15)
symbol_listbox.grid(row=1, column=0, padx=10, pady=10, rowspan=6)
symbol_listbox.bind("<<ListboxSelect>>", display_symbol_details)

# Right panel to show symbol details
details_frame = tk.Frame(portfolio_tab)
details_frame.grid(row=1, column=1, padx=10, pady=10, sticky="n")

tk.Label(details_frame, text="Symbol:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
symbol_value_var = tk.StringVar()
tk.Label(details_frame, textvariable=symbol_value_var).grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(details_frame, text="Action:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
action_value_var = tk.StringVar()
tk.Label(details_frame, textvariable=action_value_var).grid(row=1, column=1, padx=5, pady=5, sticky="w")

tk.Label(details_frame, text="Range:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
range_value_var = tk.StringVar()
tk.Label(details_frame, textvariable=range_value_var).grid(row=2, column=1, padx=5, pady=5, sticky="w")

tk.Label(details_frame, text="Take Profit Percentage:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
take_profit_value_var = tk.StringVar()
tk.Label(details_frame, textvariable=take_profit_value_var).grid(row=3, column=1, padx=5, pady=5, sticky="w")

tk.Label(details_frame, text="Check Take Profit:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
check_profit_value_var = tk.StringVar()
tk.Label(details_frame, textvariable=check_profit_value_var).grid(row=4, column=1, padx=5, pady=5, sticky="w")

tk.Label(details_frame, text="Quantity:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
quantity_value_var = tk.StringVar()
tk.Label(details_frame, textvariable=quantity_value_var).grid(row=5, column=1, padx=5, pady=5, sticky="w")

tk.Label(details_frame, text="Account:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
account_value_var = tk.StringVar()
tk.Label(details_frame, textvariable=account_value_var).grid(row=6, column=1, padx=5, pady=5, sticky="w")


# Buttons for Add, Edit, and Delete
add_button = tk.Button(portfolio_tab, text="Add Symbol", command=add_symbol_popup)
add_button.grid(row=7, column=1, padx=10, pady=10)

edit_button = tk.Button(portfolio_tab, text="Edit Selected Symbol", command=edit_symbol_popup)
edit_button.grid(row=8, column=1, padx=10, pady=10)

delete_button = tk.Button(portfolio_tab, text="Delete Selected Symbol", command=delete_symbol)
delete_button.grid(row=9, column=1, padx=10, pady=10)

# Populate symbols for the initial action
populate_symbols(None)

##----
# Load general parameters data
data = load_json_general_parameters()

# Create a dictionary to store the widget references for updating values
widget_references = {}

# Function to create widgets for general parameters
def create_widgets_for_general_parameters(data):
    for row, param in enumerate(data):
        key, value = list(param.items())[0]  # Get the key-value pair from the dictionary

        # For boolean values, create a checkbox
        if isinstance(value, bool):
            var = tk.BooleanVar(value=value)
            checkbox = tk.Checkbutton(general_params_tab, text=key, variable=var)
            checkbox.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            widget_references[key] = var

        # For string values, create a text entry field
        elif isinstance(value, str):
            label = tk.Label(general_params_tab, text=f"{key}:")
            label.grid(row=row, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(general_params_tab)
            entry.insert(0, value)
            entry.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            widget_references[key] = entry

        # For integer values, create a text entry field that only allows integer input
        elif isinstance(value, int):
            label = tk.Label(general_params_tab, text=f"{key}:")
            label.grid(row=row, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(general_params_tab)
            entry.insert(0, value)
            entry.grid(row=row, column=1, padx=10, pady=5, sticky="w")
            # Make sure only integer input is allowed
            entry.config(validate="key",
                         validatecommand=(root.register(lambda char: char.isdigit() or char == ""), "%S"))
            widget_references[key] = entry


# Function to save the current state of the general parameters
def save_general_parameters():
    updated_data = []
    for param in data:
        key = list(param.keys())[0]
        widget = widget_references[key]

        # Update based on the widget type
        if isinstance(param[key], bool):
            updated_data.append({key: widget.get()})
        elif isinstance(param[key], str):
            updated_data.append({key: widget.get()})
        elif isinstance(param[key], int):
            updated_data.append({key: int(widget.get())})

    # Save to the JSON file
    save_json_general_parameters(updated_data)


# Call the function to create the widgets
create_widgets_for_general_parameters(data)

# Add a Save button at the bottom of the general_params_tab
save_button = tk.Button(general_params_tab, text="Save", command=save_general_parameters)
save_button.grid(row=len(data), column=0, columnspan=2, padx=10, pady=10)

# Start the main loop
root.mainloop()
