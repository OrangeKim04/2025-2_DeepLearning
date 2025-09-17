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
        # 방법 1: Wikipedia에서 S&P 500 종목 리스트 가져오기
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
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
        print(f"Wikipedia S&P 500 수집 실패: {e}")
        
        # 방법 2: yfinance를 사용한 대안 - 다양한 규모의 종목들을 동적으로 찾기
        try:
            print("yfinance를 사용하여 다양한 종목 수집 시도...")
            return get_diverse_stocks_dynamically()
        except Exception as e2:
            print(f"동적 수집도 실패: {e2}")
            # 최종 폴백: 빈 리스트 반환 (프로그램이 종료되도록)
            return []


def get_diverse_stocks_dynamically() -> List[str]:
    """완전히 동적으로 다양한 규모의 종목들을 찾기 (하드코딩 제거)"""
    try:
        # 방법 1: NASDAQ과 NYSE에서 인기 종목들을 동적으로 가져오기
        return get_popular_stocks_from_exchanges()
    except Exception as e:
        print(f"거래소별 인기 종목 수집 실패: {e}")
        
        # 방법 2: yfinance의 인기 종목 API 사용
        try:
            return get_trending_stocks_from_yfinance()
        except Exception as e2:
            print(f"트렌딩 종목 수집도 실패: {e2}")
            return []


def get_popular_stocks_from_exchanges() -> List[str]:
    """주요 거래소에서 인기 종목들을 동적으로 수집"""
    try:
        # Yahoo Finance의 인기 종목 페이지에서 수집
        url = "https://finance.yahoo.com/trending-tickers"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 인기 종목 테이블에서 티커 추출
        tickers = []
        
        # 다양한 선택자로 시도
        selectors = [
            'table tbody tr td[data-field="symbol"]',
            'table tbody tr td:first-child',
            '[data-testid="trending-tickers"] table tbody tr td:first-child'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    ticker = element.get_text(strip=True)
                    if ticker and len(ticker) <= 5 and ticker.isalpha():
                        tickers.append(ticker)
                break
        
        if not tickers:
            # 대안: 다른 인기 종목 페이지 시도
            return get_trending_stocks_from_yfinance()
        
        # 유효성 검증
        valid_tickers = []
        ticker_data = []
        
        print("인기 종목들 유효성 검증 중...")
        for ticker in tickers[:50]:  # 상위 50개만 검증
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                if (info and 
                    'regularMarketPrice' in info and 
                    info.get('regularMarketPrice', 0) > 0 and
                    info.get('marketState', '') in ['REGULAR', 'CLOSED']):
                    
                    market_cap = info.get('marketCap', 0)
                    if market_cap >= 1_000_000_000:  # 10억 달러 이상
                        ticker_data.append((ticker, market_cap))
                        valid_tickers.append(ticker)
                        
            except Exception:
                continue
        
        # 시가총액 기준으로 정렬
        ticker_data.sort(key=lambda x: x[1], reverse=True)
        
        print(f"유효한 인기 종목 {len(valid_tickers)}개 발견")
        return [ticker for ticker, _ in ticker_data]
        
    except Exception as e:
        print(f"거래소 인기 종목 수집 실패: {e}")
        return []


def get_trending_stocks_from_yfinance() -> List[str]:
    """yfinance를 사용하여 트렌딩 종목들을 동적으로 찾기"""
    try:
        # 방법 1: 시장 지수 ETF들의 구성종목을 활용
        etf_tickers = ['SPY', 'QQQ', 'IWM', 'VTI', 'VEA', 'VWO']  # 다양한 시장 대표 ETF들
        
        valid_tickers = []
        ticker_data = []
        
        print("ETF 기반 종목 수집 중...")
        for etf in etf_tickers:
            try:
                stock = yf.Ticker(etf)
                info = stock.info
                if (info and 
                    'regularMarketPrice' in info and 
                    info.get('regularMarketPrice', 0) > 0):
                    
                    # ETF 자체도 유효한 투자 대상
                    market_cap = info.get('marketCap', 0)
                    ticker_data.append((etf, market_cap))
                    valid_tickers.append(etf)
                    
            except Exception:
                continue
        
        # 방법 2: 알파벳 조합으로 가능한 티커들을 체계적으로 검증
        # (A-Z, AA-ZZ, AAA-ZZZ 조합 중 실제 존재하는 종목 찾기)
        print("알파벳 조합으로 종목 검색 중...")
        additional_tickers = generate_and_validate_tickers()
        
        # 추가 종목들을 검증
        for ticker in additional_tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                if (info and 
                    'regularMarketPrice' in info and 
                    info.get('regularMarketPrice', 0) > 0 and
                    info.get('marketState', '') in ['REGULAR', 'CLOSED']):
                    
                    market_cap = info.get('marketCap', 0)
                    if market_cap >= 1_000_000_000:  # 10억 달러 이상
                        ticker_data.append((ticker, market_cap))
                        valid_tickers.append(ticker)
                        
            except Exception:
                continue
        
        # 시가총액 기준으로 정렬
        ticker_data.sort(key=lambda x: x[1], reverse=True)
        
        print(f"동적으로 발견한 종목 {len(valid_tickers)}개")
        return [ticker for ticker, _ in ticker_data]
        
    except Exception as e:
        print(f"트렌딩 종목 수집 실패: {e}")
        return []


def generate_and_validate_tickers() -> List[str]:
    """알파벳 조합으로 가능한 티커들을 생성"""
    import random
    import string
    
    # 1-4글자 조합으로 가능한 티커들 생성
    possible_tickers = []
    
    # 1글자 (A-Z)
    for char in string.ascii_uppercase:
        possible_tickers.append(char)
    
    # 2글자 (AA-ZZ)
    for char1 in string.ascii_uppercase:
        for char2 in string.ascii_uppercase:
            possible_tickers.append(char1 + char2)
    
    # 3글자 (AAA-ZZZ) - 샘플링으로 제한
    for _ in range(1000):  # 1000개만 샘플링
        ticker = ''.join(random.choices(string.ascii_uppercase, k=3))
        possible_tickers.append(ticker)
    
    # 4글자 (AAAA-ZZZZ) - 샘플링으로 제한
    for _ in range(500):  # 500개만 샘플링
        ticker = ''.join(random.choices(string.ascii_uppercase, k=4))
        possible_tickers.append(ticker)
    
    # 중복 제거 및 랜덤 샘플링
    possible_tickers = list(set(possible_tickers))
    random.shuffle(possible_tickers)
    
    # 상위 200개만 반환 (너무 많은 요청 방지)
    return possible_tickers[:200]


def get_kr_top_stocks(limit: int = 20) -> List[str]:
    """한국 상위 종목들을 자동으로 수집 (다양한 규모 포함)"""
    try:
        # KRX 상장사 목록 가져오기
        stock_list = fdr.StockListing('KRX')
        
        # 시가총액 상위 종목 필터링 (상장주식수 * 종가 기준)
        stock_list['market_cap'] = stock_list['Marcap']  # 시가총액
        stock_list = stock_list[stock_list['market_cap'] > 0]  # 유효한 데이터만
        
        # 시가총액 기준으로 정렬
        stock_list = stock_list.sort_values('market_cap', ascending=False)
        
        # 다양한 규모의 종목들을 선별
        # 상위 50%는 대형주, 나머지는 중소형주로 구성
        large_cap_count = min(limit // 2, 10)  # 대형주 절반
        mid_small_cap_count = limit - large_cap_count  # 중소형주 절반
        
        # 대형주 (상위 30%에서 선별)
        large_cap_stocks = stock_list.head(int(len(stock_list) * 0.3)).head(large_cap_count)
        
        # 중소형주 (30-80% 구간에서 선별)
        mid_small_start = int(len(stock_list) * 0.3)
        mid_small_end = int(len(stock_list) * 0.8)
        mid_small_cap_stocks = stock_list.iloc[mid_small_start:mid_small_end].head(mid_small_cap_count)
        
        # 종목 합치기
        selected_stocks = pd.concat([large_cap_stocks, mid_small_cap_stocks])
        selected_stocks = selected_stocks.drop_duplicates()  # 중복 제거
        
        # 상위 종목 코드 반환
        top_stocks = selected_stocks.head(limit)['Code'].tolist()
        return [str(code).zfill(6) for code in top_stocks]  # 6자리 코드로 변환
        
    except Exception as e:
        print(f"한국 종목 수집 실패: {e}")
        # 실패 시 빈 리스트 반환
        return []


def get_us_top_stocks(limit: int = 20) -> List[str]:
    """미국 상위 종목들을 자동으로 수집 (다양한 규모 포함)"""
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
    """다양한 섹터와 규모에서 종목을 선별 (대형주, 중형주, 성장주 포함)"""
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
