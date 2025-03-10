import json
import sys
import os

# 📌 Vérification des arguments
if len(sys.argv) < 2:
    print("Usage: python analysis/merge.py <trivy_report.json> <clair_report.json> <grype_report.json>")
    sys.exit(1)

REPORT_FILES = sys.argv[1:]

# 🔍 Vérification des fichiers existants
valid_reports = [report for report in REPORT_FILES if os.path.exists(report)]

if not valid_reports:
    print("❌ Aucun fichier valide trouvé pour la fusion. Vérifiez que les scans ont bien généré des rapports.")
    sys.exit(1)

# 📊 Chargement des rapports
merged_results = {}

for report in valid_reports:
    try:
        with open(report, "r") as file:
            scan_data = json.load(file)
    except json.JSONDecodeError:
        print(f"⚠️ Erreur : Impossible de parser {report}, fichier ignoré.")
        continue

    for result in scan_data.get("Results", []):
        if "Vulnerabilities" in result:
            for vuln in result["Vulnerabilities"]:
                pkg_name = vuln["PkgName"]
                vuln_id = vuln["VulnerabilityID"]
                severity = vuln["Severity"]
                installed_version = vuln["InstalledVersion"]
                fixed_version = vuln.get("FixedVersion", "N/A")

                if pkg_name not in merged_results:
                    merged_results[pkg_name] = []

                # Ajout des sources de scan pour cross-check
                vuln_entry = {
                    "VulnerabilityID": vuln_id,
                    "Severity": severity,
                    "InstalledVersion": installed_version,
                    "FixedVersion": fixed_version,
                    "Source": os.path.basename(report)
                }

                # Éviter les doublons
                if not any(v["VulnerabilityID"] == vuln_id for v in merged_results[pkg_name]):
                    merged_results[pkg_name].append(vuln_entry)

# 📁 Sauvegarde du JSON fusionné
MERGED_FILE = "reports/merged_results.json"
with open(MERGED_FILE, "w") as file:
    json.dump(merged_results, file, indent=4)

print(f"✅ Fusion terminée : résultats sauvegardés dans {MERGED_FILE}")
