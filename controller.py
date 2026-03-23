"""Portfolio controller: handles CLI commands and user inputs"""

from model import Portfolio


class PortfolioController:
    """Handles user commands and portfolio operations"""
    
    def __init__(self, view=None):
        self.portfolio = Portfolio()
        self.view = view

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

        elif command == "volume":
            return self._handle_volume(args)

        elif command == "predict":
            if args and args[0].lower() == "volatility":
                return self._handle_volatility(args[1:])
            return "- Usage: predict volatility TICKER [PERIOD]"

        elif command == "historical":
            if args and args[0].lower() == "volatility":
                return self._handle_historical_volatility(args[1:])
            return "- Usage: historical volatility TICKER [PERIOD]"

        elif command == "regime":
            return self._handle_regime(args)

        elif command == "graph":
            return self._handle_graph(args)
        
        elif command == "remove":
            return self._handle_remove(args)
        
        elif command == "value":
            return self._handle_value()
        
        elif command == "weights":
            return self._handle_weights(args)
        
        elif command == "return":
            return self._handle_return()

        elif command == "simulate":
            return self._handle_simulate()
        
        elif command == "help":
            return self._handle_help()
        
        elif command == "quit" or command == "exit":
            return "QUIT"
        
        else:
            return f"- Unknown command: {command}. Type 'help' for available commands."
    
    def _handle_add(self, args: list) -> str:
        """Handle 'add TICKER SECTOR ASSET_CLASS QUANTITY [PURCHASE_PRICE]' command.
        PURCHASE_PRICE is optional. If omitted, the live Yahoo Finance price is used as the purchase price.
        Current value always reflects the live price from Yahoo Finance.
        """
        if len(args) < 4:
            return "- Usage: add TICKER SECTOR ASSET_CLASS QUANTITY [PURCHASE_PRICE]\nExample: add AAPL tech stock 10\nExample: add AAPL tech stock 10 154.00"

        ticker = args[0].upper()
        sector = args[1]
        asset_class = args[2]

        try:
            quantity = int(args[3])
        except ValueError:
            return "- Error: QUANTITY must be an integer"

        if quantity <= 0:
            return "- Error: QUANTITY must be positive"

        # Parse optional purchase price
        purchase_price = None
        if len(args) >= 5:
            try:
                purchase_price = float(args[4])
            except ValueError:
                return "- Error: PURCHASE_PRICE must be a number"
            if purchase_price <= 0:
                return "- Error: PURCHASE_PRICE must be positive"

        # Validate ticker exists on Yahoo Finance and fetch live price
        live_price = self.portfolio.get_live_price(ticker)
        if live_price is None:
            return f"- Error: '{ticker}' not found on Yahoo Finance."

        # Use user-specified price for cost basis, live price if not specified
        cost_price = purchase_price if purchase_price is not None else live_price

        total_cost = self.portfolio.add_stock(ticker, sector, asset_class, quantity, cost_price)

        # Always update current price to the live market price
        self.portfolio.get_stock(ticker).price = live_price

        return f"- Added {quantity} shares of {ticker} ({sector}) ({asset_class}) at ${cost_price:.2f} = ${total_cost:.2f} total"
    
    def _handle_list(self) -> str:
        """Handle 'list' command, shows all holdings"""
        holdings = self.portfolio.list_holdings()

        if not holdings:
            return "- Portfolio is empty. Use 'add' to add stocks."

        self.portfolio.refresh_prices()
        self.view.display_holdings(holdings)
        return ""
    
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
        """Handle 'value' command, show total portfolio value"""
        self.portfolio.refresh_prices()
        total = self.portfolio.total_portfolio_value()
        return f"- Total Portfolio Value (live prices): ${total:.2f}"
    
    def _handle_weights(self, args: list) -> str:
        """Handle 'weights' command, show portfolio weights and breakdowns"""
        holdings = self.portfolio.list_holdings()

        if not holdings:
            return "- Portfolio is empty. Use 'add' to add stocks."

        self.portfolio.refresh_prices()
        total_value = self.portfolio.total_portfolio_value()

        if len(args) == 0:
            self.view.display_weights(holdings, total_value, self.portfolio.total_transaction_value())
            return ""

        elif args[0].lower() == "sectors":
            self.view.display_sector_weights(self.portfolio.get_holdings_by_sector(), total_value)
            return ""

        elif args[0].lower() == "classes":
            self.view.display_class_weights(self.portfolio.get_holdings_by_asset_class(), total_value)
            return ""

        elif args[0].lower() == "sector" and len(args) > 1:
            sector_name = args[1].lower()
            by_sector = self.portfolio.get_holdings_by_sector()
            matching_sector = next((s for s in by_sector if s.lower() == sector_name), None)
            if not matching_sector:
                return f"- Sector '{args[1]}' not found in portfolio."
            sector_stocks = by_sector[matching_sector]
            sector_value = self.portfolio.get_sector_value(matching_sector)
            self.view.display_sector_detail(matching_sector, sector_stocks, sector_value)
            return ""

        elif args[0].lower() == "class" and len(args) > 1:
            class_name = args[1].lower()
            by_class = self.portfolio.get_holdings_by_asset_class()
            matching_class = next((c for c in by_class if c.lower() == class_name), None)
            if not matching_class:
                return f"- Asset class '{args[1]}' not found in portfolio."
            class_stocks = by_class[matching_class]
            class_value = self.portfolio.get_class_value(matching_class)
            self.view.display_class_detail(matching_class, class_stocks, class_value)
            return ""

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
        """Handle 'history TICKER [PERIOD]' command - fetches close price history from Yahoo Finance.
        PERIOD examples: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y (default: 1mo)
        """
        if len(args) < 1:
            return "- Usage: history TICKER [PERIOD]\nExample: history AAPL\nExample: history AAPL 6mo"

        ticker = args[0].upper()
        period = args[1] if len(args) > 1 else "1mo"

        valid_periods = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
        if period not in valid_periods:
            return f"- Error: Invalid period '{period}'. Valid options: {', '.join(sorted(valid_periods))}"

        stock = self.portfolio.get_stock(ticker)

        try:
            hist = self.portfolio.get_ticker_history(ticker, period)
            self.view.display_price_history(ticker, period, hist, stock)
            return ""

        except Exception as e:
            return f"- Error fetching history for {ticker}: {str(e)}"

    def _handle_volume(self, args: list) -> str:
        """Handle 'volume TICKER [PERIOD]' command - shows avg and last volume from Yahoo Finance.
        PERIOD examples: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y (default: 1mo)
        """
        if len(args) < 1:
            return "- Usage: volume TICKER [PERIOD]\nExample: volume AAPL\nExample: volume AAPL 6mo"

        ticker = args[0].upper()
        period = args[1] if len(args) > 1 else "1mo"

        valid_periods = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
        if period not in valid_periods:
            return f"- Error: Invalid period '{period}'. Valid options: {', '.join(sorted(valid_periods))}"

        try:
            data = self.portfolio.get_ticker_volume(ticker, period)
            self.view.display_volume(ticker, period, data)
            return ""

        except Exception as e:
            return f"- Error fetching volume for {ticker}: {str(e)}"

    def _handle_volatility(self, args: list) -> str:
        """Handle 'predict volatility TICKER [PERIOD]' - terminal-only GARCH(1,1) forecast."""
        if len(args) < 1:
            return "- Usage: predict volatility TICKER [PERIOD]\nExample: predict volatility AAPL\nExample: predict volatility AAPL 5y"

        ticker = args[0].upper()
        period = args[1] if len(args) > 1 else "2y"

        valid_periods = {"1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
        if period not in valid_periods:
            return f"- Error: Invalid period '{period}'. Valid options: {', '.join(sorted(valid_periods))}"

        try:
            data = self.portfolio.fit_garch(ticker, period)
            self.view.display_volatility_forecast(ticker, period, data)
            return ""
        except ImportError:
            return "- Error: 'arch' package required. Run: pip install arch"
        except Exception as e:
            return f"- Error running GARCH model for {ticker}: {str(e)}"

    def _handle_historical_volatility(self, args: list) -> str:
        """Handle 'historical volatility TICKER [PERIOD]' - GARCH(1,1) conditional vol graph."""
        if len(args) < 1:
            return "- Usage: historical volatility TICKER [PERIOD]\nExample: historical volatility AAPL\nExample: historical volatility AAPL 5y"

        ticker = args[0].upper()
        period = args[1] if len(args) > 1 else "2y"

        valid_periods = {"1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
        if period not in valid_periods:
            return f"- Error: Invalid period '{period}'. Valid options: {', '.join(sorted(valid_periods))}"

        try:
            data = self.portfolio.fit_garch(ticker, period)
            self.view.display_volatility_graph(
                ticker, period, data['returns'].index, data['cond_vol'], data['predicted_vol_daily']
            )
            return f"- GARCH(1,1) historical volatility graph displayed for {ticker}."
        except ImportError:
            return "- Error: 'arch' package required. Run: pip install arch"
        except Exception as e:
            return f"- Error running GARCH model for {ticker}: {str(e)}"

    def _handle_regime(self, args: list) -> str:
        """Handle 'regime TICKER [PERIOD] [--states N]' - HMM regime detection on GARCH volatility."""
        if len(args) < 1:
            return "- Usage: regime TICKER [PERIOD] [--states N]\nExample: regime AAPL\nExample: regime AAPL 5y\nExample: regime AAPL 5y --states 3"

        ticker = args[0].upper()

        remaining = args[1:]
        n_states = 3
        if "--states" in remaining:
            idx = remaining.index("--states")
            try:
                n_states = int(remaining[idx + 1])
                remaining = [a for i, a in enumerate(remaining) if i != idx and i != idx + 1]
            except (IndexError, ValueError):
                return "- Error: --states must be followed by an integer, e.g. --states 3"
        period = remaining[0] if remaining else "2y"

        valid_periods = {"1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
        if period not in valid_periods:
            return f"- Error: Invalid period '{period}'. Valid options: {', '.join(sorted(valid_periods))}"
        if not (2 <= n_states <= 6):
            return "- Error: --states must be between 2 and 6."

        try:
            data = self.portfolio.detect_regimes(ticker, period, n_states)
        except ImportError as e:
            pkg = "hmmlearn" if "hmmlearn" in str(e) else "arch"
            return f"- Error: '{pkg}' package required. Run: pip install {pkg}"
        except Exception as e:
            return f"- Error running regime detection for {ticker}: {str(e)}"

        self.view.display_regime(ticker, period, n_states, data)
        return ""

    def _handle_simulate(self) -> str:
        """Handle 'simulate' command, Monte Carlo simulation over 15 years with 100,000 paths"""
        if not self.portfolio.list_holdings():
            return "- Portfolio is empty. Use 'add' to add stocks."

        if self.portfolio.total_portfolio_value() <= 0:
            return "- Portfolio has no value to simulate."

        data = self.portfolio.simulate_monte_carlo()
        self.view.display_simulation_results(data)
        self.view.display_simulation_graph(
            data["years"], data["portfolio_paths"], data["pct_values"],
            data["total_initial_value"], data["N_PATHS"], data["N_YEARS"]
        )
        return ""

    def _handle_help(self) -> str:
        """Delegate help display to the view"""
        self.view.show_help()
        return ""

    def _handle_return(self) -> str:
        """Handle 'return' command - shows total portfolio P&L vs cost basis"""
        holdings = self.portfolio.list_holdings()

        if not holdings:
            return "- Portfolio is empty. Use 'add' to add stocks."

        self.portfolio.refresh_prices()

        total_cost, total_value, total_pnl, total_ret_pct = self.portfolio.get_return()
        self.view.display_return(total_cost, total_value, total_pnl, total_ret_pct)
        return ""

    def _handle_graph(self, args: list) -> str:
        """Handle 'graph TICKER1 TICKER2 ...' command - displays 1-year price charts from Yahoo Finance"""
        if len(args) < 1:
            return "- Usage: graph TICKER [TICKER2 TICKER3 ...]\nExample: graph AAPL\nExample: graph AAPL MSFT GOOGL"

        try:
            tickers = [t.upper() for t in args]
            hist_dict = self.portfolio.get_tickers_graph_data(tickers)
            self.view.display_price_graph(hist_dict)
            return f"- Graph displayed for: {', '.join(hist_dict.keys())}"

        except ValueError as e:
            return f"- Error: {str(e)}"
        except Exception as e:
            return f"- Error generating graph: {str(e)}"
