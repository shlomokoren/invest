import tkinter as tk
from tkinter import ttk, messagebox
import json


# Populate the listbox based on selected action
def populate_symbols(event):
    selected_action = action_combobox.get()
    symbol_listbox.delete(0, tk.END)

    for stock in stocks_data:
        if stock['action'] == selected_action:
            symbol_listbox.insert(tk.END, stock['symbol'])


def add_symbol_popup():
    pass
def edit_symbol_popup():
    pass
def delete_symbol():
    pass
# Load the JSON data from data_invest.json file
from tkinter.filedialog import askopenfilename

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


# Load stocks data
stocks_data = load_json_data()

# Create the main window
root = tk.Tk()
root.title("Test Tabs")

# Create the notebook (tab container)
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Create the tabs
portfolio_tab = ttk.Frame(notebook)
general_params_tab = ttk.Frame(notebook)

# Add tabs to the notebook
notebook.add(portfolio_tab, text="Portfolio")
notebook.add(general_params_tab, text="General Parameters")

# Configure the root window to expand properly
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)


# Add a label to the portfolio_tab
tk.Label(portfolio_tab, text="Symbol:").grid(row=0, column=0, padx=10, pady=10, sticky="w")

action_combobox = ttk.Combobox(portfolio_tab, values=["sell", "buy", "trace"])
action_combobox.grid(row=0, column=1, padx=10, pady=10)
action_combobox.current(0)

# Symbol listbox
symbol_listbox = tk.Listbox(portfolio_tab, height=15)
symbol_listbox.grid(row=1, column=0, padx=10, pady=10, rowspan=6)

# Right panel to show symbol details
details_frame = tk.Frame(portfolio_tab)
details_frame.grid(row=1, column=1, padx=10, pady=10, sticky="n")

tk.Label(details_frame, text="Symbol:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
symbol_value_var = tk.StringVar()
tk.Label(details_frame, textvariable=symbol_value_var).grid(row=0, column=1, padx=5, pady=5, sticky="w")
symbol_value_var.set("symbol_value_var")
tk.Label(details_frame, text="Action:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
action_value_var = tk.StringVar()
tk.Label(details_frame, textvariable=action_value_var).grid(row=1, column=1, padx=5, pady=5, sticky="w")
action_value_var.set("action")
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
account_value_var.set("momo")

# Buttons for Add, Edit, and Delete
add_button = tk.Button(portfolio_tab, text="Add Symbol", command=add_symbol_popup)
add_button.grid(row=7, column=1, padx=10, pady=10)

edit_button = tk.Button(portfolio_tab, text="Edit Selected Symbol", command=edit_symbol_popup)
edit_button.grid(row=8, column=1, padx=10, pady=10)

delete_button = tk.Button(portfolio_tab, text="Delete Selected Symbol", command=delete_symbol)
delete_button.grid(row=9, column=1, padx=10, pady=10)


# Run the main loop
root.mainloop()
