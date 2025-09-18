from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime
import pytz
from typing import Dict, List, Any
import pandas as pd

from config import AppConfig
from data_fetchers import fetch_kr_price_history, fetch_us_price_history
from screener import screen_tickers, suggest_entry_exit
from report import build_report, build_reco_item_kr, build_reco_item_us
from news import fetch_market_headlines, summarize_news_openai
from stock_selector import select_diverse_stocks

app = Flask(__name__)

# 전역 변수로 캐시된 데이터 저장
cached_data = {
    'last_update': None,
    'kr_items': [],
    'us_items': [],
    'news_summary': '',
    'report_text': ''
}

def update_stock_data():
    """주식 데이터를 업데이트하는 함수"""
    global cached_data
    
    try:
        config = AppConfig.load()
        
        # 자동으로 종목 선별
        print("🔍 시장에서 종목을 자동 선별 중...")
        kr_tickers, us_tickers = select_diverse_stocks(kr_limit=15, us_limit=15)
        
        if not kr_tickers and not us_tickers:
            print("❌ 종목 선별에 실패했습니다.")
            return False
        
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
        
        # 캐시 업데이트
        cached_data = {
            'last_update': datetime.now(pytz.timezone('Asia/Seoul')),
            'kr_items': kr_items[:3],
            'us_items': us_items[:3],
            'news_summary': news_summary,
            'report_text': report_text
        }
        
        return True
        
    except Exception as e:
        print(f"데이터 업데이트 실패: {e}")
        return False

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html', 
                         last_update=cached_data.get('last_update'),
                         has_data=bool(cached_data.get('kr_items')))

@app.route('/api/update')
def api_update():
    """데이터 업데이트 API"""
    success = update_stock_data()
    return jsonify({
        'success': success,
        'last_update': cached_data.get('last_update').isoformat() if cached_data.get('last_update') else None
    })

@app.route('/api/data')
def api_data():
    """주식 데이터 API"""
    return jsonify({
        'last_update': cached_data.get('last_update').isoformat() if cached_data.get('last_update') else None,
        'kr_items': cached_data.get('kr_items', []),
        'us_items': cached_data.get('us_items', []),
        'news_summary': cached_data.get('news_summary', ''),
        'report_text': cached_data.get('report_text', '')
    })

@app.route('/api/report')
def api_report():
    """리포트 텍스트 API"""
    return jsonify({
        'report_text': cached_data.get('report_text', ''),
        'last_update': cached_data.get('last_update').isoformat() if cached_data.get('last_update') else None
    })

if __name__ == '__main__':
    # 서버 시작 시 초기 데이터 로드
    print("🚀 웹 서버 시작 중...")
    update_stock_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
