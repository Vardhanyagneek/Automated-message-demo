import csv
import os
from datetime import datetime

LOG_FILE = "results.csv"
FIELDS = ["timestamp", "name", "phone", "status", "detail"]


def log_result(name, phone, status, detail=""):
    new_file = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(FIELDS)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name, phone, status, detail,
        ])