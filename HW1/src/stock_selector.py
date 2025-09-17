from __future__ import annotations

import pandas as pd
from typing import List, Dict, Any
import FinanceDataReader as fdr
import yfinance as yf
import requests
from bs4 import BeautifulSoup


def get_sp500_tickers() -> List[str]:
    """S&P 500 종목 리스트를 웹에서 동적으로 가져오기"""
    try:
        # Wikipedia에서 S&P 500 종목 리스트 가져오기
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        response = requests.get(url)
        response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'constituents'})
        
        if not table:
            raise ValueError("S&P 500 테이블을 찾을 수 없습니다")
        
        tickers = []
        rows = table.find_all('tr')[1:]  # 헤더 제외
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 0:
                ticker = cells[0].text.strip()
                # 특수 문자 제거 및 정리
                ticker = ticker.replace('.', '-')  # BRK.B -> BRK-B
                tickers.append(ticker)
        
        return tickers
        
    except Exception as e:
        print(f"S&P 500 종목 리스트 수집 실패: {e}")
        # 폴백: 기본적인 대형주 리스트
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
            'UNH', 'JNJ', 'V', 'PG', 'JPM', 'HD', 'MA', 'DIS', 'PYPL', 'ADBE',
            'NFLX', 'CRM', 'INTC', 'AMD', 'ORCL', 'CSCO', 'TMO', 'ABT', 'PEP',
            'COST', 'AVGO', 'WMT', 'DHR', 'ACN', 'VZ', 'NKE', 'TXN', 'QCOM',
            'CMCSA', 'NEE', 'UNP', 'HON', 'IBM', 'LMT', 'SPGI', 'INTU', 'AMAT'
        ]


def get_kr_top_stocks(limit: int = 20) -> List[str]:
    """한국 상위 종목들을 자동으로 수집"""
    try:
        # KRX 상장사 목록 가져오기
        stock_list = fdr.StockListing('KRX')
        
        # 시가총액 상위 종목 필터링 (상장주식수 * 종가 기준)
        stock_list['market_cap'] = stock_list['Marcap']  # 시가총액
        stock_list = stock_list[stock_list['market_cap'] > 0]  # 유효한 데이터만
        stock_list = stock_list.sort_values('market_cap', ascending=False)
        
        # 상위 종목 코드 반환
        top_stocks = stock_list.head(limit)['Code'].tolist()
        return [str(code).zfill(6) for code in top_stocks]  # 6자리 코드로 변환
        
    except Exception as e:
        print(f"한국 종목 수집 실패: {e}")
        # 실패 시 빈 리스트 반환
        return []


def get_us_top_stocks(limit: int = 20) -> List[str]:
    """미국 상위 종목들을 자동으로 수집"""
    try:
        # S&P 500 종목 리스트를 동적으로 가져오기
        sp500_tickers = get_sp500_tickers()
        
        # 실제로 거래되는 종목인지 확인하고 시가총액 기준으로 정렬
        valid_tickers = []
        ticker_data = []
        
        for ticker in sp500_tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                if info and 'regularMarketPrice' in info and 'marketCap' in info:
                    market_cap = info.get('marketCap', 0)
                    if market_cap > 0:
                        ticker_data.append((ticker, market_cap))
            except:
                continue
        
        # 시가총액 기준으로 정렬
        ticker_data.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 종목들 반환
        valid_tickers = [ticker for ticker, _ in ticker_data[:limit]]
        return valid_tickers
        
    except Exception as e:
        print(f"미국 종목 수집 실패: {e}")
        # 실패 시 빈 리스트 반환
        return []


def get_sector_leaders() -> Dict[str, List[str]]:
    """섹터별 대표 종목들 수집 (동적 수집)"""
    # 향후 섹터별 종목을 동적으로 수집하는 기능으로 확장 가능
    return {}


def select_diverse_stocks(kr_limit: int = 15, us_limit: int = 15) -> tuple[List[str], List[str]]:
    """다양한 섹터에서 종목을 선별"""
    try:
        # 한국: 시가총액 상위 + 섹터별 대표주
        kr_stocks = get_kr_top_stocks(kr_limit)
        
        # 미국: S&P 500 상위 + 섹터별 대표주  
        us_stocks = get_us_top_stocks(us_limit)
        
        return kr_stocks, us_stocks
        
    except Exception as e:
        print(f"종목 선별 실패: {e}")
        # 빈 리스트 반환
        return ([], [])
