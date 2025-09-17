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

# Universe configuration (override defaults if desired)
KR_TICKERS=005930,000660,035420   # Samsung Elec, SK Hynix, Naver
US_TICKERS=AAPL,MSFT,NVDA
```

Token note: Access tokens expire. This app auto-refreshes using the refresh token and stores the latest tokens in `token_store.json`.

### How to Run
- One-off run now:
```bash
python -m src.main
```
- Start scheduler (runs daily at 08:30 Asia/Seoul):
```bash
python -m src.scheduler_job
```

### KakaoTalk Permissions
- For self-memo, the endpoint `v2/api/talk/memo/default/send` works with Talk API scope.
- To message a specific friend, you must obtain additional scope, fetch friend UUIDs, and use `v1/api/talk/friends/message/default/send`. This code includes both methods; enable the friend send only if your app has the permissions.

### Disclaimer
This is for educational purposes. Not investment advice.
