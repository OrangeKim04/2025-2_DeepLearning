from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any
import pytz

from data_fetchers import get_kr_ticker_name, get_us_ticker_name


KST = pytz.timezone("Asia/Seoul")


def format_recommendation_block(title: str, items: List[Dict[str, Any]]) -> str:
	lines = [title]
	for idx, it in enumerate(items, start=1):
		name = it["name"]
		code = it["ticker"]
		reason = it["reason"]
		entry = it["entry"]
		exit_ = it["exit"]
		close = it["close"]
		low52 = it["low_52w"]
		high52 = it["high_52w"]
		
		# 이모지와 함께 더 보기 좋게 포맷팅
		lines.append(f"🔥 {idx}. {name} ({code})")
		lines.append("")
		lines.append(f"📊 추천 이유:")
		lines.append(f"   {reason}")
		lines.append("")
		lines.append(f"📈 매수 시점:")
		lines.append(f"   {entry}")
		lines.append("")
		lines.append(f"📉 매도 시점:")
		lines.append(f"   {exit_}")
		lines.append("")
		lines.append(f"💰 가격 정보:")
		lines.append(f"   현재가: {close:,.0f}원")
		lines.append(f"   52주 최저: {low52:,.0f}원")
		lines.append(f"   52주 최고: {high52:,.0f}원")
		lines.append("")
		lines.append("─" * 50)
		lines.append("")
	return "\n".join(lines).strip()


def build_report(user_name: str, kr_recos: List[Dict[str, Any]], us_recos: List[Dict[str, Any]], news_summary: str) -> str:
	now_kst = datetime.now(KST)
	header = f"📈 {user_name}님을 위한 오늘의 주식 보고서 📈"
	stamp = now_kst.strftime("%Y년 %m월 %d일 %H시 %M분")
	
	lines: List[str] = [
		"=" * 40,
		header,
		"=" * 40,
		f"📅 보고 날짜: {stamp}",
		"",
		"🇰🇷 국내 주식 추천 (TOP 3)",
		""
	]
	
	lines.append(format_recommendation_block("", kr_recos))
	lines.append("")
	lines.append("🇺🇸 해외 주식 추천 (TOP 3)")
	lines.append("")
	lines.append(format_recommendation_block("", us_recos))
	lines.append("")
	lines.append("📰 시장 뉴스 요약")
	lines.append("─" * 20)
	lines.append(news_summary)
	lines.append("")
	lines.append("⚠️ 투자 주의사항")
	lines.append("─" * 20)
	lines.append("• 본 정보는 투자 참고용이며, 투자 결정은 본인의 판단과 책임하에 이루어져야 합니다.")
	lines.append("• 과거 성과가 미래 수익을 보장하지 않습니다.")
	lines.append("• 투자 전 충분한 검토와 리스크 관리가 필요합니다.")
	lines.append("")
	lines.append("=" * 40)
	
	return "\n".join([l for l in lines if l is not None])


def build_reco_item_kr(ticker: str, meta: Dict[str, Any]) -> Dict[str, Any]:
	name = get_kr_ticker_name(ticker)
	reason = (
		f"단기 추세 우위(SMA5>SMA20), RSI {meta.get('rsi'):.1f}, MACD 흐름 확인. "
		f"거래량 {meta.get('vol')/max(meta.get('vol_avg20',1),1):.1f}배"
	)
	return {
		"ticker": ticker,
		"name": name,
		"reason": reason,
		"entry": "단기 이동평균선이 장기 이동평균선을 돌파하는 시점",
		"exit": "RSI 지수가 70 이상으로 과매수 구간에 진입했을 때",
		"close": meta.get("close", float("nan")),
		"low_52w": meta.get("low_52w", float("nan")),
		"high_52w": meta.get("high_52w", float("nan")),
	}


def build_reco_item_us(ticker: str, meta: Dict[str, Any]) -> Dict[str, Any]:
	name = get_us_ticker_name(ticker)
	reason = (
		f"상대적 강도(RSI {meta.get('rsi'):.1f})와 거래량 확대로 모멘텀 강화. "
		f"MACD {meta.get('macd'):.2f}/{meta.get('macd_signal'):.2f}"
	)
	return {
		"ticker": ticker,
		"name": name,
		"reason": reason,
		"entry": "MACD가 시그널을 상향 돌파할 때",
		"exit": "RSI 지수가 70 이상으로 과매수 구간에 진입했을 때",
		"close": meta.get("close", float("nan")),
		"low_52w": meta.get("low_52w", float("nan")),
		"high_52w": meta.get("high_52w", float("nan")),
	}
