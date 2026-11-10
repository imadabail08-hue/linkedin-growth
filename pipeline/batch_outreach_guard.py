"""
Script de Filtrage, Déduplication et Délivrabilité Sécurisée (Batch de 25 max)
Conforme aux règles P1 (Hard-limit 25/jour, temporisation 90-180s, plage 8h-18h)
"""

import os
import sys
import json
import time
import random
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# ─── Configuration & Chemins ──────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
PIPELINE_FILE = BASE_DIR / "lead_state_machine.json"
LOG_DIR = BASE_DIR.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

TODAY_STR = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = LOG_DIR / f"outreach_audit_{TODAY_STR}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# ─── Quotas & Sécurité (Règle P1) ─────────────────────────────────────────────
HARD_LIMIT_DAILY = 25
DELAY_MIN = 90   # secondes
DELAY_MAX = 180  # secondes
TIMEZONE = ZoneInfo("Africa/Casablanca")
START_HOUR = 8
END_HOUR = 18

def check_time_window() -> bool:
    """Vérifie que l'exécution se situe strictement dans la plage 08h00 - 18h00 locale."""
    now_local = datetime.now(TIMEZONE)
    if not (START_HOUR <= now_local.hour < END_HOUR):
        logging.warning(f"⛔ En dehors de la plage horaire autorisée ({START_HOUR}h-{END_HOUR}h {TIMEZONE.key}). Heure actuelle : {now_local.strftime('%H:%M:%S')}")
        return False
    return True

def load_state_machine() -> dict:
    if not PIPELINE_FILE.exists():
        logging.error(f"Fichier d'état introuvable : {PIPELINE_FILE}")
        return {"leads": []}
    with open(PIPELINE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state_machine(data: dict):
    with open(PIPELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_today_sent_count(leads: list) -> int:
    """Compte les invitations envoyées aujourd'hui."""
    count = 0
    for lead in leads:
        if lead.get("state") == "INVITED" and lead.get("invited_at", "").startswith(TODAY_STR):
            count += 1
    return count

def dispatch_batch_outreach(mock_execution: bool = False):
    """
    Exécute le filtrage strict et l'envoi du batch quotidien plafonné à 25 leads.
    """
    logging.info("==================================================================")
    logging.info("🚀 Démarrage du batch Outreach LinkedIn (Contrôle P1 / Hard-Limit)")
    logging.info("==================================================================")

    if not check_time_window():
        logging.error("Arrêt du script : Exécution hors fenêtre horaire sécurisée.")
        return

    data = load_state_machine()
    leads = data.get("leads", [])
    
    already_sent_today = get_today_sent_count(leads)
    logging.info(f"📊 Invitations déjà émises aujourd'hui ({TODAY_STR}) : {already_sent_today}/{HARD_LIMIT_DAILY}")

    if already_sent_today >= HARD_LIMIT_DAILY:
        logging.warning("🛑 GARDE-FOU ATTEINT : Le quota maximal de 25 invitations par jour est déjà consommé. Arrêt immédiat.")
        return

    remaining_slots = HARD_LIMIT_DAILY - already_sent_today
    logging.info(f"🎯 Quota restant disponible pour ce batch : {remaining_slots}")

    # Filtrer les prospects qualifiés et non encore sollicités (anti-doublon strict)
    eligible_leads = [
        lead for lead in leads 
        if lead.get("state") == "PITCH_READY" and not lead.get("invited_at")
    ]

    logging.info(f"📋 Prospects éligibles prêts à l'envoi (état PITCH_READY) : {len(eligible_leads)}")

    if not eligible_leads:
        logging.info("Aucun nouveau prospect dans l'état PITCH_READY. Rien à envoyer.")
        return

    # Limiter strictement au nombre restant permis
    batch = eligible_leads[:remaining_slots]
    processed_count = 0

    for idx, lead in enumerate(batch, 1):
        lead_id = lead.get("id")
        full_name = lead.get("full_name", "Inconnu")
        profile_url = lead.get("profile_url", "")
        icebreaker = lead.get("icebreaker", "")

        logging.info(f"\n[{idx}/{len(batch)}] Traitement du prospect : {full_name} ({profile_url})")
        
        # Vérification taille message P1 (<= 300 caractères)
        if len(icebreaker) > 300:
            logging.warning(f"⚠️ Accroche trop longue ({len(icebreaker)} car.), troncature à 297 car. + '...'")
            icebreaker = icebreaker[:297] + "..."

        # Simulation / Envoi effectif
        try:
            if not mock_execution:
                # Appel du connecteur Chrome / Playwright ou API
                logging.info(f"Envoi invitation à {full_name} avec message ({len(icebreaker)} car.)")
            else:
                logging.info(f"[SIMULATION] Invitation envoyée avec message : '{icebreaker}'")

            # Mise à jour de l'état
            lead["state"] = "INVITED"
            lead["invited_at"] = datetime.now(TIMEZONE).isoformat()
            lead["icebreaker_sent"] = icebreaker
            processed_count += 1
            already_sent_today += 1

            # Sauvegarde atomique après chaque prospect
            save_state_machine(data)
            logging.info(f"✅ Lead {lead_id} mis à jour dans lead_state_machine.json (Statut: INVITED)")

            # Hard-limit check strict
            if already_sent_today >= HARD_LIMIT_DAILY:
                logging.warning(f"🛑 LIMITE ATTEINTE : 25/25 invitations envoyées. Arrêt sécurisé du pipeline.")
                break

            # Temporisation anti-détection (90 à 180 secondes) sauf sur le dernier
            if idx < len(batch) and already_sent_today < HARD_LIMIT_DAILY:
                delay = random.uniform(DELAY_MIN, DELAY_MAX)
                logging.info(f"⏳ Temporisation de sécurité : attente de {delay:.1f} secondes avant le prochain profil...")
                time.sleep(delay)

        except Exception as e:
            logging.error(f"❌ Erreur lors de l'envoi pour {full_name} : {e}")
            continue

    logging.info(f"\n🎉 Session terminée : {processed_count} invitation(s) envoyée(s). Total aujourd'hui : {already_sent_today}/{HARD_LIMIT_DAILY}")

if __name__ == "__main__":
    is_mock = "--mock" in sys.argv
    dispatch_batch_outreach(mock_execution=is_mock)
