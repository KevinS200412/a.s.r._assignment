"""Portfolio model: data storage and management"""

import numpy as np
import yfinance as yf
from arch import arch_model
from hmmlearn.hmm import GaussianHMM # Machine learning package for Hidden Markov Models

class Stock:
    """Represents single stock holding"""
    def __init__(self, ticker: str, sector: str, asset_class: str, quantity: int, price: float):
        self.ticker = ticker
        self.sector = sector
        self.asset_class = asset_class
        self.quantity = quantity
        self.price = price
        self.total_cost_invested = quantity * price  # Track total cost of all purchases (transaction value)
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
    
    def add_stock(self, ticker: str, sector: str, asset_class: str, quantity: int, price: float) -> float:
        """Add a stock to portfolio or update if exists. Returns total purchase cost of the current buy."""
        ticker = ticker.upper() # Normalize ticker input to uppercase
        if ticker in self.holdings:
            self.holdings[ticker].quantity += quantity
            self.holdings[ticker].add_price(price, additional_quantity=quantity)
        else:
            self.holdings[ticker] = Stock(ticker, sector, asset_class, quantity, price)
        return quantity * price
    
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
    
    def total_transaction_value(self) -> float:
        """Calculate total transaction value (sum of all purchases)"""
        return sum(stock.transaction_value() for stock in self.holdings.values())
    
    def get_holdings_by_sector(self) -> dict:
        """Group holdings by sector. Returns dict with sector as key and list of stocks as value"""
        by_sector = {}
        for stock in self.holdings.values():
            if stock.sector not in by_sector:
                by_sector[stock.sector] = []
            by_sector[stock.sector].append(stock) # Add stock, if belonging to this sector
        return by_sector
    
    def get_holdings_by_asset_class(self) -> dict:
        """Group holdings by asset class. Returns dict with asset class as key and list of stocks as value"""
        by_class = {}
        for stock in self.holdings.values():
            if stock.asset_class not in by_class:
                by_class[stock.asset_class] = []
            by_class[stock.asset_class].append(stock) # Add stock, if belonging to this asset class
        return by_class

    def get_sector_value(self, sector_name: str) -> float:
        """Calculate total current value of all holdings in a given sector"""
        return sum(s.total_value() for s in self.get_holdings_by_sector().get(sector_name, []))

    def get_class_value(self, class_name: str) -> float:
        """Calculate total current value of all holdings in a given asset class"""
        return sum(s.total_value() for s in self.get_holdings_by_asset_class().get(class_name, []))

    def simulate_monte_carlo(self) -> dict:
        """Run Monte Carlo GBM simulation (15 years, 100,000 paths). Returns results dict."""
        CLASS_PARAMS = {
            # (mean return, volatility), based on historical averages and standard values
            "stock":     (0.10, 0.18),
            "bond":      (0.04, 0.06),
            "etf":       (0.09, 0.15),
            "commodity": (0.05, 0.20),
        }
        # If assets have class, which is not equal to above, we will use these default parameters
        DEFAULT_PARAMS = (0.08, 0.15)

        N_PATHS = 100_000
        N_YEARS = 15
        dt      = 1.0

        holdings            = self.list_holdings()
        total_initial_value = self.total_portfolio_value()

        # Create df for simulation, every row is a path, every column is a year
        portfolio_paths       = np.zeros((N_PATHS, N_YEARS + 1))
        portfolio_paths[:, 0] = total_initial_value
        increments            = np.zeros((N_PATHS, N_YEARS))

        for stock in holdings:
            mu, sigma   = CLASS_PARAMS.get(stock.asset_class.lower(), DEFAULT_PARAMS)
            initial     = stock.total_value()
            Z           = np.random.standard_normal((N_PATHS, N_YEARS))

            # Geometric Brownian Motion (GBM) log-return: drift-corrected mean (Itô's lemma) + stochastic shock
            log_returns = (mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z

            asset_paths = initial * np.exp(np.cumsum(log_returns, axis=1))
            increments += asset_paths

        portfolio_paths[:, 1:] = increments

        percentiles  = [1, 5, 25, 50, 75, 95, 99]
        pct_values   = np.percentile(portfolio_paths, percentiles, axis=0)
        final_values = portfolio_paths[:, -1]

        year_rows = {
            year: [float(np.percentile(portfolio_paths[:, year], p)) for p in percentiles]
            for year in range(N_YEARS + 1)
        }
        summary = {
            # Percentiles of final portfolio values after 15 years
            "p1":  float(np.percentile(final_values, 1)),
            "p5":  float(np.percentile(final_values, 5)),
            "p50": float(np.median(final_values)),
            "p95": float(np.percentile(final_values, 95)),
            "p99": float(np.percentile(final_values, 99)),
        }
        return {
            "portfolio_paths":     portfolio_paths,
            "pct_values":          pct_values,
            "total_initial_value": total_initial_value,
            "N_PATHS":             N_PATHS,
            "N_YEARS":             N_YEARS,
            "percentiles":         percentiles,
            "year_rows":           year_rows,
            "summary":             summary,
            "years":               list(range(N_YEARS + 1)),
        }

    def get_live_price(self, ticker: str):
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if hist.empty or hist['Close'].dropna().empty:
                return None
            return float(hist['Close'].dropna().iloc[-1])
        except:
            return None

    def refresh_prices(self):
        if not self.holdings:
            return

        tickers = list(self.holdings.keys())

        try:
            data = yf.download(tickers, period="5d", progress=False, auto_adjust=True)
            close = data["Close"]

            if close.ndim == 1:
                close = close.to_frame(name=tickers[0])

            for ticker, stock in self.holdings.items():
                if ticker in close:
                    col = close[ticker].dropna()
                    if not col.empty:
                        stock.price = float(col.iloc[-1])
        except:
            pass

    def get_return(self):
        total_cost = self.total_transaction_value()
        total_value = self.total_portfolio_value()
        pnl = total_value - total_cost
        pct = (pnl / total_cost * 100) if total_cost > 0 else 0
        return total_cost, total_value, pnl, pct

    def get_weights(self):
        total = self.total_portfolio_value()
        result = []
        for stock in self.holdings.values():
            value = stock.total_value()
            weight = (value / total * 100) if total > 0 else 0
            result.append((stock.ticker, value, weight))
        return result

    # From here on static methods, because they only need a ticker as input and don't use any portfolio data

    @staticmethod
    def fit_garch(ticker: str, period: str) -> dict:
        """Fetch price data and fit GARCH(1,1). Returns result dict or raises on insufficient data."""

        hist = yf.Ticker(ticker).history(period=period)
        if hist.empty or len(hist) < 30: # We need enough data to fit GARCH
            raise ValueError(f"Not enough data for '{ticker}' to fit GARCH (need at least 30 observations).")

        closes  = hist['Close'].dropna()
        returns = 100 * np.log(closes / closes.shift(1)).dropna()

        # Fit GARCH(1,1) model to returns
        model   = arch_model(returns, vol='Garch', p=1, q=1, dist='normal', rescale=False)

        res     = model.fit(disp='off')

        forecast            = res.forecast(horizon=1, reindex=False)
        predicted_vol_daily  = float(np.sqrt(forecast.variance.iloc[-1, 0]))
        predicted_vol_annual = predicted_vol_daily * np.sqrt(252)

        return {
            "returns":             returns,
            "cond_vol":            res.conditional_volatility,
            "predicted_vol_daily":  predicted_vol_daily,
            "predicted_vol_annual": predicted_vol_annual,
            "last_date":           returns.index[-1].strftime('%Y-%m-%d'),
        }

    @staticmethod
    def detect_regimes(ticker: str, period: str, n_states: int) -> dict:
        """Fit GARCH(1,1) + Gaussian HMM to detect market regimes. Returns result dict or raises."""

        hist = yf.Ticker(ticker).history(period=period)
        if hist.empty or len(hist) < 60:
            raise ValueError(f"Not enough data for '{ticker}' to detect regimes (need at least 60 observations).")

        closes    = hist['Close'].dropna()
        returns   = 100 * np.log(closes / closes.shift(1)).dropna()
        garch     = arch_model(returns, vol='Garch', p=1, q=1, dist='normal', rescale=False)
        garch_res = garch.fit(disp='off')
        cond_vol  = garch_res.conditional_volatility.values

        X     = np.column_stack([returns.values, cond_vol])
        model = GaussianHMM(n_components=n_states, covariance_type='full', n_iter=200, random_state=42)
        model.fit(X)
        hidden_states = model.predict(X)

        state_vols = [cond_vol[hidden_states == s].mean() for s in range(n_states)]
        order      = np.argsort(state_vols)
        rank       = np.empty_like(order)
        for r, s in enumerate(order):
            rank[s] = r

        if n_states == 2:
            names = ["Low Vol", "High Vol"]
        elif n_states == 3:
            names = ["Low Vol", "Medium Vol", "High Vol"]
        else:
            names = [f"Regime {i+1}" for i in range(n_states)]
        regime_labels = [names[rank[s]] for s in range(n_states)]

        return {
            "returns":       returns.values,
            "cond_vol":      cond_vol,
            "hidden_states": hidden_states,
            "regime_labels": regime_labels,
            "order":         order,
            "n_states":      n_states,
            "last_date":     returns.index[-1].strftime('%Y-%m-%d'),
        }

    @staticmethod
    def get_ticker_history(ticker: str, period: str):
        """Fetch OHLCV price history for a ticker. Returns DataFrame or raises ValueError."""
        hist = yf.Ticker(ticker).history(period=period)
        if hist.empty:
            raise ValueError(f"No historical data available for '{ticker}'. Make sure it is a valid Yahoo Finance ticker.")
        return hist

    @staticmethod
    def get_ticker_volume(ticker: str, period: str) -> dict:
        """Fetch volume statistics for a ticker. Returns dict or raises ValueError."""
        hist = yf.Ticker(ticker).history(period=period)
        if hist.empty:
            raise ValueError(f"No data available for '{ticker}'. Make sure it is a valid Yahoo Finance ticker.")
        return {
            "avg_vol":   int(hist['Volume'].mean()),
            "last_vol":  int(hist['Volume'].iloc[-1]),
            "last_date": hist.index[-1].strftime('%Y-%m-%d'),
        }

    @staticmethod
    def get_tickers_graph_data(tickers: list) -> dict:
        """Fetch 1-year price history for one or more tickers. Returns {ticker: DataFrame} or raises ValueError."""
        not_found = []
        hist_dict = {}
        for ticker in tickers:
            hist = yf.Ticker(ticker).history(period="1y")
            if hist.empty or hist['Close'].dropna().empty:
                not_found.append(ticker)
                continue
            hist_dict[ticker] = hist
        if not_found:
            raise ValueError(f"No data found on Yahoo Finance for: {', '.join(not_found)}")
        return hist_dict
