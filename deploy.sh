#!/bin/bash

# a0d8dd46-3687-42ab-9a1c-8aefd39d37bf  
# 📌 Définition des variables principales
IMAGE_NAME=${1:-"nginx:latest"}
REPORTS_DIR="reports"
LOGS_DIR="logs"
LOG_FILE="$LOGS_DIR/deploy.log"
DB_FILE="$REPORTS_DIR/cve_database.db"

MERGED_REPORT="$REPORTS_DIR/merged_results.json"
PRIORITIZED_REPORT="$REPORTS_DIR/prioritized_vulns.json"
REMEDIATION_REPORT="$REPORTS_DIR/remediation_suggestions.json"

# 📂 Création des dossiers nécessaires
mkdir -p $REPORTS_DIR $LOGS_DIR

# 📝 Fonction pour journaliser les événements
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# 🚀 Vérification des outils disponibles
check_tool() {
    command -v $1 >/dev/null 2>&1
}

# 📌 Installation des dépendances Python si nécessaire
pip install -r requirements.txt > /dev/null 2>&1

# 📌 Initialisation des rapports de scan
SCAN_REPORTS=()

# 🔍 Fonction pour exécuter les scans de sécurité
run_scan() {
    local scanner=$1
    local script=$2
    local output_file="$REPORTS_DIR/${scanner}_scan_${IMAGE_NAME//:/_}.json"

    if check_tool "$scanner"; then
        log "🔍 Lancement du scan avec $scanner..."
        if python3 "$script" "$IMAGE_NAME"; then
            log "✅ Scan $scanner terminé avec succès."
            SCAN_REPORTS+=("$output_file")
        else
            log "⚠️ Scan $scanner a échoué, on continue."
        fi
    else
        log "⚠️ $scanner n'est pas installé, le scan est ignoré."
    fi
}

log "🚀 Déploiement du scan de sécurité pour l'image : $IMAGE_NAME"

# 🔍 Lancer les scans avec Trivy, Clair et Grype
run_scan "trivy" "scanners/trivy_scan.py"
run_scan "clairctl" "scanners/clair_scan.py"
run_scan "grype" "scanners/grype_scan.py"

# 🚨 Vérification des scans exécutés
if [ ${#SCAN_REPORTS[@]} -eq 0 ]; then
    log "❌ Aucun scan n'a pu être exécuté. Arrêt du processus."
    exit 1
fi

# 🔄 Fusion des résultats (uniquement ceux disponibles)
log "🔄 Fusion des résultats disponibles..."
if python3 analysis/merge.py "${SCAN_REPORTS[@]}"; then
    log "✅ Fusion des résultats terminée."
else
    log "⚠️ Erreur lors de la fusion des résultats, on continue."
fi

# ⚖️ Priorisation des vulnérabilités
log "⚖️ Priorisation des vulnérabilités..."
if python3 analysis/prioritize_vulns.py "$MERGED_REPORT"; then
    log "✅ Priorisation terminée."
else
    log "⚠️ Erreur lors de la priorisation, on continue."
fi

# 🛠 Remédiation automatique
log "🛠 Génération des remédiations..."
if python3 analysis/remediation.py "$PRIORITIZED_REPORT"; then
    log "✅ Remédiation générée avec succès."
else
    log "⚠️ Erreur lors de la génération des remédiations, on continue."
fi

# 🔄 Initialisation de la base de données des CVE
log "📂 Vérification et initialisation de la base de données des CVE..."
if [ ! -f "$DB_FILE" ]; then
    python3 database/database.py
    log "✅ Base de données CVE initialisée."
else
    log "✅ Base de données CVE déjà existante."
fi

# 🔍 Mise à jour des descriptions et références des CVE
log "🔍 Mise à jour des informations CVE..."
if python3 database/update_info_sup.py; then
    log "✅ Mise à jour des informations CVE terminée."
else
    log "⚠️ Erreur lors de la mise à jour des informations CVE, on continue."
fi

# 📊 Lancement du tableau de bord Flask
log "📊 Démarrage du tableau de bord Flask..."
if nohup python3 web_dashboard/app.py > /dev/null 2>&1 & then
    log "✅ Tableau de bord disponible sur http://127.0.0.1:5000"
else
    log "⚠️ Erreur lors du démarrage du tableau de bord Flask."
fi

log "✅ Processus terminé ! 📂 Résultats disponibles dans le dossier reports/"
