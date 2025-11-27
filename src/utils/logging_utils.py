import sys
import traceback


def status(message: str) -> None:
    """
    Replicates your original status print behavior:

    print("Status: <message>", end="\\r")

    This provides a single-line updating status indicator in the terminal.
    """
    sys.stdout.write(f"Status: {message}\r")
    sys.stdout.flush()


def info(message: str) -> None:
    """
    Standard print wrapper for normal informational output.
    Mirrors your script's use of plain print() without extra formatting.
    """
    print(message)


def error(message: str, exception: Exception = None) -> None:
    """
    Print error messages the same way your script did using print().

    If an exception is provided, print the traceback (as your script did via print).
    """
    print(f"Error: {message}")

    if exception:
        traceback.print_exc()
