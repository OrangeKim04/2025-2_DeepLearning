from __future__ import annotations

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import pytz

from config import AppConfig
from data_fetchers import fetch_kr_price_history, fetch_us_price_history
from screener import screen_tickers
from report import build_report, build_reco_item_kr, build_reco_item_us
from news import fetch_market_headlines, summarize_news_openai
from stock_selector import select_diverse_stocks


class DataManager:
    """웹과 카카오톡이 공유하는 데이터 관리자"""
    
    def __init__(self):
        self.cached_data = None
        self.last_update = None
        self.cache_duration = timedelta(minutes=5)  # 5분 캐시
    
    def is_expired(self) -> bool:
        """캐시가 만료되었는지 확인"""
        if not self.last_update:
            return True
        return datetime.now(pytz.timezone('Asia/Seoul')) - self.last_update > self.cache_duration
    
    def get_fresh_data(self) -> Dict[str, Any]:
        """최신 데이터를 가져오기 (캐시 사용)"""
        if not self.cached_data or self.is_expired():
            print("🔄 새로운 데이터 수집 중...")
            self.cached_data = self._collect_data()
            self.last_update = datetime.now(pytz.timezone('Asia/Seoul'))
            print("✅ 데이터 수집 완료")
        else:
            print("📋 캐시된 데이터 사용")
        
        return self.cached_data
    
    def _collect_data(self) -> Dict[str, Any]:
        """실제 데이터 수집 로직"""
        config = AppConfig.load()
        
        # 자동으로 종목 선별
        print("🔍 시장에서 종목을 자동 선별 중...")
        kr_tickers, us_tickers = select_diverse_stocks(kr_limit=15, us_limit=15)
        
        if not kr_tickers and not us_tickers:
            print("❌ 종목 선별에 실패했습니다.")
            return {
                'last_update': datetime.now(pytz.timezone('Asia/Seoul')),
                'kr_items': [],
                'us_items': [],
                'news_summary': "뉴스 수집 실패",
                'report_text': "데이터 수집에 실패했습니다."
            }
        
        print(f"📊 한국 종목 {len(kr_tickers)}개, 미국 종목 {len(us_tickers)}개 선별 완료")
        
        # 데이터 수집
        kr_ticker_to_df = {t: fetch_kr_price_history(t) for t in kr_tickers}
        us_ticker_to_df = {t: fetch_us_price_history(t) for t in us_tickers}
        
        # 스크리닝
        kr_selected = screen_tickers(kr_ticker_to_df, top_k=3)
        us_selected = screen_tickers(us_ticker_to_df, top_k=3)
        
        # 추천 아이템 생성
        kr_items = []
        for ticker, df, meta in kr_selected:
            item = build_reco_item_kr(ticker, {**meta})
            kr_items.append(item)
        
        us_items = []
        for ticker, df, meta in us_selected:
            item = build_reco_item_us(ticker, {**meta})
            us_items.append(item)
        
        # 뉴스 요약
        headlines = fetch_market_headlines()
        news_summary = summarize_news_openai(headlines, config.openai_api_key)
        
        # 리포트 생성
        report_text = build_report(config.user_name, kr_items[:3], us_items[:3], news_summary)
        
        return {
            'last_update': datetime.now(pytz.timezone('Asia/Seoul')),
            'kr_items': kr_items[:3],
            'us_items': us_items[:3],
            'news_summary': news_summary,
            'report_text': report_text
        }
    
    def force_refresh(self) -> Dict[str, Any]:
        """강제로 데이터 새로고침"""
        print("🔄 강제 데이터 새로고침...")
        self.cached_data = None
        self.last_update = None
        return self.get_fresh_data()


# 전역 인스턴스
data_manager = DataManager()
