import os
import json
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

TOKEN_STORE_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "token_store.json"))


def _load_list_from_env(name: str, default: List[str]) -> List[str]:
	value = os.getenv(name)
	if not value:
		return default
	return [v.strip() for v in value.split(",") if v.strip()]


@dataclass
class AppConfig:
	user_name: str
	kr_tickers: List[str]
	us_tickers: List[str]
	openai_api_key: Optional[str]
	kakao_client_id: str
	kakao_redirect_uri: str
	kakao_access_token: Optional[str]
	kakao_refresh_token: Optional[str]

	@staticmethod
	def load() -> "AppConfig":
		return AppConfig(
			user_name=os.getenv("USER_NAME", "USER"),
			kr_tickers=_load_list_from_env("KR_TICKERS", []),  # 자동 선별 사용
			us_tickers=_load_list_from_env("US_TICKERS", []),  # 자동 선별 사용
			openai_api_key=os.getenv("OPENAI_API_KEY"),
			kakao_client_id=os.getenv("KAKAO_CLIENT_ID", ""),
			kakao_redirect_uri=os.getenv("KAKAO_REDIRECT_URI", "http://localhost"),
			kakao_access_token=os.getenv("KAKAO_ACCESS_TOKEN"),
			kakao_refresh_token=os.getenv("KAKAO_REFRESH_TOKEN"),
		)


def load_token_store() -> dict:
	try:
		with open(TOKEN_STORE_PATH, "r", encoding="utf-8") as f:
			return json.load(f)
	except FileNotFoundError:
		return {}


def save_token_store(data: dict) -> None:
	with open(TOKEN_STORE_PATH, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
