from flask import Flask, request, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)

CSV_FILE = "rank.csv"

# CSV 파일 없으면 생성 (school 제거 버전)
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "name", "time"])


@app.route("/", methods=["GET"])
def home():
    return "Ranking server is running."


@app.route("/ranking", methods=["POST"])
def ranking():
    data = request.json
    name = data.get("name")
    time = data.get("time")

    if not name or not time:
        return jsonify({"status": "error", "message": "Missing name or time"}), 400

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, name, time])

    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
