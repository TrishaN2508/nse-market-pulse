# NSE Market Pulse

## What this is
A data pipeline and analysis project that downloads daily equity market data (bhavcopy) from the National Stock Exchange (NSE) of India, cleans it, stores it in a SQL database, and analyzes trading patterns — price, volume, and (eventually) delivery percentage — across stocks over time.

## Why I built it
I spent 2 years working in institutional brokerage back-office operations (TCS BaNCS Securities Processing), handling clearing and settlement using SQL and PL/SQL. This project applies that same domain background — market data, trade activity, settlement-adjacent concepts — to a self-directed data analytics pipeline, as part of my transition into a Data Analyst role. It's also my first real project combining SQL, Python, and pandas outside of production enterprise systems.

## What it does so far
- Downloads NSE's daily equity bhavcopy (open/high/low/close price, volume, turnover, number of trades) directly from NSE's public archives
- Handles NSE's session/cookie requirements needed to access the data programmatically
- Cleans and filters the raw data down to regular equity (EQ series only), removing bonds, gold bonds, mutual funds, and other non-equity instruments mixed into the same file
- Loads the cleaned data into a SQLite database
- Supports SQL querying for analysis (e.g., most actively traded stocks by volume)

## Tech stack
Python, pandas, requests, SQLite, SQL

## Project structure