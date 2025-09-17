## Daily Stock Report Bot (KakaoTalk)

Python app that fetches KRX and US stock data, analyzes with technical indicators, summarizes recent news, formats a KakaoTalk-style message, and sends it automatically every day at 08:30 KST.

### Features
- KRX via FinanceDataReader, US via yfinance
- Indicators: SMA, RSI, MACD, Bollinger Bands
- Volume/volatility screening and simple buy/sell timing hints
- News summarization via OpenAI API (optional)
- Sends KakaoTalk message using Kakao Talk API
- Scheduled daily at 08:30 KST using APScheduler

### Project Structure
```
HW1/
  README.md
  requirements.txt
  .env.example
  src/
    __init__.py
    config.py
    data_fetchers.py
    indicators.py
    screener.py
    news.py
    report.py
    kakao.py
    scheduler_job.py
    main.py
```

### Prerequisites
- Python 3.10+
- Kakao Developers app with Talk API permissions
- (Optional) OpenAI API key for news summarization

### Installation
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Environment Variables
Copy `.env.example` to `.env` and fill values:
```
# User config
USER_NAME=JAKE

# Kakao OAuth
KAKAO_CLIENT_ID=your_kakao_rest_api_key
KAKAO_REDIRECT_URI=http://localhost
KAKAO_REFRESH_TOKEN=your_refresh_token
KAKAO_ACCESS_TOKEN=your_initial_access_token

# Optional: OpenAI for news summarization
OPENAI_API_KEY=sk-...

# Universe configuration (optional - leave empty for automatic selection)
# KR_TICKERS=005930,000660,035420   # Override Korean stocks if desired
# US_TICKERS=AAPL,MSFT,NVDA         # Override US stocks if desired
```

Token note: Access tokens expire. This app auto-refreshes using the refresh token and stores the latest tokens in `token_store.json`.

### How to Run

#### 1. 웹 애플리케이션 (권장)
```bash
python src/web_app.py
```
- 브라우저에서 `http://localhost:5000` 접속
- 실시간 데이터 업데이트 가능
- 모바일 친화적 반응형 UI

#### 2. 원래 방식
- One-off run now:
```bash
python -m src.main
```
- Start scheduler (runs daily at 08:30 Asia/Seoul):
```bash
python -m src.scheduler_job
```

### 웹 배포 (Heroku)
1. Heroku CLI 설치
2. Heroku 앱 생성:
```bash
heroku create your-app-name
```
3. 환경변수 설정:
```bash
heroku config:set USER_NAME=JAKE
heroku config:set OPENAI_API_KEY=your_key
# 기타 필요한 환경변수들...
```
4. 배포:
```bash
git push heroku main
```

### KakaoTalk Permissions
- For self-memo, the endpoint `v2/api/talk/memo/default/send` works with Talk API scope.
- To message a specific friend, you must obtain additional scope, fetch friend UUIDs, and use `v1/api/talk/friends/message/default/send`. This code includes both methods; enable the friend send only if your app has the permissions.

### Disclaimer
This is for educational purposes. Not investment advice.
