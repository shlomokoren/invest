# display_file_content.py

import sys

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
    if len(sys.argv) != 2:
        print("Usage: python display_file_content.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    display_file_content(file_path)
