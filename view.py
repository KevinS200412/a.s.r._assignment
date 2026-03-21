"""Portfolio view: handles user interface and output"""

import matplotlib.pyplot as plt

class PortfolioView:
    """Handles all user-facing output and prompts"""
    
    def __init__(self):
        self.prompt = "portfolio> "
    
    def show_welcome(self) -> None:
        """Display the starting message of the portfolio CLI application"""
        welcome = """
-----------------------------------------------------------
                PORTFOLIO TRACKER CLI                            
        Type 'help' for available commands                       
-----------------------------------------------------------
"""
        print(welcome)
    
    def get_user_input(self) -> str:
        """Get input from user"""
        return input(self.prompt) # Display prompt and wait for user input
    
    def display_message(self, message: str) -> None:
        """Display a message to the user"""
        print(message)
    
    def display_error(self, error: str) -> None:
        """Display an error message"""
        print(f"❌ {error}")
    
    def display_success(self, message: str) -> None:
        """Display a success message"""
        print(f"✓ {message}")
    
    def show_goodbye(self) -> None:
        """Display goodbye message"""
        print("\nGoodbye!\n")

    def display_graph(self, ticker: str, price_data: list) -> None:
        """Display a line graph of stock price history"""
        plt.figure(figsize=(10, 5))
        plt.plot(price_data, marker='o')
        plt.title(f"Price History for {ticker}")
        plt.xlabel("Time")
        plt.ylabel("Price ($)")
        plt.grid()
        plt.show()