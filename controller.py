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
        
        elif command == "history":
            return self._handle_history(args)
        
        elif command == "graph":
            return self._handle_graph(args)
        
        elif command == "remove":
            return self._handle_remove(args)
        
        elif command == "value":
            return self._handle_value()
        
        elif command == "weights":
            return self._handle_weights(args)
        
        elif command == "help":
            return self._handle_help()
        
        elif command == "quit" or command == "exit":
            return "- QUIT"
        
        else:
            return f"- Unknown command: {command}. Type 'help' for available commands."
    
    def _handle_add(self, args: list) -> str:
        """Handle 'add TICKER SECTOR ASSET_CLASS QUANTITY PRICE' command"""
        if len(args) < 5:
            return "- Usage: add TICKER SECTOR ASSET_CLASS QUANTITY PRICE\nExample: add AAPL tech stock 1 150.50"
        
        ticker = args[0]
        sector = args[1]
        asset_class = args[2]

        try:
            quantity = int(args[3])
            price = float(args[4])
        except ValueError:
            return "- Error: QUANTITY must be integer, PRICE must be a number"
        
        if quantity <= 0 or price <= 0:
            return "- Error: QUANTITY and PRICE must be positive"
        
        self.portfolio.add_stock(ticker, sector, asset_class, quantity, price)
        total_value = quantity * price
        return f"- Added {quantity} shares of {ticker.upper()} ({sector}) ({asset_class}) at ${price} = ${total_value:.2f} total"
    
    def _handle_list(self) -> str:
        """Handle 'list' command, shows all holdings"""
        holdings = self.portfolio.list_holdings()
        
        if not holdings:
            return "- Portfolio is empty. Use 'add' to add stocks."
        
        result = "\n--- PORTFOLIO HOLDINGS ---\n"
        result += f"{'Ticker':6} | {'Sector':10} | {'Asset Class':12} | {'Qty':5} | {'Avg Price':11} | {'Transaction Value':17} | {'Current Value':14}\n"
        result += "-" * 110 + "\n"
        for stock in holdings:
            result += f"{stock.ticker:6} | {stock.sector:10} | {stock.asset_class:12} | {stock.quantity:5} | ${stock.get_average_purchase_price():10.2f} | ${stock.transaction_value():16.2f} | ${stock.total_value():13.2f}\n"
        
        return result
    
    def _handle_remove(self, args: list) -> str:
        """Handle 'remove TICKER' command"""
        if len(args) < 1:
            return "- Usage: remove TICKER\nExample: remove AAPL"
        
        ticker = args[0]
        if self.portfolio.remove_stock(ticker):
            return f"- Removed {ticker.upper()} from portfolio"
        else:
            return f"- Error: {ticker.upper()} not found in portfolio"
    
    def _handle_value(self) -> str:
        """Handle 'value' command - show total portfolio value"""
        total = self.portfolio.total_portfolio_value()
        return f"- Total Portfolio Value: ${total:.2f}"
    
    def _handle_weights(self, args: list) -> str:
        """Handle 'weights' command - show portfolio weights and breakdowns"""
        holdings = self.portfolio.list_holdings()
        
        if not holdings:
            return "- Portfolio is empty. Use 'add' to add stocks."
        
        total_value = self.portfolio.total_portfolio_value()
        
        # No arguments: show total portfolio weights
        if len(args) == 0:
            result = "\n--- PORTFOLIO WEIGHTS ---\n"
            result += f"Total Portfolio Value: ${total_value:.2f}\n"
            result += f"Total Transaction Value: ${self.portfolio.total_transaction_value():.2f}\n\n"
            result += f"{'Ticker':8} | {'Value':12} | {'Weight':10}\n"
            result += "-" * 35 + "\n"
            for stock in holdings:
                value = stock.total_value()
                weight = (value / total_value * 100) if total_value > 0 else 0
                result += f"{stock.ticker:8} | ${value:11.2f} | {weight:8.2f}%\n"
            return result
        
        # weights sectors - show weights of each sector
        elif args[0].lower() == "sectors":
            by_sector = self.portfolio.get_holdings_by_sector()
            result = "\n--- SECTOR WEIGHTS ---\n"
            result += f"Total Portfolio Value: ${total_value:.2f}\n\n"
            result += f"{'Sector':15} | {'Value':12} | {'Weight':10}\n"
            result += "-" * 42 + "\n"
            for sector in sorted(by_sector.keys()):
                sector_value = sum(stock.total_value() for stock in by_sector[sector])
                weight = (sector_value / total_value * 100) if total_value > 0 else 0
                result += f"{sector:15} | ${sector_value:11.2f} | {weight:8.2f}%\n"
            return result
        
        # weights classes - show weights of each asset class
        elif args[0].lower() == "classes":
            by_class = self.portfolio.get_holdings_by_asset_class()
            result = "\n--- ASSET CLASS WEIGHTS ---\n"
            result += f"Total Portfolio Value: ${total_value:.2f}\n\n"
            result += f"{'Asset Class':15} | {'Value':12} | {'Weight':10}\n"
            result += "-" * 42 + "\n"
            for asset_class in sorted(by_class.keys()):
                class_value = sum(stock.total_value() for stock in by_class[asset_class])
                weight = (class_value / total_value * 100) if total_value > 0 else 0
                result += f"{asset_class:15} | ${class_value:11.2f} | {weight:8.2f}%\n"
            return result
        
        # weights sector SECTOR_NAME - show weights within specific sector
        elif args[0].lower() == "sector" and len(args) > 1:
            sector_name = args[1].lower()
            by_sector = self.portfolio.get_holdings_by_sector()
            
            # Find matching sector (case-insensitive)
            matching_sector = None
            for sector in by_sector.keys():
                if sector.lower() == sector_name:
                    matching_sector = sector
                    break
            
            if not matching_sector:
                return f"- Sector '{args[1]}' not found in portfolio."
            
            sector_stocks = by_sector[matching_sector]
            sector_value = sum(stock.total_value() for stock in sector_stocks)
            
            result = f"\n--- WEIGHTS IN SECTOR: {matching_sector.upper()} ---\n"
            result += f"Sector Value: ${sector_value:.2f}\n\n"
            result += f"{'Ticker':8} | {'Value':12} | {'Weight in Sector':18}\n"
            result += "-" * 48 + "\n"
            for stock in sorted(sector_stocks, key=lambda x: x.total_value(), reverse=True):
                value = stock.total_value()
                weight = (value / sector_value * 100) if sector_value > 0 else 0
                result += f"{stock.ticker:8} | ${value:11.2f} | {weight:16.2f}%\n"
            return result
        
        # weights class CLASS_NAME - show weights within specific asset class
        elif args[0].lower() == "class" and len(args) > 1:
            class_name = args[1].lower()
            by_class = self.portfolio.get_holdings_by_asset_class()
            
            # Find matching class (case-insensitive)
            matching_class = None
            for asset_class in by_class.keys():
                if asset_class.lower() == class_name:
                    matching_class = asset_class
                    break
            
            if not matching_class:
                return f"- Asset class '{args[1]}' not found in portfolio."
            
            class_stocks = by_class[matching_class]
            class_value = sum(stock.total_value() for stock in class_stocks)
            
            result = f"\n--- WEIGHTS IN CLASS: {matching_class.upper()} ---\n"
            result += f"Class Value: ${class_value:.2f}\n\n"
            result += f"{'Ticker':8} | {'Value':12} | {'Weight in Class':18}\n"
            result += "-" * 48 + "\n"
            for stock in sorted(class_stocks, key=lambda x: x.total_value(), reverse=True):
                value = stock.total_value()
                weight = (value / class_value * 100) if class_value > 0 else 0
                result += f"{stock.ticker:8} | ${value:11.2f} | {weight:16.2f}%\n"
            return result
        
        else:
            return """- Usage: weights [option]
  weights                    - Show portfolio weights
  weights sectors            - Show weights of each sector
  weights classes            - Show weights of each asset class
  weights sector SECTOR_NAME - Show weights within a sector
  weights class CLASS_NAME   - Show weights within an asset class
Example: weights sector tech
Example: weights class stock"""
    
    def _handle_history(self, args: list) -> str:
        """Handle 'history TICKER' command - show price history"""
        if len(args) < 1:
            return "- Usage: history TICKER\nExample: history AAPL"
        
        ticker = args[0].upper()
        stock = self.portfolio.get_stock(ticker)
        
        if not stock:
            return f"- Error: {ticker} not found in portfolio"
        
        # Format the history as a list
        history_text = f"\n--- PRICE HISTORY FOR {ticker} ---\n"
        for idx, price in enumerate(stock.price_history, 1):
            history_text += f"Entry {idx}: ${price:.2f}\n"
        
        history_text += f"\nCurrent Price: ${stock.price:.2f}\n"
        return history_text
    
    def _handle_help(self) -> str:
        """Show available commands"""
        help_text = """
--- PORTFOLIO TRACKER COMMANDS ---
  add TICKER SECTOR ASSET_CLASS QUANTITY PRICE  - Add asset to portfolio
                                                   Example: add AAPL tech stock 1 150.50
  list                                          - Show all holdings
  history TICKER                                - Show price history for a ticker
                                                   Example: history AAPL
  graph TICKER [TICKER2 TICKER3 ...]           - Display price graph for one or more tickers
                                                   Example: graph AAPL
                                                   Example: graph AAPL MSFT GOOGL
  value                                         - Show total portfolio value
  weights                                       - Show portfolio weights (all assets)
  weights sectors                               - Show weights of each sector
  weights classes                               - Show weights of each asset class
  weights sector SECTOR_NAME                    - Show weights within specific sector
  weights class CLASS_NAME                      - Show weights within specific asset class
  remove TICKER                                 - Remove asset from portfolio
  help                                          - Show this help message
  quit / exit                                   - Exit the program
"""
        return help_text

    def _handle_graph(self, args: list) -> str:
        """Handle 'graph TICKER1 TICKER2 ...' command - display price charts for multiple tickers"""
        if len(args) < 1:
            return "- Usage: graph TICKER [TICKER2 TICKER3 ...]\nExample: graph AAPL\nExample: graph AAPL MSFT GOOGL"
        
        try:
            import matplotlib.pyplot as plt
            
            # Collect all valid stocks
            stocks_to_plot = []
            for ticker_arg in args:
                ticker = ticker_arg.upper()
                stock = self.portfolio.get_stock(ticker)
                
                if not stock:
                    return f"- Error: {ticker} not found in portfolio"
                
                if len(stock.price_history) < 2:
                    return f"- Error: Not enough price history for {ticker} (need at least 2 entries)"
                
                stocks_to_plot.append(stock)
            
            # Create figure with all stocks
            plt.figure(figsize=(12, 7))
            
            for stock in stocks_to_plot:
                plt.plot(range(1, len(stock.price_history) + 1), 
                        stock.price_history, 
                        marker='o', 
                        linestyle='-', 
                        linewidth=2,
                        label=stock.ticker)  # Add label for legend
            
            plt.title("Price History Comparison")
            plt.xlabel("Entry #")
            plt.ylabel("Price ($)")
            plt.legend(loc='best')  # Show legend with ticker names
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            
            ticker_list = ", ".join([s.ticker for s in stocks_to_plot])
            return f"- Graph displayed for: {ticker_list}"
        
        except ImportError:
            return "- Error: matplotlib not installed. Run: pip install -r requirements.txt"
