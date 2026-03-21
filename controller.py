"""Portfolio controller: handles CLI commands and user inputs"""

from model import Portfolio


class PortfolioController:
    """Handles user commands and portfolio operations"""
    
    def __init__(self):
        self.portfolio = Portfolio()
    
    def parse_command(self, user_input: str) -> tuple:
        """
        Splits user input into command and arguments.
        Returns (command, args) where args is a list
        """
        parts = user_input.strip().split() # Split user input into a command and arguments
        
        if not parts:
            return None, None
        
        command = parts[0].lower() # Always use in the command in lowercase
        return command, parts[1:]
    
    def execute_command(self, command: str, args: list) -> str:
        """Execute a command and return status message"""
        
        if command == "add":
            return self._handle_add(args)
        
        elif command == "list":
            return self._handle_list()
        
        elif command == "remove":
            return self._handle_remove(args)
        
        elif command == "value":
            return self._handle_value()
        
        elif command == "help":
            return self._handle_help()
        
        elif command == "quit" or command == "exit":
            return "QUIT"
        
        else:
            return f"Unknown command: {command}. Type 'help' for available commands."
    
    def _handle_add(self, args: list) -> str:
        """Handle 'add TICKER SECTOR ASSET_CLASS QUANTITY PRICE' command"""
        if len(args) < 5:
            return "Usage: add TICKER SECTOR ASSET_CLASS QUANTITY PRICE\nExample: add AAPL tech stock 1 150.50"
        
        ticker = args[0]
        sector = args[1]
        asset_class = args[2]

        try:
            quantity = int(args[3])
            price = float(args[4])
        except ValueError:
            return "Error: QUANTITY must be integer, PRICE must be a number"
        
        if quantity <= 0 or price <= 0:
            return "Error: QUANTITY and PRICE must be positive"
        
        self.portfolio.add_stock(ticker, sector, asset_class, quantity, price)
        total_value = quantity * price
        return f"Added {quantity} shares of {ticker.upper()} ({sector}) ({asset_class}) at ${price} = ${total_value:.2f} total"
    
    def _handle_list(self) -> str:
        """Handle 'list' command, shows all holdings"""
        holdings = self.portfolio.list_holdings()
        
        if not holdings:
            return "Portfolio is empty. Use 'add' to add stocks."
        
        result = "\n--- PORTFOLIO HOLDINGS ---\n"
        for stock in holdings:
            result += f"{stock.ticker:6} | {stock.sector:10} | {stock.asset_class:8} | Qty: {stock.quantity:5} | Price: ${stock.price:8.2f} | Total: ${stock.total_value():10.2f}\n"
        
        return result
    
    def _handle_remove(self, args: list) -> str:
        """Handle 'remove TICKER' command"""
        if len(args) < 1:
            return "Usage: remove TICKER\nExample: remove AAPL"
        
        ticker = args[0]
        if self.portfolio.remove_stock(ticker):
            return f"Removed {ticker.upper()} from portfolio"
        else:
            return f"Error: {ticker.upper()} not found in portfolio"
    
    def _handle_value(self) -> str:
        """Handle 'value' command - show total portfolio value"""
        total = self.portfolio.total_portfolio_value()
        return f"Total Portfolio Value: ${total:.2f}"
    
    def _handle_help(self) -> str:
        """Show available commands"""
        help_text = """
--- PORTFOLIO TRACKER COMMANDS ---
  add TICKER SECTOR ASSET_CLASS QUANTITY PRICE  - Add asset to portfolio
                                                   Example: add AAPL tech stock 1 150.50
  list                                          - Show all holdings
  value                                         - Show total portfolio value
  remove TICKER                                 - Remove asset from portfolio
  help                                          - Show this help message
  quit / exit                                   - Exit the program
"""
        return help_text
