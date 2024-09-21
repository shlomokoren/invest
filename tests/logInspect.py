import logging
import inspect

# Configure logging to output to console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def log_function_name():
    """Log the name of the currently running function."""
    current_function = inspect.currentframe().f_back.f_code.co_name
    logging.debug(f"Running function: {current_function}")

def function_a():
    log_function_name()
    # Some function logic
    print("Executing function A")

def function_b():
    log_function_name()
    # Some function logic
    print("Executing function B")

# def main():
#     log_function_name()
#     function_a()
#     function_b()
#
# if __name__ == "__main__":
#     main()
function_a()