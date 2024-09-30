# Project Name

  This Python tool tracks the moving average of stocks and provides buy or sell recommendations based on the moving average indicator. 
  Additionally, it can execute direct trades using Interactive Brokers software to automatically buy or sell stocks.
  A detailed explanation of how the moving average indicator works will be provided later in this document.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/shlomokoren/invest.git
    ```

2. Navigate to the project directory:
    ```bash
    cd your-repo-name
    ```

3. (Optional) Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Describe how to use the script. For example:

``` there are 2 python script
1 - software to make recomendations and send notifications/alerts (can log to google sheet , write to local computer logs file, send telegram alerts)
	python invest_moving_average_rule_handle.py 
	you have to configure enviroment variables and files before
2- tool to handle manual portpolio list and general parameters that are in json local files
    python manualHandleStocksListGUI.py
