import json
import os
import datetime
import discord
from discord import app_commands


WAR_LOG_PATH = "warlog.json"


def load_wars():
    if not os.path.exists(WAR_LOG_PATH):
        return {"wars": []}
    with open(WAR_LOG_PATH, "r") as f:
        return json.load(f)


def save_wars(data):
    with open(WAR_LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)
