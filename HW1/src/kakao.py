from __future__ import annotations

import time
from typing import Optional, Dict, Any
import requests

from config import AppConfig, load_token_store, save_token_store

KAKAO_AUTH_HOST = "https://kauth.kakao.com"
KAKAO_API_HOST = "https://kapi.kakao.com"


class KakaoClient:
	def __init__(self, config: AppConfig) -> None:
		self.config = config
		self._tokens = load_token_store() or {}
		if config.kakao_access_token:
			self._tokens["access_token"] = config.kakao_access_token
		if config.kakao_refresh_token:
			self._tokens["refresh_token"] = config.kakao_refresh_token

	def _save(self) -> None:
		save_token_store(self._tokens)

	def _refresh_access_token(self) -> None:
		refresh_token = self._tokens.get("refresh_token") or self.config.kakao_refresh_token
		if not refresh_token:
			raise RuntimeError("No Kakao refresh token configured")
		data = {
			"grant_type": "refresh_token",
			"client_id": self.config.kakao_client_id,
			"refresh_token": refresh_token,
		}
		resp = requests.post(f"{KAKAO_AUTH_HOST}/oauth/token", data=data, timeout=10)
		resp.raise_for_status()
		payload = resp.json()
		access_token = payload.get("access_token")
		if access_token:
			self._tokens["access_token"] = access_token
			self._save()

	def _get_auth_header(self) -> Dict[str, str]:
		token = self._tokens.get("access_token")
		if not token:
			self._refresh_access_token()
			token = self._tokens.get("access_token")
		if not token:
			raise RuntimeError("Failed to acquire Kakao access token")
		return {"Authorization": f"Bearer {token}"}

	def send_self_memo(self, text: str) -> None:
		# 카카오톡 메시지 길이 제한 (약 200자)
		max_length = 200
		
		if len(text) <= max_length:
			self._send_single_message(text)
		else:
			# 긴 메시지를 여러 개로 분할
			parts = self._split_message(text, max_length)
			for i, part in enumerate(parts, 1):
				message = f"[{i}/{len(parts)}]\n{part}"
				self._send_single_message(message)
	
	def _split_message(self, text: str, max_length: int) -> list:
		"""메시지를 적절한 길이로 분할"""
		lines = text.split('\n')
		parts = []
		current_part = []
		current_length = 0
		
		for line in lines:
			line_length = len(line) + 1  # +1 for newline
			
			if current_length + line_length > max_length and current_part:
				parts.append('\n'.join(current_part))
				current_part = [line]
				current_length = line_length
			else:
				current_part.append(line)
				current_length += line_length
		
		if current_part:
			parts.append('\n'.join(current_part))
		
		return parts
	
	def _send_single_message(self, text: str) -> None:
		"""단일 메시지 전송"""
		url = f"{KAKAO_API_HOST}/v2/api/talk/memo/default/send"
		payload = {"object_type": "text", "text": text, "link": {}}
		headers = self._get_auth_header()
		headers["Content-Type"] = "application/x-www-form-urlencoded"
		
		# form-data 형식으로 전송
		data = {"template_object": json_dumps(payload)}
		resp = requests.post(url, headers=headers, data=data, timeout=10)
		
		if resp.status_code == 401:
			self._refresh_access_token()
			headers = self._get_auth_header()
			headers["Content-Type"] = "application/x-www-form-urlencoded"
			resp = requests.post(url, headers=headers, data=data, timeout=10)
		resp.raise_for_status()

	def list_friends(self) -> Any:
		url = f"{KAKAO_API_HOST}/v1/api/talk/friends"
		headers = self._get_auth_header()
		resp = requests.get(url, headers=headers, timeout=10)
		resp.raise_for_status()
		return resp.json()

	def send_to_friend(self, uuids: list[str], text: str) -> None:
		url = f"{KAKAO_API_HOST}/v1/api/talk/friends/message/default/send"
		payload = {"object_type": "text", "text": text, "link": {}}
		headers = self._get_auth_header()
		data = {"receiver_uuids": json_dumps(uuids), "template_object": json_dumps(payload)}
		resp = requests.post(url, headers=headers, data=data, timeout=10)
		if resp.status_code == 401:
			self._refresh_access_token()
			headers = self._get_auth_header()
			resp = requests.post(url, headers=headers, data=data, timeout=10)
		resp.raise_for_status()


def json_dumps(obj: Any) -> str:
	import json
	return json.dumps(obj, ensure_ascii=False)
