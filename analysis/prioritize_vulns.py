import json
import sys
import os
#objectif classer les vulnérabilités par priorité

# 📌 Vérification des arguments
if len(sys.argv) != 2:
    print("Usage: python analysis/prioritize_vulns.py <merged_results.json>")
    sys.exit(1)

MERGED_FILE = sys.argv[1]

# 📂 Vérification du fichier
if not os.path.exists(MERGED_FILE):
    print(f"Erreur : Fichier {MERGED_FILE} introuvable.")
    sys.exit(1)

# 🔍 Chargement des vulnérabilités fusionnées
try:
    with open(MERGED_FILE, "r") as file:
        vulnerabilities = json.load(file)
except json.JSONDecodeError:
    print("Erreur : Impossible de parser le fichier JSON.")
    sys.exit(1)

# 📊 Définition des priorités avec pondération CVSS
severity_rank = {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 4
}

prioritized_vulns = []

for pkg, vulns in vulnerabilities.items():
    for vuln in vulns:
        severity = vuln["Severity"]
        cvss_score = vuln.get("CVSSv3", vuln.get("CVSSv2", 0))  # Utiliser CVSS v3, sinon v2
        priority_score = severity_rank.get(severity, 5) + (10 - cvss_score) / 10  # Pondération

        prioritized_vulns.append({
            "Package": pkg,
            "VulnerabilityID": vuln["VulnerabilityID"],
            "Severity": severity,
            "PriorityScore": round(priority_score, 2),
            "InstalledVersion": vuln["InstalledVersion"],
            "FixedVersion": vuln["FixedVersion"]
        })

# 📌 Tri des vulnérabilités par priorité
prioritized_vulns.sort(key=lambda x: x["PriorityScore"])

# 📁 Sauvegarde des vulnérabilités priorisées
PRIORITIZED_FILE = "reports/prioritized_vulns.json"
with open(PRIORITIZED_FILE, "w") as file:
    json.dump(prioritized_vulns, file, indent=4)

print(f"✅ Priorisation terminée : résultats sauvegardés dans {PRIORITIZED_FILE}")
