import subprocess
import json
import sys
import os

# Vérification des arguments
if len(sys.argv) != 2:
    print("Usage: python scanners/clair_scan.py <image-docker>")
    sys.exit(1)

IMAGE = sys.argv[1]
OUTPUT_DIR = "reports"
REPORT_FILE = os.path.join(OUTPUT_DIR, f"clair_scan_{IMAGE.replace(':', '_')}.json")

# 📂 Création du dossier de sortie
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Vérification si Clair est installé
try:
    subprocess.run(["clairctl", "version"], check=True, capture_output=True, text=True)
except FileNotFoundError:
    print("❌ Erreur : Clair n'est pas installé. Installez-le avant d'exécuter ce script.")
    sys.exit(1)

print(f"🔍 Scanning Docker image: {IMAGE} with Clair...\n")

# Exécution de Clair
try:
    result = subprocess.run(
        ["clairctl", "analyze", "--json", IMAGE],
        capture_output=True,
        text=True,
        check=True
    )
    with open(REPORT_FILE, "w") as file:
        file.write(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"❌ Erreur lors de l'exécution de Clair: {e.stderr}")
    sys.exit(1)

print(f"\n📁 Rapport JSON sauvegardé dans : {REPORT_FILE}")
