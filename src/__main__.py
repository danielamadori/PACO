import sys
import subprocess
import threading
import signal
import os
from utils.env import LOG_TO_FILE, LOG_PATH
from utils.logger import log_output, logger


gui_process = None
server_process = None

def print_help():
    help_text = """
Usage: python3 -m src [options]

Options:
    --gui           Launch the GUI (Dash app)
    --api           Launch the API (FastAPI)
    --help          Show this help message
    --log-to-file   Write logs also into logs/paco.log
"""
    print(help_text)
    logger.info("Displayed help message")


def launch_subprocess(label, path):
    logger.info(f"Launching {label}")

    if not os.path.exists(path):
        raise FileNotFoundError(f"{label} not found at {path}")

    output = open(LOG_PATH, "a") if LOG_TO_FILE else subprocess.PIPE

    process = subprocess.Popen(
        [sys.executable, path],
        stdout=output,
        stderr=output,
        cwd=os.getcwd(),
        text=True
    )

    if not LOG_TO_FILE:
        threading.Thread(target=log_output, args=(process.stdout, logger.level, label), daemon=True).start()
        threading.Thread(target=log_output, args=(process.stderr, logger.level, label), daemon=True).start()

    logger.info(f"{label} launched with PID {process.pid}")
    return process



def handle_termination(signum, frame):
    logger.warning(f"Signal {signum} received. Terminating processes...")
    for label, proc in [("GUI", gui_process), ("SERVER", server_process)]:
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                logger.info(f"{label} process terminated successfully (PID {proc.pid})")
            except Exception as e:
                logger.error(f"Error while terminating {label} process: {str(e)}")
    logger.info("Main process exiting cleanly.")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_termination)
signal.signal(signal.SIGINT, handle_termination)


def main():
    global gui_process, server_process
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--log")]

    logger.info("Starting PACO")
    if not args:
        print_help()
        sys.exit(0)

    match args[0]:
        case "--gui":
            gui_process = launch_subprocess("GUI", "gui/src/main.py")
            server_process = launch_subprocess("SERVER",
                                os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py"))
            simulator_process = launch_subprocess("SIMULATOR", "simulator/src/main.py")

        case "--api":
            server_process = launch_subprocess("SERVER",
                                os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py"))
            simulator_process = launch_subprocess("SIMULATOR", "simulator/src/main.py")
        case "--help":
            print_help()
            sys.exit(0)
        case _:
            logger.warning(f"Unknown argument: {args[0]}")
            print_help()
            sys.exit(0)

    logger.info("Waiting for subprocesses to exit...")
    try:
        exit_codes = []
        if server_process:
            exit_codes.append(server_process.wait())
        if gui_process:
            exit_codes.append(gui_process.wait())
        if simulator_process:
            exit_codes.append(simulator_process.wait())
        logger.info(f"Subprocesses exited with codes: {exit_codes}")
    except KeyboardInterrupt:
        handle_termination(signal.SIGINT, None)


if __name__ == "__main__":
    main()