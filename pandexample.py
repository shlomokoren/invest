import tkinter as tk
import json


# Load JSON data from a file
def load_json_data(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)


# Save the modified data back to the JSON file
def save_json_data(data, json_file):
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)


# Update the form fields with data from the current record
def update_form():
    symbol_entry.delete(0, tk.END)
    symbol_entry.insert(0, data[current_index]['symbol'])

    range_entry.delete(0, tk.END)
    range_entry.insert(0, data[current_index]['range'])

    action_entry.delete(0, tk.END)
    action_entry.insert(0, data[current_index]['action'])

    take_profit_entry.delete(0, tk.END)
    take_profit_entry.insert(0, data[current_index].get('takeProfitPercentage', ''))

    is_need_check_entry.set(data[current_index].get('isNeedToCheckTakeProfit', False))

    quantity_entry.delete(0, tk.END)
    quantity_entry.insert(0, data[current_index].get('quantity', ''))

    account_entry.delete(0, tk.END)
    account_entry.insert(0, data[current_index]['account'])


# Save current form data into the JSON object
def save_record():
    data[current_index]['symbol'] = symbol_entry.get()
    data[current_index]['range'] = range_entry.get()
    data[current_index]['action'] = action_entry.get()
    data[current_index]['takeProfitPercentage'] = take_profit_entry.get()
    data[current_index]['isNeedToCheckTakeProfit'] = is_need_check_entry.get()
    data[current_index]['quantity'] = quantity_entry.get()
    data[current_index]['account'] = account_entry.get()
    save_json_data(data, json_file)


# Move to the next record
def next_record():
    global current_index
    save_record()  # Save changes to the current record
    if current_index < len(data) - 1:
        current_index += 1
    update_form()


# Move to the previous record
def previous_record():
    global current_index
    save_record()  # Save changes to the current record
    if current_index > 0:
        current_index -= 1
    update_form()


# Initialize the Tkinter form
def create_form():
    global symbol_entry, range_entry, action_entry, take_profit_entry, is_need_check_entry, quantity_entry, account_entry

    tk.Label(root, text="Symbol:").grid(row=0, column=0)
    symbol_entry = tk.Entry(root)
    symbol_entry.grid(row=0, column=1)

    tk.Label(root, text="Range:").grid(row=1, column=0)
    range_entry = tk.Entry(root)
    range_entry.grid(row=1, column=1)

    tk.Label(root, text="Action:").grid(row=2, column=0)
    action_entry = tk.Entry(root)
    action_entry.grid(row=2, column=1)

    tk.Label(root, text="Take Profit Percentage:").grid(row=3, column=0)
    take_profit_entry = tk.Entry(root)
    take_profit_entry.grid(row=3, column=1)

    tk.Label(root, text="Is Need To Check Take Profit:").grid(row=4, column=0)
    is_need_check_entry = tk.BooleanVar()
    tk.Checkbutton(root, variable=is_need_check_entry).grid(row=4, column=1)

    tk.Label(root, text="Quantity:").grid(row=5, column=0)
    quantity_entry = tk.Entry(root)
    quantity_entry.grid(row=5, column=1)

    tk.Label(root, text="Account:").grid(row=6, column=0)
    account_entry = tk.Entry(root)
    account_entry.grid(row=6, column=1)

    # Navigation buttons
    prev_button = tk.Button(root, text="Back", command=previous_record)
    prev_button.grid(row=7, column=0)

    next_button = tk.Button(root, text="Next", command=next_record)
    next_button.grid(row=7, column=2)

    # Save button
    save_button = tk.Button(root, text="Save", command=save_record)
    save_button.grid(row=7, column=1)


# Main program
json_file = 'data_invest_pndatest.json'
data = load_json_data(json_file)
current_index = 0

# Create the Tkinter window
root = tk.Tk()
root.title("JSON Editor")

# Create the form
create_form()

# Load the first record into the form
update_form()

# Start the Tkinter event loop
root.mainloop()
