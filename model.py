"""Portfolio model: data storage and management"""

class Stock:
    """Represents single stock holding"""
    def __init__(self, ticker: str, sector: str, asset_class: str, quantity: int, price: float):
        self.ticker = ticker
        self.sector = sector
        self.asset_class = asset_class
        self.quantity = quantity
        self.price = price
        self.total_cost_invested = quantity * price  # Track total cost of all purchases
        self.price_history = [price]

    def add_price(self, new_price: float, additional_quantity: int = 0) -> None:
        """Add a new price to the history and update current price. Used when quantity changes."""
        self.price_history.append(new_price)
        self.price = new_price
        # If additional quantity was purchased, add to total cost
        if additional_quantity > 0:
            self.total_cost_invested += additional_quantity * new_price
    
    def get_average_purchase_price(self) -> float:
        """Calculate weighted average purchase price across all purchases"""
        return self.total_cost_invested / self.quantity if self.quantity > 0 else 0
    
    def total_value(self) -> float:
        """Calculate total current value of this holding (based on current price)"""
        return self.quantity * self.price
    
    def transaction_value(self) -> float:
        """Calculate transaction value (total amount invested at purchase prices)"""
        return self.total_cost_invested
    
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
            # Update existing holding: add quantity and update price history with new purchase
            self.holdings[ticker].quantity += quantity
            self.holdings[ticker].add_price(price, additional_quantity=quantity)  # Add new price and quantity to cost basis
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

