import logging
import sys
import traceback


def setup_logger(name: str) -> logging.Logger:
    """
    Creates or returns a module-level logger configured in a simple,
    script-friendly format. This maintains compatibility with your
    original print-based behavior while using standard logging.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


def status(message: str) -> None:
    """
    Single-line status updates, similar to your original:
        print("Status: <message>", end="\\r")
    Useful for progress indicators in the terminal.
    """
    sys.stdout.write(f"Status: {message}\r")
    sys.stdout.flush()


def info(message: str) -> None:
    """
    Lightweight print-style info output.
    Legacy compatibility for parts of the system that expected print().
    """
    print(message)


def error(message: str, exception: Exception = None) -> None:
    """
    Print an error message plus traceback when applicable.
    Mirrors your original error print behavior.
    """
    print(f"Error: {message}")

    if exception:
        traceback.print_exc()
