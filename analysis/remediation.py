import json
import sys
import os
import platform
import subprocess

# 📌 Vérification des arguments
if len(sys.argv) != 2:
    print("Usage: python analysis/remediation.py <prioritized_vulns.json>")
    sys.exit(1)

PRIORITIZED_FILE = sys.argv[1]

if not os.path.exists(PRIORITIZED_FILE):
    print(f"Erreur : Fichier {PRIORITIZED_FILE} introuvable.")
    sys.exit(1)

try:
    with open(PRIORITIZED_FILE, "r") as file:
        prioritized_vulns = json.load(file)
except json.JSONDecodeError:
    print("Erreur : Impossible de parser le fichier JSON.")
    sys.exit(1)

def get_latest_version(pkg_name):
    """Vérifie la dernière version disponible selon l'OS"""
    os_name = platform.system()
    
    if os_name == "Linux":
        try:
            result = subprocess.run(
                ["apt-cache", "policy", pkg_name], capture_output=True, text=True, check=True
            )
            for line in result.stdout.split("\n"):
                if "Candidate:" in line:
                    return line.split(":")[1].strip()
        except subprocess.CalledProcessError:
            pass
    elif os_name == "Alpine":
        return f"apk --no-cache upgrade {pkg_name}"
    elif os_name == "RedHat":
        return f"yum update {pkg_name} -y"
    return None

remediation_suggestions = []

for vuln in prioritized_vulns:
    pkg_name = vuln["Package"]
    fixed_version = get_latest_version(pkg_name) or vuln["FixedVersion"]

    if fixed_version and fixed_version != vuln["InstalledVersion"]:
        remediation_suggestions.append({
            "Package": pkg_name,
            "VulnerabilityID": vuln["VulnerabilityID"],
            "Severity": vuln["Severity"],
            "InstalledVersion": vuln["InstalledVersion"],
            "FixedVersion": fixed_version,
            "Recommendation": f"Mettre à jour {pkg_name} vers {fixed_version}."
        })

REMEDIATION_FILE = "reports/remediation_suggestions.json"
with open(REMEDIATION_FILE, "w") as file:
    json.dump(remediation_suggestions, file, indent=4)

print(f"✅ Remédiation générée : résultats sauvegardés dans {REMEDIATION_FILE}")
