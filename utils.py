# utils.py

import json
import os
import datetime

from config import WAR_LOG_PATH


def load_wars():
    if not os.path.exists(WAR_LOG_PATH):
        return {"wars": []}
    with open(WAR_LOG_PATH, "r") as f:
        return json.load(f)


def save_wars(data):
    with open(WAR_LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)


def interpret_roll(result):
    outcomes = {
        1: "Narrow turnout (Lower)",
        2: "Normal turnout (Lower)",
        3: "Critical turnout (Lower)",
        4: "Narrow turnout (Medium)",
        5: "Normal turnout (Medium)",
        6: "Critical turnout (Medium)",
        7: "Narrow turnout (Upper)",
        8: "Normal turnout (Upper)",
        9: "Critical turnout (Upper)",
        10: "Best turnout",
    }
    return outcomes.get(result, "Invalid result")


def normalize_name(name: str) -> str:
    return name.replace("_", " ").lower()


def setup_logging():
    print("🛠 Logging initialized.")
