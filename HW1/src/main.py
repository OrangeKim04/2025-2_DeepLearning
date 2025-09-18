from __future__ import annotations

from data_manager import data_manager
from config import AppConfig
from kakao import KakaoClient


def run_once() -> None:
	config = AppConfig.load()
	
	# 공통 데이터 관리자에서 최신 데이터 가져오기
	print("📋 최신 데이터 가져오는 중...")
	data = data_manager.get_fresh_data()
	
	# 리포트를 파일로 저장 (카카오톡과 동일한 내용)
	report_text = data['report_text']
	with open('report.txt', 'w', encoding='utf-8') as f:
		f.write(report_text)
	print("💾 리포트 파일 저장 완료")
	
	# 카카오톡으로 리포트 전송
	client = KakaoClient(config)
	client.send_self_memo(report_text)
	print("✅ 카카오톡 리포트 전송 완료")


if __name__ == "__main__":
	run_once()
