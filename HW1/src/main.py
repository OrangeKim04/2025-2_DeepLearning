from __future__ import annotations

from data_manager import data_manager
from config import AppConfig
from kakao import KakaoClient


def run_once() -> None:
	config = AppConfig.load()
	
	# 공통 데이터 관리자에서 최신 데이터 가져오기
	print("📋 최신 데이터 가져오는 중...")
	data = data_manager.get_fresh_data()
	
	# 카카오톡으로 리포트 전송
	client = KakaoClient(config)
	client.send_self_memo(data['report_text'])
	print("✅ 카카오톡 리포트 전송 완료")


if __name__ == "__main__":
	run_once()
