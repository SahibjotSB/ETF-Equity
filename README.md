# ETF Portfolio Tracker & Risk Analyzer

A full-stack application for tracking and analyzing ETF portfolios with risk metrics, performance visualization, and portfolio rebalancing capabilities.

![Demo](assets/demo.png)

## Features

- Portfolio performance tracking vs benchmark indices (SPY, QQQ, etc.)
- Risk metrics calculation (Sharpe Ratio, Max Drawdown, Volatility)
- Interactive performance charts with Plotly
- Asset correlation heatmap visualization
- Portfolio rebalancing calculator
- Local SQLite database for historical tracking

## Technology Stack

- **Backend**: Python, Flask, SQLite
- **Data Processing**: yfinance, NumPy, Pandas
- **Frontend**: HTML, CSS, JavaScript, Plotly.js
- **Data Visualization**: Plotly

## Installation and Setup

1. Clone the repository
2. Install required packages:
   ```
   pip install flask yfinance pandas numpy plotly
   ```
3. Initialize the database:
   ```
   sqlite3 portfolio.db < schema.sql
   ```
4. Run the application:
   ```
   python app.py
   ```
5. Navigate to `http://127.0.0.1:5000` in your web browser

## Usage Guide

### Portfolio Analysis

1. Enter ETF tickers and their weights in the portfolio section
2. Select a benchmark index and time period for comparison
3. Click "Analyze Portfolio" to view performance and risk metrics
4. The performance chart will show how your portfolio performs against the benchmark
5. The correlation heatmap will display relationships between your ETFs

### Portfolio Rebalancing

1. After analyzing your portfolio, enter the current dollar value of each holding
2. Click "Calculate Rebalancing" to see what trades are needed to rebalance to target weights
3. Green values indicate buys, red values indicate sells

## Key Metrics Explained

- **Sharpe Ratio**: Measures risk-adjusted return (higher is better)
- **Volatility**: Annualized standard deviation of returns (lower indicates stability)
- **Max Drawdown**: Largest percentage drop from peak to trough (smaller is better)
- **Annualized Return**: Expected yearly return based on historical performance

## Future Enhancements

- User accounts and saved portfolios
- Additional risk metrics (Sortino ratio, beta, etc.)
- Tax-efficient rebalancing suggestions
- Portfolio optimization tools
- Export functionality for reports