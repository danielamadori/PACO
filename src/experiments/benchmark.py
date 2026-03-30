import sqlite3
from datetime import datetime
from src.experiments.experiment import single_execution
from src.experiments.etl.read import read_cpi_bundles
import signal
import sys
import time
from src.experiments.telegram.telegram_bot import send_telegram_message
from src.utils.env import BENCHMARKS_DB, BENCHMARKS_DB_NOT_UR

conn = sqlite3.connect(BENCHMARKS_DB)
cursor = conn.cursor()


def handle_termination(signum, frame):
    print("Termination signal received. Closing database connection.")
    conn.close()
    sys.exit(0)


def ensure_experiments_columns(cursor):
    expected_columns = {
        "time_explain_strategy_impacts_based": "REAL",
        "time_explain_strategy_decision_based": "REAL",
        "time_explain_strategy_hybrid": "REAL",
        "explain_strategy_impacts_based_status": "TEXT",
        "explain_strategy_decision_based_status": "TEXT",
        "explain_strategy_hybrid_status": "TEXT",
        "explainer_leaves_impacts_based": "INTEGER",
        "explainer_leaves_decision_based": "INTEGER",
        "explainer_leaves_hybrid": "INTEGER",
        "explainer_leaves_total": "INTEGER",
        "explainer_choices_impacts_based_total": "INTEGER",
        "explainer_choices_impacts_based_forced": "INTEGER",
        "explainer_choices_impacts_based_arbitrary": "INTEGER",
        "explainer_choices_impacts_based_impacts": "INTEGER",
        "explainer_choices_impacts_based_decision": "INTEGER",
        "explainer_choices_decision_based_total": "INTEGER",
        "explainer_choices_decision_based_forced": "INTEGER",
        "explainer_choices_decision_based_arbitrary": "INTEGER",
        "explainer_choices_decision_based_impacts": "INTEGER",
        "explainer_choices_decision_based_decision": "INTEGER",
        "explainer_choices_hybrid_total": "INTEGER",
        "explainer_choices_hybrid_forced": "INTEGER",
        "explainer_choices_hybrid_arbitrary": "INTEGER",
        "explainer_choices_hybrid_impacts": "INTEGER",
        "explainer_choices_hybrid_decision": "INTEGER",
    }
    cursor.execute("PRAGMA table_info(experiments)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    for column_name, column_type in expected_columns.items():
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE experiments ADD COLUMN {column_name} {column_type}")


def run_benchmarks(not_use_Ur = False):
    global conn
    conn = sqlite3.connect(BENCHMARKS_DB_NOT_UR if not_use_Ur else BENCHMARKS_DB)

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
            time_explain_strategy_impacts_based REAL,
            time_explain_strategy_decision_based REAL,
            time_explain_strategy_hybrid REAL,
            explain_strategy_impacts_based_status TEXT,
            explain_strategy_decision_based_status TEXT,
            explain_strategy_hybrid_status TEXT,
            explainer_leaves_impacts_based INTEGER,
            explainer_leaves_decision_based INTEGER,
            explainer_leaves_hybrid INTEGER,
            explainer_leaves_total INTEGER,
            explainer_choices_impacts_based_total INTEGER,
            explainer_choices_impacts_based_forced INTEGER,
            explainer_choices_impacts_based_arbitrary INTEGER,
            explainer_choices_impacts_based_impacts INTEGER,
            explainer_choices_impacts_based_decision INTEGER,
            explainer_choices_decision_based_total INTEGER,
            explainer_choices_decision_based_forced INTEGER,
            explainer_choices_decision_based_arbitrary INTEGER,
            explainer_choices_decision_based_impacts INTEGER,
            explainer_choices_decision_based_decision INTEGER,
            explainer_choices_hybrid_total INTEGER,
            explainer_choices_hybrid_forced INTEGER,
            explainer_choices_hybrid_arbitrary INTEGER,
            explainer_choices_hybrid_impacts INTEGER,
            explainer_choices_hybrid_decision INTEGER,
            strategy_tree_time REAL,
            initial_bounds TEXT,
            final_bounds TEXT,
            error TEXT,
            frontier_size INTEGER,
            PRIMARY KEY (x, y, w)
        )
    ''')
    ensure_experiments_columns(cursor)
    conn.commit()

    print(str(datetime.now()) + " Starting benchmark...")

    last_time = time.time() + 10

    try:
        for k in range(2, 21):
            for x in range(1, k):
                y = k - x

                if x <= 10 and y <= 10:
                    bundle = read_cpi_bundles(x=x, y=y)

                    if not bundle:
                        s = f"No bundle found for x={x}, y={y}"
                        print(str(datetime.now()) + " " + s)
                        send_telegram_message(s)
                    else:
                        for w in range(0, len(bundle)):
                            single_execution(cursor, conn, x, y, w, bundle, not_use_Ur)

                            if time.time() - last_time > 1:
                                last_time = time.time()
                                send_telegram_message(f"x={x}, y={y}, w={w} Done")

    except Exception as e:
        print(str(datetime.now()) + f" Error during benchmark: {str(e)}")
        conn.rollback()

if __name__ == '__main__':
    arguments = sys.argv[1:]
    not_use_Ur = "--not-use-Ur" in arguments
    print(str(datetime.now()) + " Starting benchmark..." + (" without Ur" if not_use_Ur else " with Ur"))
    run_benchmarks(not_use_Ur=not_use_Ur)
    conn.close()
    print(str(datetime.now()) + " Benchmark completed.")
