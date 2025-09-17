from __future__ import annotations

import pandas as pd


def add_sma(df: pd.DataFrame, window: int, col: str = "Close") -> pd.DataFrame:
	out = df.copy()
	out[f"SMA_{window}"] = out[col].rolling(window=window, min_periods=window).mean()
	return out


def add_ema(df: pd.DataFrame, window: int, col: str = "Close") -> pd.DataFrame:
	out = df.copy()
	out[f"EMA_{window}"] = out[col].ewm(span=window, adjust=False).mean()
	return out


def add_rsi(df: pd.DataFrame, window: int = 14, col: str = "Close") -> pd.DataFrame:
	out = df.copy()
	delta = out[col].diff()
	gain = delta.clip(lower=0)
	loss = -delta.clip(upper=0)
	avg_gain = gain.rolling(window=window, min_periods=window).mean()
	avg_loss = loss.rolling(window=window, min_periods=window).mean()
	rs = avg_gain / (avg_loss.replace(0, 1e-9))
	out["RSI"] = 100 - (100 / (1 + rs))
	return out


def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, col: str = "Close") -> pd.DataFrame:
	out = df.copy()
	ema_fast = out[col].ewm(span=fast, adjust=False).mean()
	ema_slow = out[col].ewm(span=slow, adjust=False).mean()
	out["MACD"] = ema_fast - ema_slow
	out["MACD_SIGNAL"] = out["MACD"].ewm(span=signal, adjust=False).mean()
	out["MACD_HIST"] = out["MACD"] - out["MACD_SIGNAL"]
	return out


def add_bbands(df: pd.DataFrame, window: int = 20, num_std: float = 2.0, col: str = "Close") -> pd.DataFrame:
	out = df.copy()
	ma = out[col].rolling(window=window, min_periods=window).mean()
	std = out[col].rolling(window=window, min_periods=window).std()
	out["BB_MID"] = ma
	out["BB_UPPER"] = ma + num_std * std
	out["BB_LOWER"] = ma - num_std * std
	return out
