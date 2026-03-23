# Project: CLI portfolio tracker

# This project is a Command Line Interface (CLI) application that allows users to manage and analyze a financial portfolio. Users can add assets, track their value using live market data, and perform various analyses such as portfolio weights, historical prices, volatility forecasting, and Monte Carlo simulation.

# The application is structured using the MVC (Model-View-Controller) design pattern to ensure clear separation of concerns. The controller handles CLI input and commands, the model manages portfolio data, calculations, and market analytics, and the view displays results, tables, and graphs to the user.

# Features:
- Add and remove assets (stocks, ETFs, etc.) to portfolio
- Fetch live prices from Yahoo Finance
- View portfolio holdings, total value, and return
- Analyze portfolio weights (by asset, sector, class)
- View historical price data and trading volume
- Predict volatility using GARCH(1,1)
- Detect market regimes using Hidden Markov Models (machine learning)
- Run Monte Carlo simulations for future portfolio value
- Display graphs for price history, volatility, and simulations


# Running the Application (Windows):

# 0. Make sure Python (version 3.9 or higher) is installed

# 1. Download the ZIP file from the GitHub repository (link provided in email) and extract it

# 2. Open Command Prompt (CMD)

# 3. Navigate to the project folder
cd C:\path\to\your\folder\a.s.r._assignment

# 4. Create a virtual environment
python -m venv venv

# 5. Activate the virtual environment
venv\Scripts\activate

# 6. Install dependencies
pip install -r requirements.txt

# 7. Run the application
python main.py

# 8. You should now see:
# portfolio>


# How to work with the project:

1. When 'portfolio>' is displayed, you can enter commands in the terminal
2. Type 'help' to see all available commands
3. The application will display all commands together with a description of each command

Examples of commands:

Example: list
         -> displays all current holdings in the portfolio

Example: value
         -> shows the total value of the portfolio

Example: add AAPL tech stock 2 200
         -> adds 2 shares of AAPL at $200 per share (total cost: $400)

Example: history AAPL 6mo
         -> displays AAPL price history over the last 6 months

Example: weights sector tech
         -> shows the distribution of stocks within the tech sector


Remarks:

- If you add an asset at a specific price, this is used as the purchase price, while the current value is always based on live market data.

- The application uses live data from Yahoo Finance, so an internet connection is required for most features.

- The Monte Carlo simulation is based on assumed return and volatility parameters and does not guarantee future performance.

