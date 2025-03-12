import sqlite3
from datetime import datetime
from experiments.experiment import single_execution
from experiments.read import read_cpi_bundles
import signal
import sys
import time
from experiments.telegram_bot import send_telegram_message

BENCHMARKS_DB = 'benchmarks.sqlite'

conn = sqlite3.connect(BENCHMARKS_DB)
cursor = conn.cursor()


def handle_termination(signum, frame):
    print("Termination signal received. Closing database connection.")
    conn.close()
    sys.exit(0)


def run_benchmarks():
    global conn
    conn = sqlite3.connect(BENCHMARKS_DB)

    signal.signal(signal.SIGTERM, handle_termination)
    signal.signal(signal.SIGINT, handle_termination)

    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            x INTEGER,
            y INTEGER,
            w INTEGER,
            z INTEGER,
            num_impacts INTEGER,
            choice_distribution REAL,
            generation_mode TEXT,
            duration_interval_min INTEGER,
            duration_interval_max INTEGER,
            vts TIMESTAMP,
            vte TIMESTAMP,
            time_create_execution_tree REAL,
            time_evaluate_cei_execution_tree REAL,
            found_strategy_time REAL,
            build_strategy_time REAL,
            time_explain_strategy REAL, 
            strategy_tree_time REAL,
            initial_bounds TEXT,
            final_bounds TEXT,
            PRIMARY KEY (x, y, w)
        )
    ''')
    conn.commit()

    print(str(datetime.now()) + " Starting benchmark...")

    last_time = time.time() + 10

    try:
        for k in range(2, 20):
            for x in range(1, k-1):
                y = k - x

                if x <= 10 and y <= 10:
                    bundle = read_cpi_bundles(x=1, y=6)

                    if not bundle:
                        s = f"No bundle found for x={x}, y={y}"
                        print(str(datetime.now()) + " " + s)
                        send_telegram_message(s)

                    for w in range(0, len(bundle)):
                        single_execution(cursor, conn, 1, 6, w, bundle)

                        if time.time() - last_time > 1:
                            last_time = time.time()
                            send_telegram_message(f"x={x}, y={y}, w={w} Done")


                    return
    except Exception as e:
        print(str(datetime.now()) + f" Error during benchmark: {str(e)}")
        conn.rollback()

if __name__ == '__main__':
    run_benchmarks()
    conn.close()
    print(str(datetime.now()) + " Benchmark completed.")