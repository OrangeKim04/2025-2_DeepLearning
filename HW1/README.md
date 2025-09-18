# 📈 AI 주식 분석 봇 (KakaoTalk)

> **실시간 주식 분석과 개인화된 투자 인사이트를 카카오톡으로 받아보세요!**

[![Cursor](https://img.shields.io/badge/Built%20with-Cursor-00D4AA?style=flat&logo=cursor&logoColor=white)](https://cursor.sh/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

## 🎯 프로젝트 개요

**AI 주식 분석 봇**은 한국과 미국 주식 시장을 실시간으로 분석하여 개인화된 투자 추천을 카카오톡으로 전송하는 지능형 시스템입니다.

> **💡 Cursor AI 코딩**: 이 프로젝트는 [Cursor](https://cursor.sh/) AI 코딩 어시스턴트를 활용하여 개발되었습니다. AI와의 협업을 통해 효율적이고 혁신적인 개발 경험을 보여줍니다.

### ✨ 핵심 기능
- **🤖 완전 자동화**: 하드코딩 없는 동적 종목 선별
- **📊 실시간 분석**: RSI, MACD, 거래량 등 기술적 지표 기반 분석
- **🎯 개인화된 추천**: 각 종목별 맞춤형 매수/매도 시점 제시
- **📱 카카오톡 자동 메모**: 실시간 리포트를 본인 카카오톡으로 즉시 전송
- **🔗 웹 링크 지원**: 카카오톡 "자세히 보기"로 동일한 리포트 웹에서 확인 (PC/모바일 최적화)
- **📰 뉴스 요약**: OpenAI를 활용한 시장 뉴스 자동 요약

## 🔧 기술적 특징
- **📈 데이터 소스**: 한국(KRX) - FinanceDataReader, 미국 - yfinance
- **📊 기술적 지표**: SMA, RSI, MACD, 볼린저 밴드, 거래량 분석
- **🎯 스크리닝**: 시가총액, 거래량, 변동성 기반 종목 선별
- **🤖 AI 뉴스 요약**: OpenAI GPT를 활용한 시장 뉴스 자동 요약
- **⏰ 자동 스케줄링**: 매일 08:30 KST 자동 실행
- **🌐 웹 링크**: Flask 기반 카카오톡 링크용 최소 서버 (HTML/CSS 스타일링)
- **🚀 AI 개발 도구**: Cursor AI 코딩 어시스턴트로 효율적 개발

## 📁 프로젝트 구조
```
HW1/
├── README.md                 # 프로젝트 문서
├── requirements.txt          # Python 의존성
├── .env                     # 환경변수 설정 (숨김 파일)
└── src/
    ├── __init__.py
    ├── config.py            # 설정 관리
    ├── data_manager.py      # 공통 데이터 관리자
    ├── data_fetchers.py     # 주식 데이터 수집
    ├── indicators.py        # 기술적 지표 계산
    ├── screener.py          # 종목 스크리닝
    ├── stock_selector.py    # 동적 종목 선별
    ├── news.py              # 뉴스 수집 및 요약
    ├── report.py            # 리포트 생성
    ├── kakao.py             # 카카오톡 API 연동
    ├── web_app.py           # Flask 웹 서버 (카카오톡 링크용)
    ├── scheduler_job.py     # 자동 스케줄링
    └── main.py              # 메인 실행 파일
```

## 🚀 시작하기

### 📋 사전 요구사항
- **Python 3.10+** 
- **Kakao Developers** 앱 등록 및 Talk API 권한
- **OpenAI API 키** - 뉴스 요약 기능용 (현재 활성화됨)
- **.env 파일** - 환경변수 설정 (현재 사용 중)
- **ngrok** - 외부 접근을 위한 터널링 서비스 (현재 사용 중)

### 💻 설치 방법
```bash
# 가상환경 생성 및 활성화
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1

# 의존성 설치
pip install -r requirements.txt
```

### ⚙️ 환경변수 설정

#### 📝 .env 파일 생성
프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# 사용자 설정
USER_NAME=YOUR_NAME

# 카카오 OAuth 설정 (필수)
KAKAO_CLIENT_ID=your_kakao_rest_api_key
KAKAO_ACCESS_TOKEN=your_initial_access_token
KAKAO_REFRESH_TOKEN=your_refresh_token

# OpenAI API (선택사항 - 뉴스 요약용)
OPENAI_API_KEY=sk-your_openai_api_key

# ngrok URL (외부 접근용)
NGROK_URL=https://your-ngrok-url.ngrok-free.app
```

#### 🔧 현재 프로젝트 설정 상태
- **환경변수 파일**: `.env` 파일 사용
- **사용자명**: 설정됨
- **카카오톡 API**: 설정됨
- **OpenAI API**: 설정됨 (뉴스 요약 기능 활성화)
- **종목 선별**: 완전 자동 선별 모드 (하드코딩 완전 제거)
  - **한국**: FinanceDataReader로 시가총액 기반 자동 선별
  - **미국**: Wikipedia S&P 500 + Yahoo Finance 트렌딩 + ETF 기반 동적 수집

> **💡 토큰 관리**: Access 토큰은 만료됩니다. 이 앱은 refresh 토큰을 사용해 자동 갱신하고 `token_store.json`에 저장합니다.

## 🎮 실행 방법

### 📱 카카오톡 메시지 전송 (메인 기능)
```bash
python src/main.py
```
- **즉시 실행**: 현재 시점의 분석 결과를 카카오톡으로 전송
- **웹 링크 지원**: "자세히 보기" 버튼으로 동일한 리포트 웹에서 확인
- **모바일/웹 지원**: 모든 디바이스에서 동일한 경험 (PC/모바일 최적화)

### 🌐 웹 서버 (카카오톡 링크용)
```bash
python src/web_app.py
```
- **카카오톡 링크**: `/report.txt` 엔드포인트로 리포트 제공 (HTML 스타일링)
- **최소 서버**: 카카오톡 링크용으로만 최적화
- **모바일 호환**: PC/모바일 모두에서 최적화된 가독성
- **외부 접근**: ngrok을 통한 외부에서도 접근 가능

### ⏰ 자동 스케줄링
```bash
python src/scheduler_job.py
```
- **자동 실행**: 매일 08:30 KST에 자동으로 분석 및 전송
- **백그라운드**: 서버에서 24시간 실행 가능

## 🚀 배포 방법

### 🌐 ngrok을 통한 로컬 배포 (현재 사용 중)

#### 📋 사전 준비
1. **ngrok 설치**: [ngrok.com](https://ngrok.com/)에서 다운로드
2. **ngrok 계정**: 무료 계정 생성 (선택사항)

#### 🚀 배포 단계
```bash
# 1. Flask 앱 실행
python src/web_app.py

# 2. 새 터미널에서 ngrok 실행
ngrok http 5000

# 3. ngrok URL 확인 및 사용
# 예: https://xxxxx.ngrok-free.app
```

#### ✅ 배포 확인
- **카카오톡 테스트**: `python src/main.py`로 메시지 전송
- **링크 테스트**: 카카오톡 "자세히 보기" 버튼으로 리포트 확인
- **외부 접근**: 다른 기기에서도 ngrok URL로 접근 가능

#### 💡 ngrok 장점
- **간편한 설정**: 복잡한 서버 설정 불필요
- **즉시 배포**: 로컬 개발 환경을 바로 외부에 노출
- **HTTPS 지원**: 자동 SSL 인증서 제공
- **무료 사용**: 개발 및 테스트 목적으로 충분

## 🔐 카카오톡 API 권한

### 📝 자동 메모 전송 (현재 사용 중)
- **엔드포인트**: `v2/api/talk/memo/default/send`
- **권한**: Talk API 스코프만 필요
- **기능**: 본인에게 메모 전송 + 웹 링크 지원
- **상태**: ✅ 활성화됨

### 👥 친구 메시지 전송 (구현됨, 미사용)
- **엔드포인트**: `v1/api/talk/friends/message/default/send`
- **권한**: 추가 스코프 필요
- **기능**: 특정 친구에게 메시지 전송
- **상태**: ❌ 현재 사용되지 않음 (코드에만 존재)

## 🛠️ 개발 도구

이 프로젝트는 다음과 같은 최신 개발 도구들을 활용하여 제작되었습니다:

- **🤖 [Cursor AI](https://cursor.sh/)**: AI 코딩 어시스턴트로 효율적인 개발
- **🐍 Python 3.10+**: 메인 개발 언어
- **🌐 Flask**: 웹 프레임워크
- **📊 Pandas & NumPy**: 데이터 분석
- **🤖 OpenAI API**: 뉴스 요약 및 AI 기능
- **📱 KakaoTalk API**: 메시지 전송
- **🌐 ngrok**: 로컬 서버 외부 노출 (현재 사용 중)

---
**Made with ❤️ and 🤖 AI for intelligent stock analysis**
