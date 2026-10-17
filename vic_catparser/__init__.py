from vic_catparser.service import CancelledError, ProcessResult, process_vic

__version__ = "2.1"
APP_TITLE = f"Project VIC Category Parser v{__version__}"

__all__ = ["APP_TITLE", "CancelledError", "ProcessResult", "process_vic", "__version__"]
