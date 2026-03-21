"""Portfolio model: data storage and management"""

class Stock:
    """Represents single stock holding"""
    def __init__(self, ticker: str, sector: str, asset_class: str, quantity: int, price: float):
        self.ticker = ticker
        self.sector = sector
        self.asset_class = asset_class
        self.quantity = quantity
        self.price = price
    
    def total_value(self) -> float:
        """Calculate total value of this holding"""
        return self.quantity * self.price
    
    def __repr__(self) -> str: # Ensures good-looking print of stock info
        return f"Stock({self.ticker}, {self.sector}, {self.asset_class}, Qty:{self.quantity}, Price:${self.price})"

class Portfolio:
    """Manages the user's stock portfolio"""
    def __init__(self):
        self.holdings = {}  # Dict with the ticker as key, Stock as value
    
    def add_stock(self, ticker: str, sector: str, asset_class: str, quantity: int, price: float) -> None:
        """Add a stock to portfolio or update if exists"""
        ticker = ticker.upper() # Normalize ticker input to uppercase
        if ticker in self.holdings:
            # Update existing holding
            self.holdings[ticker].quantity += quantity
        else:
            # Add new holding
            self.holdings[ticker] = Stock(ticker, sector, asset_class, quantity, price)
    
    def remove_stock(self, ticker: str) -> bool:
        """Remove a stock from portfolio. Returns True if successful"""
        ticker = ticker.upper()
        if ticker in self.holdings:
            del self.holdings[ticker]
            return True
        return False
    
    def get_stock(self, ticker: str) -> Stock:
        """Get a stock by ticker"""
        return self.holdings.get(ticker.upper())
    
    def list_holdings(self) -> list:
        """Get list of all holdings"""
        return list(self.holdings.values())
    
    def total_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        return sum(stock.total_value() for stock in self.holdings.values())

