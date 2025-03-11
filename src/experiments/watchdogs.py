import os
import shutil
import time
import subprocess
import sqlite3
from experiments.benchmark import BENCHMARKS_DB


def clean_stuck_rows(current_threshold):
	conn = sqlite3.connect(BENCHMARKS_DB)
	cursor = conn.cursor()
	cursor.execute("DELETE FROM experiments WHERE vte IS NULL")
	print(f"Removed {cursor.rowcount} stuck rows with NULL vte from the database.")
	conn.commit()
	conn.close()

	shutil.copy(BENCHMARKS_DB, f"{current_threshold}_{BENCHMARKS_DB}")


def run(current_threshold, check_interval, log_filename):
	try:
		while True:
			print(f"Benchmark with {current_threshold} minutes threshold started")
			with open(log_filename, 'a') as log_file:
				process = subprocess.Popen([os.sys.executable, 'benchmark.py'], stdout=log_file, stderr=log_file, cwd=os.getcwd())

			while True:
				time.sleep(check_interval)

				if process.poll() is not None:
					print(f"Benchmark with {current_threshold} minutes threshold done")
					clean_stuck_rows(current_threshold)
					current_threshold *= 2
					break

				if os.path.getmtime(BENCHMARKS_DB) < time.time() - 60 * current_threshold:
					print(f"Experiment is stuck, killing it")
					process.terminate()
					process.wait()
					time.sleep(1)
					break

	except KeyboardInterrupt:
		process.terminate()
		process.wait()
		print("Watchdog terminato manualmente.")


if __name__ == '__main__':
	run(1, 10, 'benchmark_output.log')


