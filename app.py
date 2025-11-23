from flask import Flask, request, jsonify, render_template_string
import sqlite3
import datetime
import os

app = Flask(__name__)

DB_FILE = "records.db"

# -------------------------------
# DB 초기화 (학교 포함)
# -------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school TEXT NOT NULL,
            name TEXT NOT NULL,
            record REAL NOT NULL,
            diff REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------------------------------
# 기록 저장 API
# -------------------------------
@app.post("/api/save_record")
def save_record():
    data = request.get_json()
    school = data.get("school")
    name = data.get("name")
    record = data.get("record")
    diff = data.get("diff")

    if not school or not name or record is None or diff is None:
        return jsonify({"error": "Invalid data"}), 400

    # 이름란에 '초기화' 입력 시 랭킹 초기화
    if name.strip() == "초기화":
        return reset_records()

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO records (school, name, record, diff, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (school, name, record, diff, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return jsonify({"message": "Record saved!"}), 200

# -------------------------------
# 랭킹 초기화 API
# -------------------------------
@app.post("/api/reset_records")
def reset_records():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM records")
    conn.commit()
    conn.close()
    return jsonify({"message": "All records cleared!"})

# -------------------------------
# 랭킹 조회 API
# -------------------------------
ranking_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>10초 게임 랭킹</title>
<style>
body { font-family: Arial, sans-serif; background: #f9f9f9; padding: 40px; text-align: center; }
h1 { margin-bottom: 20px; }
table { width: 80%; margin: auto; border-collapse: collapse; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
th, td { padding: 12px; border-bottom: 1px solid #ddd; font-size: 18px; }
th { background: #3b82f6; color: white; }
tr:nth-child(even) { background: #f0f7ff; }
</style>
</head>
<body>
<h1>10초 맞추기 게임 랭킹 TOP 20</h1>
<table>
<tr>
<th>순위</th>
<th>학교</th>
<th>이름</th>
<th>기록(초)</th>
<th>오차(초)</th>
<th>날짜</th>
</tr>
{% for row in records %}
<tr>
<td>{{ loop.index }}</td>
<td>{{ row[1] }}</td>
<td>{{ row[2] }}</td>
<td>{{ "%.3f"|format(row[3]) }}</td>
<td>{{ "%.3f"|format(row[4]) }}</td>
<td>{{ row[5][:10] }}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

@app.get("/ranking")
def ranking():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM records
        ORDER BY diff ASC
        LIMIT 20
    """)
    rows = cur.fetchall()
    conn.close()
    return render_template_string(ranking_html, records=rows)

# -------------------------------
# TOP20 JSON 조회 API
# -------------------------------
@app.get("/api/get_top20")
def get_top20():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM records
        ORDER BY diff ASC
        LIMIT 20
    """)
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "school": r[1],
            "name": r[2],
            "record": r[3],
            "diff": r[4],
            "created_at": r[5]
        })
    return jsonify(result), 200

# -------------------------------
# 홈 페이지
# -------------------------------
@app.get("/")
def home():
    return "<h2>10초 게임 서버 작동 중! /ranking 에서 TOP20 랭킹 확인</h2>"

# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
