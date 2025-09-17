from __future__ import annotations

from datetime import datetime
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler

from .main import run_once

KST = pytz.timezone("Asia/Seoul")


def _job():
	run_once()


def start_scheduler() -> None:
	sched = BlockingScheduler(timezone=KST)
	sched.add_job(_job, "cron", hour=8, minute=30)
	print("Scheduler started for 08:30 KST daily")
	try:
		sched.start()
	except (KeyboardInterrupt, SystemExit):
		print("Scheduler stopped")


if __name__ == "__main__":
	start_scheduler()
