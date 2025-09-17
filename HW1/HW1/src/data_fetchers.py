from __future__ import annotations

import datetime as dt
from typing import Tuple

import FinanceDataReader as fdr
import pandas as pd
import yfinance as yf


def fetch_kr_price_history(ticker: str, period_days: int = 260) -> pd.DataFrame:
	"""Fetch KRX daily price history using FinanceDataReader.

	Returns columns: [Open, High, Low, Close, Volume]
	"""
	end = dt.date.today()
	start = end - dt.timedelta(days=period_days * 2)
	df = fdr.DataReader(ticker, start, end)
	if df is None or df.empty:
		return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
	df = df.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"})
	df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
	return df


def fetch_us_price_history(ticker: str, period_days: int = 260) -> pd.DataFrame:
	"""Fetch US daily price history using yfinance."""
	period = f"{period_days}d"
	yt = yf.Ticker(ticker)
	df = yt.history(period=period, interval="1d", auto_adjust=False)
	if df is None or df.empty:
		return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
	df = df.rename(columns={"Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"})
	df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
	return df


def get_kr_ticker_name(ticker: str) -> str:
	try:
		info = fdr.StockListing("KRX")
		row = info[info["Code"] == ticker]
		if not row.empty:
			return str(row.iloc[0]["Name"])
	except Exception:
		pass
	return ticker


def get_us_ticker_name(ticker: str) -> str:
	try:
		info = yf.Ticker(ticker)
		name = info.info.get("shortName") if hasattr(info, "info") else None
		return name or ticker
	except Exception:
		return ticker


def compute_52w_stats(df: pd.DataFrame) -> Tuple[float, float]:
	"""Return (52-week low, 52-week high) from last ~252 trading days."""
	window = min(len(df), 252)
	if window == 0:
		return (float("nan"), float("nan"))
	last = df.tail(window)
	return float(last["Low"].min()), float(last["High"].max())
