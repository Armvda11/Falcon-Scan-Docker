from flask import Flask, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Chemin du dossier `web_dashboard`
DB_FILE = os.path.join(BASE_DIR, "../reports/cve_database.db")

@app.route("/")
def index():
    return render_template("index.html")

# 📌 Correction API : Récupérer la sévérité depuis la base
@app.route("/api/severity")
def get_severity_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            SUM(CASE WHEN severity = 'CRITICAL' THEN 1 ELSE 0 END) AS critical,
            SUM(CASE WHEN severity = 'HIGH' THEN 1 ELSE 0 END) AS high,
            SUM(CASE WHEN severity = 'MEDIUM' THEN 1 ELSE 0 END) AS medium,
            SUM(CASE WHEN severity = 'LOW' THEN 1 ELSE 0 END) AS low
        FROM cve_info
    """)

    data = cursor.fetchone()
    conn.close()

    print(f"🔍 Résultat SQL : {data}")

    return jsonify({
        "CRITICAL": data[0] or 0,
        "HIGH": data[1] or 0,
        "MEDIUM": data[2] or 0,
        "LOW": data[3] or 0
    })

if __name__ == "__main__":
    app.run(debug=True)
