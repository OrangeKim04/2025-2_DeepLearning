from __future__ import annotations

from data_manager import data_manager
from config import AppConfig
from kakao import KakaoClient
from datetime import datetime
import os


def run_once() -> None:
	config = AppConfig.load()
	
	# 공통 데이터 관리자에서 최신 데이터 가져오기
	print("📋 최신 데이터 가져오는 중...")
	data = data_manager.get_fresh_data()
	
	# 리포트를 개별 파일로 저장 (카카오톡 메시지별 고유 링크)
	report_text = data['report_text']
	reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
	os.makedirs(reports_dir, exist_ok=True)
	filename = datetime.now().strftime('%Y%m%d_%H%M%S') + '.txt'
	file_path = os.path.normpath(os.path.join(reports_dir, filename))
	with open(file_path, 'w', encoding='utf-8') as f:
		f.write(report_text)
	print("💾 리포트 파일 저장:", file_path)
	
	# 카카오톡으로 리포트 전송 (해당 파일에 대한 링크 포함)
	client = KakaoClient(config)
	link_path = f"/reports/{filename}"
	client.send_self_memo(report_text, link_path=link_path)
	print("✅ 카카오톡 리포트 전송 완료")


if __name__ == "__main__":
	run_once()
