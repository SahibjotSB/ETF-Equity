"""
Portfolio Risk Metrics Bridge Module
Author: Sahibjot Singh Bhoday
Description: This module creates a bridge between Python and C++ for efficient calculation
of portfolio risk metrics. The C++ implementation provides better performance for
computationally intensive calculations.
"""

from ctypes import cdll, POINTER, c_double, c_int
import numpy as np
import os

# Load the C++ DLL - Using relative path for portability
lib_path = os.path.abspath(os.path.join("metrics", "risk_metrics.dll"))
lib = cdll.LoadLibrary(lib_path)

# Configure C++ function interfaces
# Each function needs proper type hints for ctypes to handle data conversion

# Sharpe Ratio calculation setup
sharpe_fn = lib.calculate_sharpe
sharpe_fn.argtypes = [POINTER(c_double), c_int, c_double]  # Array of returns, size, risk-free rate
sharpe_fn.restype = c_double

# Volatility calculation setup
volatility_fn = lib.calculate_volatility
volatility_fn.argtypes = [POINTER(c_double), c_int]  # Array of returns, size
volatility_fn.restype = c_double

# Maximum Drawdown calculation setup
drawdown_fn = lib.calculate_max_drawdown
drawdown_fn.argtypes = [POINTER(c_double), c_int]  # Array of returns, size
drawdown_fn.restype = c_double

def calculate_metrics_cpp(portfolio_returns, risk_free=0.03/252):
    """
    Calculate key portfolio risk metrics using C++ implementations
    
    Args:
        portfolio_returns (list): Daily returns of the portfolio
        risk_free (float): Daily risk-free rate (default: 3% annual rate converted to daily)
    
    Returns:
        dict: Dictionary containing Sharpe ratio, volatility, max drawdown, and annualized returns
    """
    # Convert Python list to C++ compatible array
    arr = (c_double * len(portfolio_returns))(*portfolio_returns)
    size = len(portfolio_returns)

    # Calculate metrics using C++ functions
    sharpe = sharpe_fn(arr, size, risk_free)
    volatility = volatility_fn(arr, size)
    max_drawdown = drawdown_fn(arr, size)
    annual_return = np.mean(portfolio_returns) * 252 * 100  # Annualize daily returns

    # Round results for cleaner display
    return {
        "sharpe_ratio": round(sharpe, 2),
        "volatility": round(volatility, 2),
        "max_drawdown": round(max_drawdown, 2),
        "returns": round(annual_return, 2)
    }
