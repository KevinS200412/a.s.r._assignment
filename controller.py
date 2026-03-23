"""Portfolio controller: handles CLI commands and user inputs"""

import yfinance as yf
from model import Portfolio


class PortfolioController:
    """Handles user commands and portfolio operations"""
    
    def __init__(self):
        self.portfolio = Portfolio()

    def _validate_and_fetch_price(self, ticker: str) -> tuple:
        """
        Validates that a ticker exists on Yahoo Finance and returns its current price.
        Returns (price, None) on success, or (None, error_message) on failure.
        """
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if hist.empty or hist['Close'].dropna().empty:
                return None, f"- Error: '{ticker}' was not found on Yahoo Finance. Cannot add this asset."
            price = float(hist['Close'].dropna().iloc[-1])
            return round(price, 4), None
        except Exception:
            return None, f"- Error: Could not fetch data for '{ticker}' from Yahoo Finance. Cannot add this asset."

    def _refresh_portfolio_prices(self) -> None:
        """Update all stock prices in the portfolio with live data from Yahoo Finance."""
        holdings = self.portfolio.list_holdings()
        if not holdings:
            return
        for stock in holdings:
            try:
                hist = yf.Ticker(stock.ticker).history(period="5d")
                if not hist.empty:
                    closes = hist['Close'].dropna()
                    if len(closes) > 0:
                        stock.price = round(float(closes.iloc[-1]), 4)
            except Exception:
                pass  # Keep existing price if refresh fails

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
        
        elif command == "simulate":
            return self._handle_simulate()
        
        elif command == "help":
            return self._handle_help()
        
        elif command == "quit" or command == "exit":
            return "- QUIT"
        
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
        live_price, error = self._validate_and_fetch_price(ticker)
        if error:
            return error

        # Use user-specified price for cost basis, live price if not specified
        cost_price = purchase_price if purchase_price is not None else live_price

        self.portfolio.add_stock(ticker, sector, asset_class, quantity, cost_price)

        # Always update current price to the live market price
        stock = self.portfolio.get_stock(ticker)
        stock.price = live_price

        total_cost = quantity * cost_price
        return f"- Added {quantity} shares of {ticker} ({sector}) ({asset_class}) at ${cost_price:.2f} = ${total_cost:.2f} total"
    
    def _handle_list(self) -> str:
        """Handle 'list' command, shows all holdings"""
        holdings = self.portfolio.list_holdings()

        if not holdings:
            return "- Portfolio is empty. Use 'add' to add stocks."

        # Refresh prices from Yahoo Finance before displaying
        self._refresh_portfolio_prices()

        result = "\n--- PORTFOLIO HOLDINGS (live prices from Yahoo Finance) ---\n"
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
        """Handle 'value' command, show total portfolio value"""
        self._refresh_portfolio_prices()
        total = self.portfolio.total_portfolio_value()
        return f"- Total Portfolio Value (live prices): ${total:.2f}"
    
    def _handle_weights(self, args: list) -> str:
        """Handle 'weights' command, show portfolio weights and breakdowns"""
        holdings = self.portfolio.list_holdings()

        if not holdings:
            return "- Portfolio is empty. Use 'add' to add stocks."

        # Refresh prices from Yahoo Finance before computing weights
        self._refresh_portfolio_prices()
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
            hist = yf.Ticker(ticker).history(period=period)
            if hist.empty:
                return f"- No historical data available for '{ticker}'. Make sure it is a valid Yahoo Finance ticker."

            result = f"\n--- PRICE HISTORY FOR {ticker} (Period: {period}, source: Yahoo Finance) ---\n"
            result += f"{'Date':12} | {'Close':10}\n"
            result += "-" * 26 + "\n"
            for date, row in hist.iterrows():
                date_str = date.strftime('%Y-%m-%d')
                result += f"{date_str:12} | ${row['Close']:9.2f}\n"

            if stock:
                result += f"\nCurrent Price: ${stock.price:.2f} | Avg Purchase Price: ${stock.get_average_purchase_price():.2f}\n"
            return result

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
            hist = yf.Ticker(ticker).history(period=period)
            if hist.empty:
                return f"- No data available for '{ticker}'. Make sure it is a valid Yahoo Finance ticker."

            avg_vol = int(hist['Volume'].mean())
            last_vol = int(hist['Volume'].iloc[-1])
            last_date = hist.index[-1].strftime('%Y-%m-%d')

            result = f"\n--- VOLUME INFO FOR {ticker} (Period: {period}, source: Yahoo Finance) ---\n"
            result += f"Avg Volume (Period: {period}): {avg_vol:,}\n"
            result += f"Last Volume ({last_date}): {last_vol:,}\n"
            return result

        except Exception as e:
            return f"- Error fetching volume for {ticker}: {str(e)}"

    def _garch_fit(self, ticker: str, period: str):
        """Shared helper: fetch data, fit GARCH(1,1), return (result, returns, predicted_vol_daily, last_date) or raises."""
        import numpy as np
        from arch import arch_model

        hist = yf.Ticker(ticker).history(period=period)
        if hist.empty or len(hist) < 30:
            raise ValueError(f"Not enough data for '{ticker}' to fit GARCH (need at least 30 observations).")

        closes = hist['Close'].dropna()
        returns = 100 * np.log(closes / closes.shift(1)).dropna()
        last_date = closes.index[-1].strftime('%Y-%m-%d')

        model = arch_model(returns, vol='Garch', p=1, q=1, dist='normal', rescale=False)
        result = model.fit(disp='off')

        forecast = result.forecast(horizon=1, reindex=False)
        predicted_vol_daily = float(np.sqrt(forecast.variance.iloc[-1, 0]))
        predicted_vol_annual = predicted_vol_daily * np.sqrt(252)

        return result, returns, predicted_vol_daily, predicted_vol_annual, last_date

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
            from arch import arch_model
        except ImportError:
            return "- Error: 'arch' package required. Run: pip install arch"

        try:
            import numpy as np
            result, returns, predicted_vol_daily, predicted_vol_annual, last_date = self._garch_fit(ticker, period)

            out  = f"\n--- GARCH(1,1) VOLATILITY FORECAST FOR {ticker} ---\n"
            out += f"Fitted on {period} of data ({len(returns)} obs, up to {last_date})\n"
            out += f"Predicted daily vol (today): {predicted_vol_daily:.4f}%\n"
            return out

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
            from arch import arch_model
        except ImportError:
            return "- Error: 'arch' package required. Run: pip install arch"

        try:
            import matplotlib.pyplot as plt
            result, returns, predicted_vol_daily, predicted_vol_annual, last_date = self._garch_fit(ticker, period)

            cond_vol = result.conditional_volatility
            plt.figure(figsize=(12, 5))
            plt.plot(returns.index, cond_vol, color='steelblue', linewidth=1, label='Conditional volatility (daily %)')
            plt.axhline(predicted_vol_daily, color='red', linestyle='--', linewidth=1.5,
                        label=f'Today forecast: {predicted_vol_daily:.3f}%')
            plt.title(f'GARCH(1,1) Conditional Volatility — {ticker} ({period})')
            plt.xlabel('Date')
            plt.ylabel('Daily Volatility (%)')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()

            return f"- GARCH(1,1) historical volatility graph displayed for {ticker}."

        except Exception as e:
            return f"- Error running GARCH model for {ticker}: {str(e)}"

    def _handle_regime(self, args: list) -> str:
        """Handle 'regime TICKER [PERIOD] [--states N]' - HMM regime detection on GARCH volatility.
        Fits a Gaussian HMM on daily returns + GARCH vol, labels each day as a market regime,
        and plots the price series coloured by regime. Also reports current regime.
        """
        if len(args) < 1:
            return "- Usage: regime TICKER [PERIOD] [--states N]\nExample: regime AAPL\nExample: regime AAPL 5y\nExample: regime AAPL 5y --states 3"

        ticker = args[0].upper()

        # Parse optional --states flag and period
        remaining = args[1:]
        n_states = 3  # default: low / medium / high vol
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
            from hmmlearn.hmm import GaussianHMM
        except ImportError:
            return "- Error: 'hmmlearn' package required. Run: pip install hmmlearn"

        try:
            import numpy as np
            from arch import arch_model

            hist = yf.Ticker(ticker).history(period=period)
            if hist.empty or len(hist) < 60:
                return f"- Error: Not enough data for '{ticker}' to detect regimes (need at least 60 observations)."

            closes = hist['Close'].dropna()
            returns = 100 * np.log(closes / closes.shift(1)).dropna()
            aligned_closes = closes.loc[returns.index]

            # Fit GARCH(1,1) to get conditional volatility series
            garch = arch_model(returns, vol='Garch', p=1, q=1, dist='normal', rescale=False)
            garch_res = garch.fit(disp='off')
            cond_vol = garch_res.conditional_volatility.values

            # Feature matrix: [return, GARCH vol]
            X = np.column_stack([returns.values, cond_vol])

            # Fit Gaussian HMM
            model = GaussianHMM(n_components=n_states, covariance_type='full',
                                n_iter=200, random_state=42)
            model.fit(X)
            hidden_states = model.predict(X)

            # Label regimes by mean GARCH vol (ascending = low -> high vol)
            state_vols = [cond_vol[hidden_states == s].mean() for s in range(n_states)]
            order = np.argsort(state_vols)   # index of states sorted low->high vol
            rank = np.empty_like(order)      # rank[state] = 0(low)..N-1(high)
            for r, s in enumerate(order):
                rank[s] = r

            regime_labels = [None] * n_states
            if n_states == 2:
                names = ["Low Vol", "High Vol"]
            elif n_states == 3:
                names = ["Low Vol", "Medium Vol", "High Vol"]
            else:
                names = [f"Regime {i+1}" for i in range(n_states)]
            for s in range(n_states):
                regime_labels[s] = names[rank[s]]

            # Terminal summary: current regime + stats per regime
            current_state = hidden_states[-1]
            current_regime = regime_labels[current_state]
            last_date = aligned_closes.index[-1].strftime('%Y-%m-%d')

            out  = f"\n--- REGIME DETECTION FOR {ticker} ({period}, {n_states} states) ---\n"
            out += f"Current regime ({last_date}): {current_regime}\n\n"
            out += f"{'Regime':<14} | {'Days':>6} | {'% Time':>7} | {'Avg Daily Return':>17} | {'Avg Daily Vol':>14}\n"
            out += "-" * 68 + "\n"
            for s in order:  # iterate in volatility ascending order (Low -> High)
                mask = hidden_states == s
                days = mask.sum()
                pct = 100 * days / len(hidden_states)
                avg_ret = returns.values[mask].mean()
                avg_v = cond_vol[mask].mean()
                out += f"{regime_labels[s]:<14} | {days:>6} | {pct:>6.1f}% | {avg_ret:>16.4f}% | {avg_v:>13.4f}%\n"
            return out

        except Exception as e:
            return f"- Error running regime detection for {ticker}: {str(e)}"

    def _handle_simulate(self) -> str:
        """Handle 'simulate' command, Monte Carlo simulation over 15 years with 100,000 paths"""
        holdings = self.portfolio.list_holdings()

        if not holdings:
            return "- Portfolio is empty. Use 'add' to add stocks."

        try:
            import numpy as np
            import matplotlib.pyplot as plt
        except ImportError:
            return "- Error: numpy and matplotlib required. Run: pip install -r requirements.txt"

        # Expected annual return and volatility per asset class (mu, sigma), based on historical averages
        CLASS_PARAMS = {
            "stock":     (0.10, 0.18),  # 10% return, 18% volatility
            "bond":      (0.04, 0.06),  # 4% return, 6% volatility
            "etf":       (0.09, 0.15),  # 9% return, 15% volatility
            "commodity": (0.05, 0.20),  # 5% return, 20% volatility
        }
        DEFAULT_PARAMS = (0.08, 0.15)  # If class is different than the ones above

        N_PATHS = 100_000
        N_YEARS = 15
        N_STEPS = N_YEARS  # One step per year
        dt = 1.0           # Annual time step

        total_initial_value = self.portfolio.total_portfolio_value()
        if total_initial_value <= 0:
            return "- Portfolio has no value to simulate."

        # Simulate total portfolio value across paths using weighted Geometric Brownian Motion (GBM) for each asset class
        # Each asset contributes its weight * GBM path
        portfolio_paths = np.zeros((N_PATHS, N_STEPS + 1))
        portfolio_paths[:, 0] = total_initial_value

        for stock in holdings:
            weight = stock.total_value() / total_initial_value
            mu, sigma = CLASS_PARAMS.get(stock.asset_class.lower(), DEFAULT_PARAMS)
            initial = stock.total_value()

            # Geometric Brownian Motion: S(t+dt) = S(t) * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z)
            Z = np.random.standard_normal((N_PATHS, N_STEPS))
            log_returns = (mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z
            # Build price paths via cumulative product
            asset_paths = initial * np.exp(np.cumsum(log_returns, axis=1))
            # Add initial value as t=0 column
            asset_paths = np.hstack([np.full((N_PATHS, 1), initial), asset_paths])
            portfolio_paths += asset_paths - initial  # Add asset contribution

        # Use only the asset-driven paths (reset to correct initial)
        # Recalculate properly: portfolio = sum of all asset paths
        portfolio_paths_final = np.zeros((N_PATHS, N_STEPS + 1))
        portfolio_paths_final[:, 0] = total_initial_value

        increments = np.zeros((N_PATHS, N_STEPS))
        for stock in holdings:
            mu, sigma = CLASS_PARAMS.get(stock.asset_class.lower(), DEFAULT_PARAMS)
            initial = stock.total_value()
            Z = np.random.standard_normal((N_PATHS, N_STEPS))
            log_returns = (mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z
            asset_paths = initial * np.exp(np.cumsum(log_returns, axis=1))
            increments += asset_paths

        portfolio_paths_final[:, 1:] = increments

        # Compute percentiles at each year
        percentiles = [1, 5, 25, 50, 75, 95, 99]
        pct_values = np.percentile(portfolio_paths_final, percentiles, axis=0)
        final_values = portfolio_paths_final[:, -1]

        # Summary statistics
        result = f"\n--- MONTE CARLO SIMULATION (15 Years, 100,000 Paths) ---\n"
        result += f"Initial Portfolio Value: ${total_initial_value:,.2f}\n\n"
        result += f"{'Year':>6} | {'1st %ile':>14} | {'5th %ile':>14} | {'25th %ile':>14} | {'Median':>14} | {'75th %ile':>14} | {'95th %ile':>14} | {'99th %ile':>14}\n"
        result += "-" * 120 + "\n"
        for year in range(0, N_YEARS + 1, 3):
            row = [np.percentile(portfolio_paths_final[:, year], p) for p in percentiles]
            result += f"{year:>6} | ${row[0]:>13,.0f} | ${row[1]:>13,.0f} | ${row[2]:>13,.0f} | ${row[3]:>13,.0f} | ${row[4]:>13,.0f} | ${row[5]:>13,.0f} | ${row[6]:>13,.0f}\n"
        # Always show year 15
        row = [np.percentile(portfolio_paths_final[:, 15], p) for p in percentiles]
        result += f"{'15':>6} | ${row[0]:>13,.0f} | ${row[1]:>13,.0f} | ${row[2]:>13,.0f} | ${row[3]:>13,.0f} | ${row[4]:>13,.0f} | ${row[5]:>13,.0f} | ${row[6]:>13,.0f}\n"
        result += "-" * 120 + "\n"
        result += f"\nAfter 15 years ({N_PATHS:,} simulated paths):\n"
        result += f"  Extreme worst (1st pct):  ${np.percentile(final_values, 1):>15,.2f}\n"
        result += f"  Worst case   (5th pct):  ${np.percentile(final_values, 5):>15,.2f}\n"
        result += f"  Median outcome (50th):   ${np.median(final_values):>15,.2f}\n"
        result += f"  Best case   (95th pct):  ${np.percentile(final_values, 95):>15,.2f}\n"
        result += f"  Extreme best (99th pct): ${np.percentile(final_values, 99):>15,.2f}\n"

        # Plot simulation
        years = np.arange(N_YEARS + 1)
        plt.figure(figsize=(14, 7))
        # Plot a sample of paths in light grey
        sample_idx = np.random.choice(N_PATHS, size=200, replace=False)
        for i in sample_idx:
            plt.plot(years, portfolio_paths_final[i] / 1e3, color='steelblue', alpha=0.03, linewidth=0.5)
        # Plot percentile bands (1st-99th, 5th-95th, 25th-75th)
        plt.fill_between(years, pct_values[0] / 1e3, pct_values[6] / 1e3, alpha=0.08, color='red', label='1st–99th pct')
        plt.fill_between(years, pct_values[1] / 1e3, pct_values[5] / 1e3, alpha=0.15, color='orange', label='5th–95th pct')
        plt.fill_between(years, pct_values[2] / 1e3, pct_values[4] / 1e3, alpha=0.25, color='orange', label='25th–75th pct')
        plt.plot(years, pct_values[3] / 1e3, color='darkorange', linewidth=2.5, label='Median')
        plt.axhline(y=total_initial_value / 1e3, color='red', linestyle='--', linewidth=1.5, label='Initial Value')
        plt.title(f"Portfolio Monte Carlo Simulation — 15 Years, {N_PATHS:,} Paths", fontsize=14)
        plt.xlabel("Year")
        plt.ylabel("Portfolio Value ($000s)")
        plt.legend(loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, N_YEARS + 1))
        plt.tight_layout()
        plt.show()

        return result

    def _handle_help(self) -> str:
        """Show available commands"""
        help_text = """
--- PORTFOLIO TRACKER COMMANDS ---
  add TICKER SECTOR ASSET_CLASS QUANTITY [PURCHASE_PRICE]  - Add asset to portfolio
                                                              PURCHASE_PRICE is optional; if omitted, the live price is used as purchase price
                                                              Current value always reflects the live Yahoo Finance price
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
  simulate                                     - Run Monte Carlo simulation (15yr, 100k paths)
  remove TICKER                                - Remove asset from portfolio
  help                                         - Show this help message
  quit / exit                                  - Exit the program
"""
        return help_text

    def _handle_graph(self, args: list) -> str:
        """Handle 'graph TICKER1 TICKER2 ...' command - displays 1-year price charts from Yahoo Finance"""
        if len(args) < 1:
            return "- Usage: graph TICKER [TICKER2 TICKER3 ...]\nExample: graph AAPL\nExample: graph AAPL MSFT GOOGL"

        try:
            import matplotlib.pyplot as plt

            tickers = [t.upper() for t in args]
            not_found = []

            plt.figure(figsize=(12, 7))

            for ticker in tickers:
                hist = yf.Ticker(ticker).history(period="1y") # Show historical price for 1 year
                if hist.empty or hist['Close'].dropna().empty:
                    not_found.append(ticker)
                    continue
                plt.plot(hist.index, hist['Close'], linewidth=2, label=ticker)

            if not_found:
                plt.close()
                return f"- Error: No data found on Yahoo Finance for: {', '.join(not_found)}"

            plotted = [t for t in tickers if t not in not_found]

            plt.title("Price History — 1 Year (Yahoo Finance)")
            plt.xlabel("Date")
            plt.ylabel("Price ($)")
            plt.legend(loc='best')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()

            return f"- Graph displayed for: {', '.join(plotted)}"

        except ImportError:
            return "- Error: matplotlib required. Run: pip install -r requirements.txt"
        except Exception as e:
            return f"- Error generating graph: {str(e)}"
