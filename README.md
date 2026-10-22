# NSE Market Pulse

## What this is
A data pipeline and analysis project that downloads daily equity market data from the National Stock Exchange (NSE) of India — price/volume, delivery percentage, bulk deals, FII/DII institutional trading activity, corporate announcements, and financial results filings — cleans it, stores it in a SQL database, and analyzes trading patterns across stocks over a full year.

## Key finding
High-volume trading days show significantly lower delivery percentages than typical days (43.97% average vs. 56.73% average, based on a 90th-percentile volume threshold across 572,000+ stock-day observations spanning a full year, July 2025–July 2026). A Welch's t-test confirms this difference is highly statistically significant (t = -163.83, p < 0.001), suggesting that unusually high trading activity is more often driven by short-term/speculative trading rather than genuine investment accumulation.

This pattern is remarkably consistent with the project's original 21-day sample (14.26 percentage point gap vs. 12.77 today), and dramatically more statistically confident at full scale — indicating a stable, persistent market pattern rather than a short-term artifact.

This is a correlational finding, not a causal one — both high volume and low delivery could be driven by a shared underlying factor (e.g., interest in low-priced, volatile stocks), rather than volume directly causing lower delivery.

## Conclusion
All 10 of the year's single highest-volume trading days belong to one stock — Vodafone Idea (IDEA) — spread across six different months, each showing delivery percentages between 11% and 24%. This means the vast majority of shares traded on IDEA's biggest-volume days were bought and sold again within the same session rather than held, and the pattern recurred consistently regardless of month or broader market conditions.

Corporate announcement data (179,000+ filings over the year) adds context: the most common categories are routine disclosures — investor/analyst meeting updates (25,105), newspaper publication copies (17,782), general updates (17,634) — rather than major corporate actions, suggesting day-to-day announcement volume doesn't explain sustained speculative activity in specific stocks.

Together, the year-long statistical result and the concentrated, repeated pattern in a single identifiable stock make a compelling case that delivery percentage is a genuinely useful signal for distinguishing speculative trading from real investment accumulation in Indian equities — though, as noted above, this remains a correlational observation rather than a proven causal mechanism.

## Dashboard
![NSE Market Pulse Dashboard](screenshots/dashboard.png)

An interactive Power BI dashboard (`nse_market_pulse_dashboard.pbix`) built on top of the SQLite database, featuring:
- KPI cards summarizing stocks tracked, average delivery %, and bulk deals recorded
- A scatter plot visualizing the core volume-vs-delivery-% finding
- Top 10 stocks by average trading volume
- FII/DII net flow trend over time

Data is exported from SQLite to CSV via `export_for_powerbi.py`; the dashboard is refreshed manually by re-running the export and clicking Refresh in Power BI Desktop.

## What it does so far
- Downloads NSE's daily equity bhavcopy (open/high/low/close price, volume, turnover, number of trades)
- Downloads NSE's daily delivery position data (delivery quantity and delivery percentage per stock)
- Downloads NSE's bulk deals data (large institutional trades, per stock per day)
- Downloads NSE's FII/DII daily institutional trading activity (foreign vs. domestic institutional buy/sell values)
- Downloads NSE's corporate announcements (full year), covering board meetings, credit ratings, resignations, and 130+ other filing categories
- Downloads NSE's corporate financial results filing index (company, quarter, filing type, audited status) using a probe-then-fetch pattern — first querying the exact record count, then requesting precisely that many in a single request, to avoid data drift from NSE's live-updating feed shifting mid-pagination
- Handles NSE's session/cookie requirements needed to access data programmatically, including a `Referer` header for endpoints that require it
- Proactively filters out known NSE trading holidays using NSE's own holiday-calendar API, with reactive error handling as a fallback for unexpected failures
- Cleans and filters datasets down to regular equity (EQ series only), removing bonds, gold bonds, mutual funds, and other non-equity instruments mixed into the same files
- Handles real-world data messiness: whitespace in column names and values, non-numeric placeholder characters, inconsistent date formats and URL conventions across NSE's own endpoints
- Includes a deduplication safeguard for delivery data, after discovering NSE occasionally serves duplicate records for a small number of dates during large historical fetches
- Loads all cleaned datasets into a SQLite database as separate, joinable tables
- Joins price/volume data with delivery data by date and symbol
- Runs a statistical hypothesis test (Welch's t-test) comparing delivery percentage between high-volume and normal-volume trading days
- Implements a same-day upsert safeguard for FII/DII data (which NSE only ever publishes as a same-day snapshot, no historical range available), so the pipeline can be run multiple times a day without creating duplicates, while still capturing revisions to provisional figures
- Visualizes all findings in an interactive Power BI dashboard, built on a CSV export of the SQLite data

## Tech stack
Python, pandas, requests, scipy, SQLite, SQL

## Project structure
```
nse-market-pulse/
├── fetch_one_day.py              # Single-day bhavcopy fetch (reference/debug)
├── fetch_range.py                # Multi-day bhavcopy fetch with holiday filtering
├── fetch_delivery_one_day.py     # Single-day delivery data fetch (reference/debug)
├── fetch_delivery_range.py       # Multi-day delivery data fetch with holiday filtering
├── fetch_bulk_deals_range.py     # Multi-day bulk deals fetch (per-day looping; endpoint ignores date-range params)
├── fetch_fii_dii.py              # Daily FII/DII snapshot with same-day upsert safeguard
├── fetch_fii_dii_cloud.py        # Cloud-safe version of the FII/DII fetch, used by the GitHub Actions workflow
├── fetch_announcements_range.py  # Full-year corporate announcements fetch
├── fetch_financial_results_one_day.py   # Financial results filing index exploration/reference
├── fetch_financial_results_range.py     # Full-year financial results filing index (probe-then-fetch)
├── fetch_shareholding_pattern_one_day.py  # Shareholding pattern exploration (deferred, see Roadmap)
├── dedupe_delivery.py            # One-time cleanup script that removed duplicate delivery records
├── export_for_powerbi.py         # Exports SQLite tables to CSV for Power BI
├── nse_market_pulse_dashboard.pbix  # Power BI dashboard file
├── screenshots/                  # Dashboard screenshot for this README
├── data/                         # FII/DII history CSV, updated by the GitHub Actions workflow
├── .github/workflows/            # GitHub Actions workflow definitions
├── analyze.py                    # SQL queries against the stored data
├── stat_test.py                  # Statistical test: volume vs. delivery percentage
├── requirements.txt
├── .gitignore
└── README.md
```
## Setup

```bash
pip install -r requirements.txt
python fetch_range.py
python fetch_delivery_range.py
python fetch_bulk_deals_range.py
python fetch_announcements_range.py
python fetch_financial_results_range.py
python fetch_fii_dii.py
python analyze.py
python stat_test.py
python export_for_powerbi.py
```

All fetch scripts default to a 365-day lookback (skipping weekends and NSE holidays automatically), except `fetch_fii_dii.py`, which fetches only the current day's data and is meant to be run daily to build up history over time — NSE doesn't expose a historical range for this dataset. All data is stored in `nse_market_pulse.db` (a local SQLite file, not committed to this repo).

## Automation
`fetch_fii_dii.py` is scheduled to run automatically on weekdays via Windows Task Scheduler, since NSE only exposes same-day FII/DII figures with no historical backfill available. The task is configured to catch up if the scheduled run is missed (e.g., laptop was off), and the script's built-in upsert logic ensures re-running it on the same day safely overwrites that day's data rather than creating duplicates — useful since NSE's figures are provisional and may be revised intraday.

## Cloud automation
`fetch_fii_dii_cloud.py` runs automatically via GitHub Actions (`.github/workflows/fii_dii_daily.yml`) on weekdays at 8 PM IST, independent of any local machine. This was built after discovering that the local Windows Task Scheduler approach could miss a full trading day's data if the laptop wasn't powered on at all during that day — since NSE's FII/DII endpoint has no historical backfill, a missed day is permanently unrecoverable. Moving this specific pipeline to GitHub Actions removes that single point of failure. Results are committed directly to `data/fii_dii_history.csv` in this repo. The workflow can also be triggered manually from the Actions tab.

## Data sources
- **Bhavcopy**: `nsearchives.nseindia.com` (NSE's UDiFF format, adopted July 2024)
- **Delivery position data**: `archives.nseindia.com` (`sec_bhavdata_full` report)
- **Bulk deals**: `nseindia.com/api/historicalOR/bulk-block-short-deals` (internal API, discovered via browser DevTools network inspection; the API's `to` date parameter is not honored, so data must be fetched one day at a time)
- **FII/DII activity**: `nseindia.com/api/fiidiiTradeReact` (internal API; same-day snapshot only, no historical range; data is explicitly provisional per NSE, subject to revision via NSDL's custodial confirmation process)
- **Corporate announcements**: `nseindia.com/api/corporate-announcements` (supports genuine date-range filtering, verified at up to a full year)
- **Financial results filings**: `nseindia.com/api/integrated-filing-results` (NSE's current Integrated Filing system, replacing an older `corporates-financial-results` endpoint found to be stale/deprecated; provides filing metadata only — actual revenue/profit/EPS figures are embedded in linked XBRL/iXBRL documents, which are out of scope for this project). This endpoint paginates a live-updating feed, which was found to cause duplicate and skipped records under simple multi-page pagination; fixed with a probe-then-fetch pattern that queries the exact count first, then retrieves everything in a single request.
- **Holiday calendar**: NSE's internal holiday-master API

All sources require no API key, just a browser-like session with valid cookies (and in some cases a valid `Referer` header). NSE's bulk deals endpoint additionally sits behind bot-detection on at least one alternate URL pattern that was tested and abandoned in favor of the working endpoint above. NSE has changed file formats/URLs before and may again — the download logic may need updates if that happens.

## Roadmap
- [ ] Extend statistical analysis to bulk deals and FII/DII (e.g., does bulk deal activity coincide with delivery spikes?)
- [ ] Deploy dashboard as a live shareable link (Streamlit or Power BI Service)
- [ ] Migrate from SQLite to MySQL for a proper client-server database setup
- [ ] Shareholding pattern data — investigated (`nseindia.com/api/corporate-share-holdings-master`); real promoter/public % data confirmed available, but the dataset is fundamentally quarterly (not daily) and would need different date-handling logic than the rest of this project's daily time-series tables. Deferred as a lower-priority addition.

## Limitations
- Data reflects market-wide aggregate activity per stock per day, not per-broker or per-counterparty detail
- The volume/delivery relationship found here is correlational, not causal
- FII/DII data is provisional as published by NSE and may not reflect final, custodial-confirmed figures
- Bulk deals history in this project only extends as far back as the pipeline has actually been run manually — this source cannot be backfilled from NSE's public site
- FII/DII data is collected automatically via GitHub Actions (see Cloud automation above), reducing but not eliminating gap risk — a gap would still occur if GitHub Actions itself experienced an outage during a trading day, though this is far less likely than a personal laptop being off
- Financial results data covers filing events only (who filed, when, for what quarter) — not the underlying revenue/profit/EPS figures, which would require XBRL parsing (a separate, substantial undertaking)
- A small number of dates (3 out of 244 trading days) in the delivery dataset returned duplicate records during the full-year fetch; these were identified via row-count validation and removed via deduplication before analysis