import os
import shutil
import signal
import sys
import threading
import time
import subprocess
import sqlite3
from datetime import datetime

from src.utils.env import BENCHMARKS_DB, LOG_FILENAME, BENCHMARKS_DB_NOT_UR
from src.experiments.telegram.telegram_bot import (
    send_telegram_message,
    listen_for_messages,
    TELEGRAM_BOT_TOKEN,
)


def clean_stuck_rows(current_threshold, db_path=BENCHMARKS_DB):
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	cursor.execute(
		"SELECT name FROM sqlite_master WHERE type='table' AND name='experiments'"
	)
	if cursor.fetchone() is None:
		print("Table 'experiments' does not exist yet, skipping stuck rows cleanup.")
		conn.close()
		return

	cursor.execute("DELETE FROM experiments WHERE vte IS NULL")
	print(f"Removed {cursor.rowcount} stuck rows with NULL vte from the database.")
	conn.commit()
	conn.close()

	shutil.copy(db_path, f"{current_threshold}_{db_path}")


process = None

def watchdog_handle_termination(signum, frame):
	process.terminate()
	s = "Experiment terminated"
	print(str(datetime.now()) + " " + s)
	send_telegram_message(s)
	sys.exit(0)


def execute_benchmark(not_use_Ur = False):
	with open(LOG_FILENAME, 'a') as log_file:
		benchmark_path = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			"benchmark.py --not-use-Ur" if not_use_Ur else "benchmark.py")

		if not os.path.exists(benchmark_path):
			raise FileNotFoundError(f"benchmark.py not found at {benchmark_path}")

		return subprocess.Popen([os.sys.executable, benchmark_path], stdout=log_file, stderr=log_file, cwd=os.getcwd())




def run(current_threshold, check_interval, not_use_Ur = False):
	global process

	signal.signal(signal.SIGTERM, watchdog_handle_termination)
	signal.signal(signal.SIGINT, watchdog_handle_termination)

	#Telegram Bot
	if TELEGRAM_BOT_TOKEN != '':
		threading.Thread(target=listen_for_messages, daemon=True).start()

	try:

		while True:
			process = execute_benchmark(not_use_Ur)

			while True:
				time.sleep(check_interval)

				if process.poll() is not None:
					#s = f"Benchmark with {current_threshold} minutes threshold done"
					#print(str(datetime.now()) + " " + s)
					#send_telegram_message(s)
					clean_stuck_rows(current_threshold, BENCHMARKS_DB_NOT_UR if not_use_Ur else BENCHMARKS_DB)
					current_threshold *= 2
					break
				
				benchmarcks_db = os.path.getmtime(BENCHMARKS_DB_NOT_UR) if not_use_Ur else os.path.getmtime(BENCHMARKS_DB)
				if benchmarcks_db < time.time() - 60 * current_threshold:
					s = f"A experiment was stuck for {current_threshold} min and I killed it"
					print(str(datetime.now()) + " " + s)
					send_telegram_message(s)

					process.terminate()
					process.wait()
					time.sleep(1)
					break

				if current_threshold > 60 * 5:
					s = "Watchdog reached the maximum threshold of 5 hours"
					print(str(datetime.now()) + " " + s)
					send_telegram_message(s)
					sys.exit(0)


	except Exception as e:
		process.terminate()
		process.wait()
		s = "Watchdog terminated by exception: " + str(e)
		print(str(datetime.now()) + " " + s)
		send_telegram_message(s)