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

    def display_price_graph(self, hist_dict: dict) -> None:
        """Display 1-year price history for one or more tickers"""
        plt.figure(figsize=(12, 7))
        for ticker, hist in hist_dict.items():
            plt.plot(hist.index, hist['Close'], linewidth=2, label=ticker)
        plt.title("Price History — 1 Year (Yahoo Finance)")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.legend(loc='best')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def display_volatility_graph(self, ticker: str, period: str, dates, cond_vol, predicted_vol_daily: float) -> None:
        """Display GARCH(1,1) conditional volatility graph"""
        plt.figure(figsize=(12, 5))
        plt.plot(dates, cond_vol, color='steelblue', linewidth=1, label='Conditional volatility (daily %)')
        plt.axhline(predicted_vol_daily, color='red', linestyle='--', linewidth=1.5,
                    label=f'Today forecast: {predicted_vol_daily:.3f}%')
        plt.title(f'GARCH(1,1) Conditional Volatility — {ticker} ({period})')
        plt.xlabel('Date')
        plt.ylabel('Daily Volatility (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def display_simulation_graph(self, years, portfolio_paths, pct_values, total_initial_value: float, n_paths: int, n_years: int) -> None:
        """Display Monte Carlo simulation graph"""
        import numpy as np
        plt.figure(figsize=(14, 7))
        sample_idx = np.random.choice(n_paths, size=200, replace=False)
        for i in sample_idx:
            plt.plot(years, portfolio_paths[i] / 1e3, color='steelblue', alpha=0.03, linewidth=0.5)
        plt.fill_between(years, pct_values[0] / 1e3, pct_values[6] / 1e3, alpha=0.08, color='red', label='1st–99th pct')
        plt.fill_between(years, pct_values[1] / 1e3, pct_values[5] / 1e3, alpha=0.15, color='orange', label='5th–95th pct')
        plt.fill_between(years, pct_values[2] / 1e3, pct_values[4] / 1e3, alpha=0.25, color='orange', label='25th–75th pct')
        plt.plot(years, pct_values[3] / 1e3, color='darkorange', linewidth=2.5, label='Median')
        plt.axhline(y=total_initial_value / 1e3, color='red', linestyle='--', linewidth=1.5, label='Initial Value')
        plt.title(f"Portfolio Monte Carlo Simulation — {n_years} Years, {n_paths:,} Paths", fontsize=14)
        plt.xlabel("Year")
        plt.ylabel("Portfolio Value ($000s)")
        plt.legend(loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, n_years + 1))
        plt.tight_layout()
        plt.show()