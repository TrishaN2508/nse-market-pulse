# NSE Market Pulse

## What this is
A data pipeline and analysis project that downloads daily equity market data (bhavcopy and delivery position data) from the National Stock Exchange (NSE) of India, cleans it, stores it in a SQL database, and analyzes trading patterns — price, volume, and delivery percentage — across stocks over time.

## Key finding
High-volume trading days show significantly lower delivery percentages than typical days (42.74% average vs. 57.00% average, based on a 90th-percentile volume threshold across 48,000+ stock-day observations). A Welch's t-test confirms this difference is highly statistically significant (t = -53.57, p < 0.001), suggesting that unusually high trading activity is more often driven by short-term/speculative trading rather than genuine investment accumulation.

This is a correlational finding, not a causal one — both high volume and low delivery could be driven by a shared underlying factor (e.g., interest in low-priced, volatile stocks), rather than volume directly causing lower delivery.

## What it does so far
- Downloads NSE's daily equity bhavcopy (open/high/low/close price, volume, turnover, number of trades) directly from NSE's public archives
- Downloads NSE's daily delivery position data (delivery quantity and delivery percentage per stock)
- Handles NSE's session/cookie requirements needed to access data programmatically
- Proactively filters out known NSE trading holidays using NSE's own holiday-calendar API, with reactive error handling as a fallback for unexpected failures
- Cleans and filters both datasets down to regular equity (EQ series only), removing bonds, gold bonds, mutual funds, and other non-equity instruments mixed into the same files
- Handles real-world data messiness: whitespace in column names and values, non-numeric placeholder characters, inconsistent date formats and URL conventions across NSE's own endpoints
- Loads both cleaned datasets into a SQLite database as separate, joinable tables
- Joins price/volume data with delivery data by date and symbol
- Runs a statistical hypothesis test (Welch's t-test) comparing delivery percentage between high-volume and normal-volume trading days

## Tech stack
Python, pandas, requests, scipy, SQLite, SQL

## Project structure
nse-market-pulse/
├── fetch_one_day.py            # Single-day bhavcopy fetch (reference/debug)
├── fetch_range.py              # Multi-day bhavcopy fetch with holiday filtering
├── fetch_delivery_one_day.py   # Single-day delivery data fetch (reference/debug)
├── fetch_delivery_range.py     # Multi-day delivery data fetch with holiday filtering
├── analyze.py                  # SQL queries against the stored data
├── stat_test.py                # Statistical test: volume vs. delivery percentage
├── requirements.txt
├── .gitignore
└── README.md

## Setup

```bash
pip install -r requirements.txt
python fetch_range.py
python fetch_delivery_range.py
python analyze.py
python stat_test.py
```

This downloads the last 30 days of bhavcopy and delivery data (skipping weekends and NSE holidays automatically), stores it in `nse_market_pulse.db` (a local SQLite file, not committed to this repo), runs SQL analysis queries, and runs the statistical test comparing high-volume vs. normal-volume delivery percentages.

## Data sources
- **Bhavcopy**: `nsearchives.nseindia.com` (NSE's UDiFF format, adopted July 2024)
- **Delivery position data**: `archives.nseindia.com` (`sec_bhavdata_full` report)
- **Holiday calendar**: NSE's internal holiday-master API

Both require no API key, just a browser-like session with valid cookies. NSE has changed file formats/URLs before and may again — the download logic may need updates if that happens.

## Roadmap
- [ ] Add bulk/block deals data (large institutional trades)
- [ ] Add FII/DII daily trading activity data
- [ ] Add corporate announcements data, to explain price/volume/delivery spikes
- [ ] Build an interactive dashboard (Power BI / Tableau / Streamlit)

## Limitations
- Data reflects market-wide aggregate activity per stock per day, not per-broker or per-counterparty detail
- The volume/delivery relationship found here is correlational, not causal
- Analysis currently covers a ~1 month rolling window; longer historical analysis would strengthen the finding