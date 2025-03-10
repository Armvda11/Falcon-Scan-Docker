import subprocess
import json
import sys
import os

# 📌 Vérification des arguments
if len(sys.argv) != 2:
    print("Usage: python scanners/trivy_scan.py <image-docker>")
    sys.exit(1)

IMAGE = sys.argv[1]
OUTPUT_DIR = "reports"
INFO_FILE = os.path.join(OUTPUT_DIR, "info_sup.json")
REPORT_FILE = os.path.join(OUTPUT_DIR, f"trivy_scan_{IMAGE.replace(':', '_')}.json")

# 📂 Création des dossiers si inexistants
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🔍 Vérification et chargement du fichier d'infos supplémentaires
if os.path.exists(INFO_FILE):
    with open(INFO_FILE, "r") as f:
        info_sup = json.load(f)
else:
    info_sup = {}

print(f"🔍 Scanning Docker image: {IMAGE} with Trivy...\n")

# 📌 Exécution de Trivy
try:
    result = subprocess.run(
        ["trivy", "image", "--format", "json", "--output", REPORT_FILE, IMAGE],
        capture_output=True,
        text=True,
        check=True
    )
except subprocess.CalledProcessError as e:
    print(f"❌ Erreur lors de l'exécution de Trivy: {e.stderr}")
    sys.exit(1)

# 📌 Lecture du fichier JSON généré
try:
    with open(REPORT_FILE, "r") as file:
        scan_results = json.load(file)
except json.JSONDecodeError:
    print("❌ Erreur lors du parsing du fichier JSON.")
    sys.exit(1)

# 📌 Stockage des vulnérabilités détectées
vulnerabilities = {}

for result in scan_results.get("Results", []):
    if "Vulnerabilities" in result:
        for vuln in result["Vulnerabilities"]:
            cve_id = vuln["VulnerabilityID"]
            pkg_name = vuln["PkgName"]
            severity = vuln["Severity"]
            installed_version = vuln["InstalledVersion"]

            if cve_id not in vulnerabilities:
                vulnerabilities[cve_id] = {
                    "Package": pkg_name,
                    "Severity": severity,
                    "InstalledVersion": installed_version
                }

            # Ajout automatique d'une entrée dans info_sup.json si elle n'existe pas
            if cve_id not in info_sup:
                info_sup[cve_id] = {"description": "Description non disponible", "references": []}

# 📁 Mise à jour du fichier info_sup.json
with open(INFO_FILE, "w") as f:
    json.dump(info_sup, f, indent=4)

# 🔴 Affichage des vulnérabilités
for cve_id, details in vulnerabilities.items():
    print(f"- {cve_id} | {details['Package']} | Version: {details['InstalledVersion']} | Sévérité: {details['Severity']}")
    print("  🔗 Plus d'infos disponibles dans reports/info_sup.json")

print(f"\n📁 Rapport JSON sauvegardé dans : {REPORT_FILE}")
