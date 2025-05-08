# === FULL PROJECT: ETF Portfolio Tracker & Risk Analyzer ===
# Includes: Flask Backend, SQLite Storage, HTML + JavaScript Frontend

# === BACKEND: app.py ===

from flask import Flask, jsonify, request
import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# SQLite setup
conn = sqlite3.connect('etf_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS analytics (
        date TEXT,
        etf TEXT,
        sharpe REAL,
        drawdown REAL,
        volatility REAL
    )
''')
conn.commit()

# Helpers
def fetch_data(tickers, start="2023-01-01"):
    data = yf.download(tickers, start=start)["Adj Close"]
    return data

def compute_metrics(prices):
    daily_returns = prices.pct_change().dropna()
    mean_returns = daily_returns.mean()
    std_returns = daily_returns.std()
    sharpe_ratio = (mean_returns / std_returns) * np.sqrt(252)
    cumulative = (1 + daily_returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()
    volatility = std_returns * np.sqrt(252)
    return sharpe_ratio, max_drawdown, volatility

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    tickers = data.get("tickers", [])
    if not tickers:
        return jsonify({"error": "No tickers provided."}), 400
    prices = fetch_data(tickers)
    results = {}
    for ticker in tickers:
        if ticker not in prices.columns:
            continue
        ts = prices[ticker].dropna()
        if ts.empty:
            continue
        sharpe, drawdown, vol = compute_metrics(ts)
        results[ticker] = {
            "sharpe": round(sharpe, 3),
            "max_drawdown": round(drawdown, 3),
            "volatility": round(vol, 3)
        }
        cursor.execute("INSERT INTO analytics VALUES (?, ?, ?, ?, ?)",
                       (datetime.today().strftime('%Y-%m-%d'), ticker, sharpe, drawdown, vol))
        conn.commit()
    return jsonify(results)

@app.route('/history', methods=['GET'])
def history():
    cursor.execute("SELECT * FROM analytics")
    rows = cursor.fetchall()
    return jsonify([
        {"date": r[0], "etf": r[1], "sharpe": r[2], "drawdown": r[3], "volatility": r[4]} for r in rows
    ])

if __name__ == '__main__':
    app.run(debug=True)



# === HOW TO RUN ===
# 1. pip install flask yfinance pandas numpy flask-cors
# 2. Save app.py and run: python app.py
# 3. Save the HTML above as index.html and open in browser
# 4. Enter tickers like "SPY,QQQ" and click Analyze