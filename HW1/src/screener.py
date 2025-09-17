from __future__ import annotations

from typing import List, Dict, Any, Tuple
import pandas as pd

from indicators import add_sma, add_rsi, add_macd, add_bbands
from data_fetchers import compute_52w_stats


def enrich_indicators(df: pd.DataFrame) -> pd.DataFrame:
	out = df.copy()
	out = add_sma(out, 5)
	out = add_sma(out, 20)
	out = add_sma(out, 60)
	out = add_rsi(out, 14)
	out = add_macd(out)
	out = add_bbands(out)
	return out


def score_row(row: pd.Series) -> float:
	score = 0.0
	# Trend: short MA above long MA
	if row.get("SMA_5") and row.get("SMA_20") and row.get("SMA_60"):
		if row["SMA_5"] > row["SMA_20"]:
			score += 1.0
		if row["SMA_20"] > row["SMA_60"]:
			score += 0.5
	# RSI moderate (40-65) preferred for swing entries
	rsi = row.get("RSI")
	if pd.notna(rsi):
		if 40 <= rsi <= 65:
			score += 1.0
		elif rsi < 30:
			score += 0.3  # potential rebound
	# MACD histogram positive or crossing up
	macd = row.get("MACD")
	signal = row.get("MACD_SIGNAL")
	if pd.notna(macd) and pd.notna(signal):
		if macd > signal:
			score += 0.7
	# Volume spike vs 20d avg
	vol = row.get("Volume")
	vol_avg20 = row.get("VOL_AVG20")
	if pd.notna(vol) and pd.notna(vol_avg20) and vol_avg20 > 0:
		if vol / vol_avg20 >= 1.5:
			score += 0.7
	return score


def screen_tickers(ticker_to_df: Dict[str, pd.DataFrame], top_k: int = 3) -> List[Tuple[str, pd.DataFrame, Dict[str, Any]]]:
	candidates: List[Tuple[str, pd.DataFrame, Dict[str, Any]]] = []
	for ticker, df in ticker_to_df.items():
		if df is None or df.empty:
			continue
		df2 = df.copy()
		df2["VOL_AVG20"] = df2["Volume"].rolling(window=20, min_periods=20).mean()
		df2 = enrich_indicators(df2)
		last = df2.iloc[-1]
		score = score_row(last)
		low_52w, high_52w = compute_52w_stats(df2)
		meta = {
			"score": score,
			"close": float(last["Close"]),
			"rsi": float(last.get("RSI", float("nan"))),
			"macd": float(last.get("MACD", float("nan"))),
			"macd_signal": float(last.get("MACD_SIGNAL", float("nan"))),
			"bb_lower": float(last.get("BB_LOWER", float("nan"))),
			"bb_upper": float(last.get("BB_UPPER", float("nan"))),
			"sma5": float(last.get("SMA_5", float("nan"))),
			"sma20": float(last.get("SMA_20", float("nan"))),
			"sma60": float(last.get("SMA_60", float("nan"))),
			"vol": float(last.get("Volume", float("nan"))),
			"vol_avg20": float(last.get("VOL_AVG20", float("nan"))),
			"low_52w": low_52w,
			"high_52w": high_52w,
		}
		candidates.append((ticker, df2, meta))
	# sort by score, then volume spike
	candidates.sort(key=lambda x: (x[2]["score"], x[2]["vol"] / (x[2]["vol_avg20"] or 1)), reverse=True)
	return candidates[:top_k]


def suggest_entry_exit(meta: Dict[str, Any]) -> Tuple[str, str]:
	entry = "단기 이동평균선이 장기 이동평균선을 돌파하는 시점"
	if meta.get("macd") and meta.get("macd_signal") and meta["macd"] > meta["macd_signal"]:
		entry = "MACD가 시그널을 상향 돌파할 때"
	exit_ = "RSI 지수가 70 이상으로 과매수 구간에 진입했을 때"
	if meta.get("rsi") and meta["rsi"] < 30:
		exit_ = "RSI가 30을 하회 후 되돌림 시 분할 매도"
	return entry, exit_
