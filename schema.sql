/*
ETF Portfolio Tracker Database Schema
Author: Sahibjot Singh Bhoday
*/

-- Tracks daily portfolio and benchmark values (base 100)
CREATE TABLE IF NOT EXISTS portfolio_history (
    date TEXT PRIMARY KEY,
    portfolio_value REAL,
    benchmark_value REAL
);

-- Core ETF information lookup table
CREATE TABLE IF NOT EXISTS etfs (
    ticker TEXT PRIMARY KEY,
    name TEXT,
    category TEXT,
    expense_ratio REAL
);

-- User portfolio metadata
CREATE TABLE IF NOT EXISTS portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    created_date TEXT,
    last_updated TEXT
);

-- Portfolio ETF allocations with weights as decimals
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    portfolio_id INTEGER,
    ticker TEXT,
    weight REAL,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
    FOREIGN KEY (ticker) REFERENCES etfs(ticker),
    PRIMARY KEY (portfolio_id, ticker)
);
