import os

# Get the current script's directory
current_directory =""
current_directory = os.path.dirname(os.path.abspath(__file__))
print(os.name)
# Ensure the path is correct for the OS
current_directory = current_directory.replace("\\", "\\\\")

print(f"The script is running from: {current_directory}")