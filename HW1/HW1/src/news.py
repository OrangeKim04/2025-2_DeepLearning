from __future__ import annotations

import datetime as dt
import os
from typing import List

import requests

try:
	from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
	OpenAI = None  # type: ignore


def fetch_market_headlines() -> List[str]:
	"""Fetch recent market headlines from a free source.

	For simplicity (no API key), use a couple of RSS feeds.
	"""
	sources = [
		"https://finance.yahoo.com/news/rssindex",
		"https://www.koreaherald.com/rss/020303000000.xml",
	]
	headlines: List[str] = []
	for url in sources:
		try:
			resp = requests.get(url, timeout=10)
			text = resp.text
			for line in text.splitlines():
				if "<title>" in line and "</title>" in line:
					t = line.split("<title>")[-1].split("</title>")[0].strip()
					if t and t.lower() != "yahoo news - latest news & headlines":
						headlines.append(t)
		except Exception:
			continue
	return headlines[:10]


def summarize_news_openai(headlines: List[str], openai_api_key: str | None) -> str:
	if not headlines:
		return "최근 주요 헤드라인 없음"
	if not openai_api_key or OpenAI is None:
		# Simple heuristic fallback
		joined = "; ".join(headlines[:5])
		return f"핵심 이슈 요약: {joined}"
	client = OpenAI(api_key=openai_api_key)
	prompt = (
		"다음 오늘의 금융/증시 헤드라인을 한국어로 3문장 이내로 핵심만 요약해줘.\n" +
		"- 과열/공포 지표나 대형 이벤트(FOMC, CPI, 실적) 언급 포함\n" +
		"- 투자 조언은 하지 말 것\n\n" + "\n".join(f"- {h}" for h in headlines[:10])
	)
	resp = client.chat.completions.create(
		model="gpt-4o-mini",
		messages=[{"role": "user", "content": prompt}],
		temperature=0.3,
		max_tokens=200,
	)
	return resp.choices[0].message.content.strip()
