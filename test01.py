# display_file_content.py

def display_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            print("File Content:\n")
            print(content)
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    file_path = input("data_invest.json")
    display_file_content(file_path)