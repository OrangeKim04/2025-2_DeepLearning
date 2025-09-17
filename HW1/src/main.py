from __future__ import annotations

from typing import Dict
import pandas as pd

from config import AppConfig
from data_fetchers import fetch_kr_price_history, fetch_us_price_history
from screener import screen_tickers, suggest_entry_exit
from report import build_report, build_reco_item_kr, build_reco_item_us
from news import fetch_market_headlines, summarize_news_openai
from kakao import KakaoClient
from stock_selector import select_diverse_stocks


def run_once() -> None:
	config = AppConfig.load()
	
	# 자동으로 종목 선별 (하드코딩된 종목 대신)
	print("🔍 시장에서 종목을 자동 선별 중...")
	kr_tickers, us_tickers = select_diverse_stocks(kr_limit=15, us_limit=15)
	
	if not kr_tickers and not us_tickers:
		print("❌ 종목 선별에 실패했습니다. 프로그램을 종료합니다.")
		return
	
	print(f"📊 한국 종목 {len(kr_tickers)}개, 미국 종목 {len(us_tickers)}개 선별 완료")
	
	# Fetch data
	kr_ticker_to_df: Dict[str, pd.DataFrame] = {t: fetch_kr_price_history(t) for t in kr_tickers}
	us_ticker_to_df: Dict[str, pd.DataFrame] = {t: fetch_us_price_history(t) for t in us_tickers}
	# Screen
	kr_selected = screen_tickers(kr_ticker_to_df, top_k=3)
	us_selected = screen_tickers(us_ticker_to_df, top_k=3)
	# Build reco lists
	kr_items = []
	for ticker, df, meta in kr_selected:
		entry, exit_ = suggest_entry_exit(meta)
		item = build_reco_item_kr(ticker, {**meta})
		item["entry"] = entry
		item["exit"] = exit_
		kr_items.append(item)
	us_items = []
	for ticker, df, meta in us_selected:
		entry, exit_ = suggest_entry_exit(meta)
		item = build_reco_item_us(ticker, {**meta})
		item["entry"] = entry
		item["exit"] = exit_
		us_items.append(item)
	# News summary
	headlines = fetch_market_headlines()
	news_summary = summarize_news_openai(headlines, config.openai_api_key)
	# Report
	report_text = build_report(config.user_name, kr_items[:3], us_items[:3], news_summary)
	# Send via Kakao (self-memo by default)
	client = KakaoClient(config)
	client.send_self_memo(report_text)
	print("Report sent.")


if __name__ == "__main__":
	run_once()
