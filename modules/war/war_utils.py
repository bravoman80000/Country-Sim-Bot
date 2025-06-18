import json
import os

# Use absolute path for Railway compatibility
WAR_LOG_PATH = "/data/warlog.json"

def load_wars():
    """Loads wars from the JSON file. Returns an empty list if the file does not exist."""
    if not os.path.exists(WAR_LOG_PATH):
        return {"wars": []}
    with open(WAR_LOG_PATH, "r") as f:
        return json.load(f)

def save_wars(data):
    """Saves wars to the JSON file in a nicely formatted way."""
    with open(WAR_LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)
