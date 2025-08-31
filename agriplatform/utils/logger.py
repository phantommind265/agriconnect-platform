import json
from datetime import datetime
import os

LOG_FILE = "logs/usage_logs.json"

def log_event(user, action, details=None):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    entry = {
            "user": user or "anonymous",
            "action": action,
            "details": details,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

    #append log
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecoderError:
                logs = []

    logs.append(entry)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)
