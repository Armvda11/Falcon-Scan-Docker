import requests
import sqlite3
import time
import os

# 📌 URL de l'API NVD (NOUVELLE VERSION)
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_API_KEY = os.getenv("NVD_API_KEY")  # Récupération de la clé API depuis les variables d'environnement

DB_FILE = "reports/cve_database.db"

# 🔍 Fonction pour récupérer les informations d'une CVE
def fetch_cve_info(cve_id):
    """Récupère les détails d'une CVE depuis l'API NVD"""
    headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}  # Utilisation de la clé API si disponible
    params = {"cveId": cve_id}

    try:
        response = requests.get(NVD_API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Vérifier si la CVE existe dans la réponse
        if "vulnerabilities" in data and len(data["vulnerabilities"]) > 0:
            cve_data = data["vulnerabilities"][0]["cve"]

            # Récupération de la description
            description = cve_data["descriptions"][0]["value"]

            # Récupération des références
            references = [ref["url"] for ref in cve_data["references"]]

            return description, references
        else:
            print(f"⚠️ CVE {cve_id} non trouvée dans la base NVD.")
            return "Description non disponible", []
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erreur lors de la récupération de {cve_id} : {e}")
        return "Description non disponible", []

# 📌 Connexion à la base SQLite
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# 📌 Récupération des CVE à mettre à jour
cursor.execute("SELECT cve_id FROM cve_info WHERE description = 'Description non disponible'")
cve_list = [row[0] for row in cursor.fetchall()]

print(f"🔍 Mise à jour de {len(cve_list)} CVE non renseignées...\n")

# 📌 Boucle pour récupérer les informations et mettre à jour la base de données
for cve in cve_list:
    desc, refs = fetch_cve_info(cve)
    cursor.execute(
        "UPDATE cve_info SET description = ?, reference_links = ? WHERE cve_id = ?",
        (desc, str(refs), cve)
    )
    conn.commit()
    print(f"✅ CVE {cve} mise à jour.")

    # Pause pour éviter le rate-limiting
    time.sleep(1.5)

conn.close()
print("\n✅ Mise à jour complète des CVE en base.")
