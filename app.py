from flask import Flask, request, jsonify, render_template
import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3
import json
from datetime import datetime, timedelta
import requests
from metrics_bridge import calculate_metrics_cpp  # C++ bridge function

TWELVE_DATA_API_KEY = '0efe8cf8f26243d199f215489ba1cb40'

def fetch_twelvedata_price(ticker, interval='1day', outputsize=100):
    url = f"https://api.twelvedata.com/time_series"
    params = {
        'symbol': ticker,
        'interval': interval,
        'apikey': TWELVE_DATA_API_KEY,
        'outputsize': outputsize,
        'format': 'JSON'
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'values' not in data:
        print(f"Error fetching {ticker}: {data.get('message', 'Unknown error')}")
        return None

    df = pd.DataFrame(data['values'])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    df = df.sort_index()
    df[ticker] = df['close'].astype(float)
    return df[[ticker]]

app = Flask(__name__)

def calculate_metrics(portfolio_data, weights):
    # Calculate daily returns
    returns = portfolio_data.pct_change().dropna()

    # Calculate portfolio returns
    portfolio_returns = (returns * weights).sum(axis=1)

    # ✅ Use C++ for risk metrics calculation
    return calculate_metrics_cpp(portfolio_returns.values)


def get_correlation_matrix(portfolio_data):
    return portfolio_data.pct_change().dropna().corr().round(2).to_dict()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/portfolio', methods=['POST'])
def analyze_portfolio():
    data = request.json
    tickers = data['tickers']
    weights = np.array(data['weights'])
    benchmark = data.get('benchmark', 'SPY')
    period = data.get('period', '1y')
    
    # Normalize weights
    weights = weights / np.sum(weights)
    
    # Get historical data with error handling and rate limit management
    end_date = datetime.now()
    tickers_with_benchmark = tickers + [benchmark] if benchmark not in tickers else tickers
    
    # Add delay and retry logic for Yahoo Finance API
    max_retries = 3
    retry_delay = 2  # seconds
    
    portfolio_data = pd.DataFrame()

    for ticker in tickers_with_benchmark:
        try:
            df = yf.download(ticker, period=period, auto_adjust=False, progress=False, threads=False)
            if 'Adj Close' in df and not df.empty:
                portfolio_data[ticker] = df['Adj Close']
            else:
                raise ValueError("No data or 'Adj Close' missing")
        except Exception as e:
            print(f"Yahoo Finance failed for {ticker}: {e}")
            # Fallback to Twelve Data
            fallback_df = fetch_twelvedata_price(ticker, interval='1day', outputsize=100)
            if fallback_df is not None:
                portfolio_data = pd.concat([portfolio_data, fallback_df], axis=1)
            import time
            time.sleep(1.5)  # Avoid rate limit for Twelve Data
        
        # Check if we have data
        if portfolio_data.empty:
            return jsonify({
                'error': 'Failed to retrieve data from Yahoo Finance. Please try again later.'
            }), 429  # HTTP 429 Too Many Requests
    
    # Calculate metrics
    metrics = calculate_metrics(portfolio_data[tickers], weights)
    
    # Calculate correlation matrix
    correlation = get_correlation_matrix(portfolio_data[tickers])
    
    # Prepare time series for charting
    portfolio_values = (portfolio_data[tickers] * weights).sum(axis=1)
    benchmark_values = portfolio_data[benchmark]
    
    # Normalize to start at 100
    portfolio_values = 100 * (portfolio_values / portfolio_values.iloc[0])
    benchmark_values = 100 * (benchmark_values / benchmark_values.iloc[0])
    
    # Save to database
    try:
        conn = sqlite3.connect('portfolio.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS portfolio_history
                    (date TEXT, portfolio_value REAL, benchmark_value REAL)''')
        
        # Store today's values
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute("INSERT INTO portfolio_history VALUES (?, ?, ?)",
                 (today, portfolio_values.iloc[-1], benchmark_values.iloc[-1]))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
    
    # Format for Plotly
    dates = portfolio_values.index.strftime('%Y-%m-%d').tolist()
    
    return jsonify({
        'metrics': metrics,
        'correlation': correlation,
        'timeseries': {
            'dates': dates,
            'portfolio': portfolio_values.round(2).tolist(),
            'benchmark': benchmark_values.round(2).tolist(),
            'benchmark_ticker': benchmark
        }
    })

@app.route('/api/rebalance', methods=['POST'])
def rebalance_portfolio():
    data = request.json
    current_tickers = data['tickers']
    target_weights = np.array(data['weights'])
    current_values = np.array(data['values'])
    
    # Calculate current weights
    total_value = np.sum(current_values)
    current_weights = current_values / total_value
    
    # Calculate trades needed to rebalance
    target_values = total_value * target_weights
    trades_needed = target_values - current_values
    
    return jsonify({
        'target_values': target_values.tolist(),
        'trades_needed': trades_needed.tolist(),
        'rebalanced_weights': target_weights.tolist()
    })

if __name__ == '__main__':
    app.run(debug=True)