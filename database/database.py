import sqlite3
import json

DB_FILE = "reports/cve_database.db"

def init_db():
    """Initialise la base de données pour stocker les informations des CVE"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cve_info (
            cve_id TEXT PRIMARY KEY,
            description TEXT,
            reference_links TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def insert_cve(cve_id, description, references):
    """Ajoute une CVE à la base de données"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO cve_info (cve_id, description, reference_links) 
        VALUES (?, ?, ?)
    """, (cve_id, description, json.dumps(references)))
    
    conn.commit()
    conn.close()

def get_cve(cve_id):
    """Récupère les informations d'une CVE depuis la base"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT description, reference_links FROM cve_info WHERE cve_id = ?", (cve_id,))
    row = cursor.fetchone()
    
    conn.close()
    if row:
        return {"description": row[0], "references": json.loads(row[1])}
    return None

if __name__ == "__main__":
    init_db()
    print("✅ Base de données CVE initialisée.")
