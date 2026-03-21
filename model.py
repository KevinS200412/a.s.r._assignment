"""Portfolio model: data storage and management"""

class Stock:
    """Represents single stock holding"""
    def __init__(self, ticker: str, sector: str, quantity: int, price: float):
        self.ticker = ticker
        self.sector = sector
        self.quantity = quantity
        self.price = price
    
    def total_value(self) -> float:
        """Calculate total value of this holding"""
        return self.quantity * self.price
    
    def __repr__(self) -> str: # Ensures good-looking print of stock info
        return f"Stock({self.ticker}, Sector:{self.sector}, Quantity:{self.quantity}, Price:${self.price})"
