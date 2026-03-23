"""Portfolio view: handles user interface and output"""

import matplotlib.pyplot as plt
import numpy as np

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

    def show_help(self) -> None:
        """Display available commands"""
        print("""
--- PORTFOLIO TRACKER COMMANDS ---
  add TICKER SECTOR ASSET_CLASS QUANTITY [PURCHASE_PRICE]  - Add asset to portfolio
                                                              PURCHASE_PRICE is optional; if omitted, 
                                                                the live price is used as purchase price
                                                              Current value reflects the live price from Yahoo Finance
                                                              Example: add AAPL tech stock 10
                                                              Example: add AAPL tech stock 10 154.00
  list                                         - Show all holdings (prices refreshed from Yahoo Finance)
  history TICKER [PERIOD]                      - Show historical close prices from Yahoo Finance
                                                  PERIOD: 1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max (default: 1mo)
  volume TICKER [PERIOD]                       - Show avg and last trading volume from Yahoo Finance
  graph TICKER [TICKER2 TICKER3 ...]           - Display 1-year price chart from Yahoo Finance
                                                  Example: graph AAPL
                                                  Example: graph AAPL MSFT GOOGL
  value                                        - Show total portfolio value (live prices)
  weights                                      - Show portfolio weights (all assets, live prices)
  weights sectors                              - Show weights of each sector
  weights classes                              - Show weights of each asset class
  weights sector SECTOR_NAME                   - Show weights within specific sector
  weights class CLASS_NAME                     - Show weights within specific asset class
  predict volatility TICKER                    - GARCH(1,1) forecast of today's volatility (terminal output)
  historical volatility TICKER [PERIOD]        - GARCH(1,1) conditional volatility graph over time
                                                  PERIOD: 1mo 3mo 6mo 1y 2y 5y 10y ytd max (default: 2y)
                                                  Example: historical volatility AAPL
  regime TICKER [PERIOD] [--states N]          - HMM regime detection (low/medium/high vol states)
                                                  PERIOD default: 2y | --states default: 3 (2-6)
                                                  Example: regime AAPL
                                                  Example: regime AAPL 5y --states 4
  return                                       - Show total portfolio return (cost basis vs live value)
  simulate                                     - Run Monte Carlo simulation (15yr, 100k paths)
  remove TICKER                                - Remove asset from portfolio
  help                                         - Show this help message
  quit / exit                                  - Exit the program
""")

    def display_holdings(self, holdings: list) -> None:
        """Display portfolio holdings table"""
        result = "\n--- PORTFOLIO HOLDINGS (live prices from Yahoo Finance) ---\n"
        result += f"{'Ticker':6} | {'Sector':10} | {'Asset Class':12} | {'Qty':5} | {'Avg Price':11} | {'Transaction Value':17} | {'Current Value':14}\n"
        result += "-" * 110 + "\n"
        for stock in holdings:
            # 6, 8, 12 etc. indicate column widths for consistent alignment
            result += f"{stock.ticker:6} | {stock.sector:10} | {stock.asset_class:12} | {stock.quantity:5} | ${stock.get_average_purchase_price():10.2f} | ${stock.transaction_value():16.2f} | ${stock.total_value():13.2f}\n"
        print(result)

    def display_weights(self, holdings: list, total_value: float, transaction_value: float) -> None:
        """Display portfolio weights table"""
        result = "\n--- PORTFOLIO WEIGHTS ---\n"
        result += f"Total Portfolio Value: ${total_value:.2f}\n"
        result += f"Total Transaction Value: ${transaction_value:.2f}\n\n"
        result += f"{'Ticker':8} | {'Value':12} | {'Weight':10}\n"
        result += "-" * 35 + "\n"
        for stock in holdings:
            value = stock.total_value()
            weight = (value / total_value * 100) if total_value > 0 else 0
            result += f"{stock.ticker:8} | ${value:11.2f} | {weight:8.2f}%\n"
        print(result)

    def display_sector_weights(self, by_sector: dict, total_value: float) -> None:
        """Display sector weights table"""
        result = "\n--- SECTOR WEIGHTS ---\n"
        result += f"Total Portfolio Value: ${total_value:.2f}\n\n"
        result += f"{'Sector':15} | {'Value':12} | {'Weight':10}\n"
        result += "-" * 42 + "\n"
        for sector in sorted(by_sector.keys()):
            sector_value = sum(stock.total_value() for stock in by_sector[sector])
            weight = (sector_value / total_value * 100) if total_value > 0 else 0
            result += f"{sector:15} | ${sector_value:11.2f} | {weight:8.2f}%\n"
        print(result)

    def display_class_weights(self, by_class: dict, total_value: float) -> None:
        """Display asset class weights table"""
        result = "\n--- ASSET CLASS WEIGHTS ---\n"
        result += f"Total Portfolio Value: ${total_value:.2f}\n\n"
        result += f"{'Asset Class':15} | {'Value':12} | {'Weight':10}\n"
        result += "-" * 42 + "\n"
        for asset_class in sorted(by_class.keys()):
            class_value = sum(stock.total_value() for stock in by_class[asset_class])
            weight = (class_value / total_value * 100) if total_value > 0 else 0
            result += f"{asset_class:15} | ${class_value:11.2f} | {weight:8.2f}%\n"
        print(result)

    def display_sector_detail(self, sector_name: str, sector_stocks: list, sector_value: float) -> None:
        """Display weights within a specific sector"""
        result = f"\n--- WEIGHTS IN SECTOR: {sector_name.upper()} ---\n"
        result += f"Sector Value: ${sector_value:.2f}\n\n"
        result += f"{'Ticker':8} | {'Value':12} | {'Weight in Sector':18}\n"
        result += "-" * 48 + "\n"
        for stock in sorted(sector_stocks, key=lambda x: x.total_value(), reverse=True):
            value = stock.total_value()
            weight = (value / sector_value * 100) if sector_value > 0 else 0
            result += f"{stock.ticker:8} | ${value:11.2f} | {weight:16.2f}%\n"
        print(result)

    def display_class_detail(self, class_name: str, class_stocks: list, class_value: float) -> None:
        """Display weights within a specific asset class"""
        result = f"\n--- WEIGHTS IN CLASS: {class_name.upper()} ---\n"
        result += f"Class Value: ${class_value:.2f}\n\n"
        result += f"{'Ticker':8} | {'Value':12} | {'Weight in Class':18}\n"
        result += "-" * 48 + "\n"
        for stock in sorted(class_stocks, key=lambda x: x.total_value(), reverse=True):
            value = stock.total_value()
            weight = (value / class_value * 100) if class_value > 0 else 0
            result += f"{stock.ticker:8} | ${value:11.2f} | {weight:16.2f}%\n"
        print(result)

    def display_price_history(self, ticker: str, period: str, hist, stock=None) -> None:
        """Display historical close price table"""
        result = f"\n--- PRICE HISTORY FOR {ticker} (Period: {period}, source: Yahoo Finance) ---\n"
        result += f"{'Date':12} | {'Close':10}\n"
        result += "-" * 26 + "\n"
        for date, row in hist.iterrows():
            date_str = date.strftime('%Y-%m-%d')
            result += f"{date_str:12} | ${row['Close']:9.2f}\n"
        if stock:
            result += f"\nCurrent Price: ${stock.price:.2f} | Avg Purchase Price: ${stock.get_average_purchase_price():.2f}\n"
        print(result)

    def display_volume(self, ticker: str, period: str, data: dict) -> None:
        """Display volume statistics"""
        result = f"\n--- VOLUME INFO FOR {ticker} (Period: {period}, source: Yahoo Finance) ---\n"
        result += f"Avg Volume (Period: {period}): {data['avg_vol']:,}\n"
        result += f"Last Volume ({data['last_date']}): {data['last_vol']:,}\n"
        print(result)

    def display_volatility_forecast(self, ticker: str, period: str, data: dict) -> None:
        """Display GARCH(1,1) volatility forecast"""
        out  = f"\n--- GARCH(1,1) VOLATILITY FORECAST FOR {ticker} ---\n"
        out += f"Fitted on {period} of data ({len(data['returns'])} obs, up to {data['last_date']})\n"
        out += f"Predicted daily vol (today): {data['predicted_vol_daily']:.4f}%\n"
        print(out)

    def display_regime(self, ticker: str, period: str, n_states: int, data: dict) -> None:
        """Display HMM regime detection table"""
        returns       = data["returns"]
        cond_vol      = data["cond_vol"]
        hidden_states = data["hidden_states"]
        regime_labels = data["regime_labels"]
        order         = data["order"]
        last_date     = data["last_date"]
        current_regime = regime_labels[hidden_states[-1]]
        out  = f"\n--- REGIME DETECTION FOR {ticker} ({period}, {n_states} states) ---\n"
        out += f"Current regime ({last_date}): {current_regime}\n\n"
        out += f"{'Regime':<14} | {'Days':>6} | {'% Time':>7} | {'Avg Daily Return':>17} | {'Avg Daily Vol':>14}\n"
        out += "-" * 68 + "\n"
        for s in order:
            mask    = hidden_states == s # Amount of states, chosen by user
            days    = mask.sum()
            pct     = 100 * days / len(hidden_states)
            avg_ret = returns[mask].mean()
            avg_v   = cond_vol[mask].mean()
            out += f"{regime_labels[s]:<14} | {days:>6} | {pct:>6.1f}% | {avg_ret:>16.4f}% | {avg_v:>13.4f}%\n"
        print(out)

    def display_simulation_results(self, data: dict) -> None:
        """Display Monte Carlo simulation text results table"""
        N_PATHS   = data["N_PATHS"] # Amount of paths for simulating
        N_YEARS   = data["N_YEARS"] # Amount of years for simulating
        year_rows = data["year_rows"]
        summary   = data["summary"]
        result  = f"\n--- MONTE CARLO SIMULATION (15 Years, 100,000 Paths) ---\n"
        result += f"Initial Portfolio Value: ${data['total_initial_value']:,.2f}\n\n"
        result += f"{'Year':>6} | {'1st %ile':>14} | {'5th %ile':>14} | {'25th %ile':>14} | {'Median':>14} | {'75th %ile':>14} | {'95th %ile':>14} | {'99th %ile':>14}\n"
        result += "-" * 120 + "\n"
        for year in range(0, N_YEARS + 1, 3):
            row = year_rows[year]
            result += f"{year:>6} | ${row[0]:>13,.0f} | ${row[1]:>13,.0f} | ${row[2]:>13,.0f} | ${row[3]:>13,.0f} | ${row[4]:>13,.0f} | ${row[5]:>13,.0f} | ${row[6]:>13,.0f}\n"
        row = year_rows[N_YEARS]
        result += f"{'15':>6} | ${row[0]:>13,.0f} | ${row[1]:>13,.0f} | ${row[2]:>13,.0f} | ${row[3]:>13,.0f} | ${row[4]:>13,.0f} | ${row[5]:>13,.0f} | ${row[6]:>13,.0f}\n"
        result += "-" * 120 + "\n"
        result += f"\nAfter 15 years ({N_PATHS:,} simulated paths):\n"
        result += f"  Extreme worst (1st pct):  ${summary['p1']:>15,.2f}\n"
        result += f"  Worst case   (5th pct):  ${summary['p5']:>15,.2f}\n"
        result += f"  Median outcome (50th):   ${summary['p50']:>15,.2f}\n"
        result += f"  Best case   (95th pct):  ${summary['p95']:>15,.2f}\n"
        result += f"  Extreme best (99th pct): ${summary['p99']:>15,.2f}\n"
        print(result)

    def display_return(self, total_cost: float, total_value: float, total_pnl: float, total_ret_pct: float) -> None:
        """Display portfolio P&L and return table"""
        pnl_str = ("+" if total_pnl >= 0 else "-") + f"${abs(total_pnl):>10.2f}"
        ret_str = ("+" if total_ret_pct >= 0 else "") + f"{total_ret_pct:>9.2f}%"
        result  = "\n--- PORTFOLIO RETURN ---\n"
        result += f"{'Transaction Value':>14} | {'Current Value':>12} | {'P&L ($)':>13} | {'Return (%)':>11}\n"
        result += "-" * 58 + "\n"
        result += f"${total_cost:>13,.2f} | ${total_value:>11,.2f} | {pnl_str} | {ret_str}\n"
        print(result)

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
        """Display GARCH(1,1) conditional volatility graph, for a given period"""
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
        plt.figure(figsize=(14, 7))
        sample_idx = np.random.choice(n_paths, size=200, replace=False)
        for i in sample_idx:
            plt.plot(years, portfolio_paths[i] / 1e3, color='steelblue', alpha=0.03, linewidth=0.5)

        # The colored bands for the percentiles are plotted on top of the individual paths for better visibility    
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