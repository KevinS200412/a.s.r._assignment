# Portfolio Tracker CLI

This project is a Command Line Interface (CLI) application that allows users to manage and analyze a financial portfolio. Users can add assets, track their value using live market data, and perform various analyses such as portfolio weights, historical prices, volatility forecasting, and Monte Carlo simulation.

The application is structured using the MVC (Model-View-Controller) design pattern to ensure clear separation of concerns. The controller handles CLI input and commands, the model manages portfolio data, calculations, and market analytics, and the view displays results, tables, and graphs to the user.

--------

## Features

| Category | Capability |
-----------------------------------------------------------------------------------
| **Portfolio Management** | Add / remove stocks, ETFs, bonds, commodities |
| **Live Pricing** | Real-time quotes from Yahoo Finance |
| **Holdings & Returns** | View holdings, total value, and P&L |
| **Weight Analysis** | Breakdown by asset, sector, or asset class |
| **Historical Data** | Price history and trading volume lookup |
| **Volatility Forecasting** | GARCH(1,1) predicted & historical volatility |
| **Regime Detection** | Hidden Markov Model (HMM) market regime classification |
| **Monte Carlo Simulation** | 100,000-path GBM simulation over 15 years |
| **Graphs** | Price charts, volatility curves, simulation fan charts |

-------

## Architecture

main.py          Entry point, runs the CLI event loop
controller.py    Routes commands, parses input, delegates to model/view
model.py         Portfolio data, Yahoo Finance integration, GARCH, HMM, Monte Carlo
view.py          All terminal output, tables, and matplotlib graphs

--------

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt`:
  - `matplotlib`, `numpy`, `yfinance`, `arch`, `hmmlearn`, `scikit-learn`

--------

## Getting Started

### 1. Clone the repository

```bash
git clone <https://github.com/KevinS200412/a.s.r._assignment>
cd a.s.r._assignment
```

### 2. Create and activate a virtual environment

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

You should see the welcome screen:

-----------------------------------------------------------
                PORTFOLIO TRACKER CLI
        Type 'help' for available commands
-----------------------------------------------------------

portfolio>

--------

## Sample Working Example

Below is information that demonstrates the core workflow, adding assets, inspecting the portfolio, and running analytics.

### Add assets to the portfolio

portfolio> add AAPL tech stock 10
- Added 10 shares of AAPL (tech) (stock) at $195.27 = $1952.70 total

portfolio> add MSFT tech stock 5
- Added 5 shares of MSFT (tech) (stock) at $420.55 = $2102.75 total

portfolio> add VXUS international etf 50
- Added 50 shares of VXUS (international) (etf) at $58.12 = $2906.00 total

portfolio> add BND bonds bond 100
- Added 100 shares of BND (bonds) (bond) at $72.45 = $7245.00 total

### View holdings

portfolio> list

--- PORTFOLIO HOLDINGS (live prices from Yahoo Finance) ---
Ticker | Sector     | Asset Class  |   Qty | Avg Price   | Transaction Value | Current Value
--------------------------------------------------------------------------------------------------------------
AAPL   | tech       | stock        |    10 |     $195.27 |         $1,952.70 |      $1,960.40
MSFT   | tech       | stock        |     5 |     $420.55 |         $2,102.75 |      $2,115.30
VXUS   | international | etf       |    50 |      $58.12 |         $2,906.00 |      $2,920.50
BND    | bonds      | bond         |   100 |      $72.45 |         $7,245.00 |      $7,260.00

### Check portfolio value and return

portfolio> value
- Total Portfolio Value (live prices): $14,256.20

portfolio> return

--- PORTFOLIO RETURN ---
Transaction Value | Current Value |     P&L ($) | Return (%)
----------------------------------------------------------
    $14,206.45    |   $14,256.20  |     +$49.75 |    +0.35%

### Analyze portfolio weights

portfolio> weights sectors

--- SECTOR WEIGHTS ---
Total Portfolio Value: $14,256.20

Sector          |        Value |    Weight
------------------------------------------
bonds           |    $7,260.00 |   50.89%
international   |    $2,920.50 |   20.49%
tech            |    $4,075.70 |   28.59%

### Predict volatility with GARCH(1,1)

portfolio> predict volatility AAPL

--- GARCH(1,1) VOLATILITY FORECAST FOR AAPL ---
Fitted on 2y of data (502 obs, up to 2026-03-20)
Predicted daily vol (today): 1.4672%

### Detect market regimes (HMM) using machine learning

portfolio> regime AAPL 2y --states 3

--- REGIME DETECTION FOR AAPL (2y, 3 states) ---
Current regime (2026-03-20): Low Vol

Regime         |   Days | % Time | Avg Daily Return | Avg Daily Vol
--------------------------------------------------------------------
Low Vol        |    285 |  56.7% |           0.0912% |       1.0234%
Medium Vol     |    158 |  31.5% |          -0.0321% |       1.8567%
High Vol       |     59 |  11.8% |          -0.1845% |       3.1290%

### Run Monte Carlo simulation

portfolio> simulate

--- MONTE CARLO SIMULATION (15 Years, 100,000 Paths) ---
Initial Portfolio Value: $14,256.20

  Year |      1st %ile |      5th %ile |     25th %ile |        Median |     75th %ile |     95th %ile |     99th %ile
------------------------------------------------------------------------------------------------------------------------
     0 |       $14,256 |       $14,256 |       $14,256 |       $14,256 |       $14,256 |       $14,256 |       $14,256
     3 |        $9,812 |       $11,234 |       $14,105 |       $16,890 |       $20,256 |       $26,412 |       $31,567
     6 |        $8,456 |       $10,678 |       $15,890 |       $21,345 |       $28,901 |       $43,567 |       $58,234
     9 |        $7,890 |       $10,890 |       $18,456 |       $27,123 |       $40,567 |       $71,234 |      $103,456
    12 |        $7,345 |       $11,456 |       $21,890 |       $34,567 |       $56,789 |      $112,345 |      $178,901
    15 |        $7,012 |       $12,345 |       $26,234 |       $43,567 |       $78,901 |      $178,234 |      $312,456

After 15 years (100,000 simulated paths):
  Extreme worst (1st pct):  $        7,012.34
  Worst case   (5th pct):  $       12,345.67
  Median outcome (50th):   $       43,567.89
  Best case   (95th pct):  $      178,234.56
  Extreme best (99th pct): $      312,456.78

### View a price chart

portfolio> graph AAPL MSFT
- Graph displayed for: AAPL, MSFT

---> A matplotlib window will open showing the 1-year price history for each ticker.

### Exit

portfolio> quit

Goodbye!

--------

## Command Reference

| Command | Description |
|---|---|
| `add TICKER SECTOR CLASS QTY [PRICE]` | Add asset (price optional, defaults to live price) |
| `remove TICKER` | Remove asset from portfolio |
| `list` | Show all holdings with live prices |
| `value` | Total portfolio value |
| `return` | Portfolio P&L vs cost basis |
| `weights` | Weight of each asset |
| `weights sectors` | Weight of each sector |
| `weights classes` | Weight of each asset class |
| `weights sector NAME` | Drill into a specific sector |
| `weights class NAME` | Drill into a specific asset class |
| `history TICKER [PERIOD]` | Historical close prices (default: `1mo`) |
| `volume TICKER [PERIOD]` | Average and last trading volume |
| `graph TICKER [TICKER2 ...]` | 1-year price chart |
| `predict volatility TICKER [PERIOD]` | GARCH(1,1) daily volatility forecast |
| `historical volatility TICKER [PERIOD]` | GARCH(1,1) conditional volatility graph |
| `regime TICKER [PERIOD] [--states N]` | HMM regime detection (default: 3 states) |
| `simulate` | Monte Carlo simulation (15 yr, 100k paths) |
| `help` | Show all commands |
| `quit` / `exit` | Exit the program |

**Valid periods:** `1d` `5d` `1mo` `3mo` `6mo` `1y` `2y` `5y` `10y` `max`

---------

