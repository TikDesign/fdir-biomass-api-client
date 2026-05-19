"""
modules/logger.py
Enkel logging til konsoll + fil, og JSON-lagring til output/.
"""

import json
import os
from datetime import datetime

LOG_FILE = "output/run.log"


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _write(level: str, message: str):
    line = f"[{_ts()}] [{level}] {message}"
    print(line)
    os.makedirs("output", exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def log_info(message: str):
    _write("INFO ", message)


def log_error(message: str):
    _write("ERROR", message)


def save_json(data: dict, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
