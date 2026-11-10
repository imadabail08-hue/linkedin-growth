"""
LinkedIn Daily Runner (Production Finale avec Recommandations 1, 2, 4, 5)
========================================================================
- Vérification Week-end / Jours Fériés (Recommandation 5)
- Récupération Dynamique ArXiv / IEEE / NVIDIA (Recommandation 1)
- Bibliothèque de Recyclage intelligent Top Posts (Recommandation 4)
- Démarrage automatique sans intervention manuelle (Recommandation 2)
"""

import sys
import time
import random
import argparse
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"C:\Users\Windows 10\.gemini\antigravity\scratch\linkedin-growth")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Imports des modules d'amélioration
from holiday_checker import is_holiday_or_weekend
from dynamic_content_curator import generate_dynamic_post
from repurpose_engine import get_post_ready_for_repurpose, log_post_performance

TARGET_QUERIES = [
    "Embedded Systems Engineer Maroc",
    "Embedded Systems Engineer",
    "Robotics PhD",
    "Computer Vision Engineer",
    "NVIDIA Jetson Specialist",
    "Industrial IoT Engineer"
]

def download_image(url: str, filename: str) -> Path | None:
    img_path = BASE_DIR / filename
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            img_path.write_bytes(resp.content)
            print(f"✅ Image téléchargée : {filename}")
            return img_path
    except Exception as e:
        print(f"⚠️ Erreur téléchargement image : {e}")
    return None

def publish_post(page, post_data: dict):
    print(f"\n📝 --- PUBLICATION : {post_data['title']} ---")
    img_path = download_image(post_data["image_url"], post_data["image_name"])

    page.goto("https://www.linkedin.com/feed/")
    page.wait_for_load_state("domcontentloaded")
    time.sleep(3)

    create_btn = page.locator("button:has-text('Create a post'), button:has-text('Start a post'), p:has-text('Start a post')").first
    if not create_btn.is_visible():
        create_btn = page.locator("div:has-text('Start a post')").last

    if not create_btn.is_visible():
        print("❌ Bouton 'Create a post' non trouvé.")
        return False

    create_btn.click()
    time.sleep(2)

    # Attacher l'image
    if img_path and img_path.exists():
        media_btn = page.locator("button[aria-label='Media'], button[aria-label='médias']").first
        if media_btn.is_visible():
            try:
                with page.expect_file_chooser(timeout=7000) as fc_info:
                    media_btn.click()
                    fc = fc_info.value
                    fc.set_files(str(img_path))
                    print(f"📸 Image attachée : {img_path.name}")
                    time.sleep(3)

                    next_btn = page.locator("button:has-text('Next'), button:has-text('Suivant')").first
                    if next_btn.is_visible():
                        next_btn.click()
                        time.sleep(2)
                        print("✅ Étape image validée.")
            except Exception as e:
                print(f"⚠️ Erreur upload image : {e}")

    # Rédiger le texte enrichi
    editor = page.locator("div.ql-editor, div[role='textbox'][contenteditable='true']").first
    if editor.is_visible():
        editor.click()
        editor.fill(post_data["text"])
        time.sleep(2)
        print("✅ Contenu technique, sources et crédits insérés.")

    # Publier
    post_btn = page.locator("button:has-text('Post'), button:has-text('Publier')").filter(has_not_text="Create").filter(has_not_text="Commencer").first
    if post_btn.is_visible() and post_btn.is_enabled():
        post_btn.click()
        print("🚀 POST PUBLIÉ AVEC SUCCÈS SUR LINKEDIN !")
        time.sleep(5)
        return True
    else:
        print("⚠️ Bouton Post indisponible.")
        return False

def send_auto_connections(page, total_target=13):
    print(f"\n👥 --- ENVOI DE {total_target} DEMANDES DE CONNEXION ---")
    connected = 0

    for query in TARGET_QUERIES:
        if connected >= total_target:
            break

        url = f"https://www.linkedin.com/search/results/people/?keywords={query.replace(' ', '%20')}&origin=SWITCH_SEARCH_VERTICAL"
        print(f"\n🔍 Recherche : '{query}'")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)

        invite_links = page.locator("a[aria-label*='Invite'], button[aria-label*='Invite']").all()
        print(f"Trouvé {len(invite_links)} profils sur cette page.")

        for link in invite_links:
            if connected >= total_target:
                break
            try:
                label = link.get_attribute("aria-label") or "Profil"
                link.scroll_into_view_if_needed()
                time.sleep(0.8)
                link.click()
                time.sleep(1.5)

                send_no_note = page.locator("button:has-text('Send without a note'), button:has-text('Envoyer sans note'), button:has-text('Send'), button:has-text('Envoyer')").filter(has_not_text="Add").filter(has_not_text="Ajouter").first
                if send_no_note.is_visible():
                    send_no_note.click()
                    time.sleep(1)

                connected += 1
                print(f"  [{connected}/{total_target}] Connexion envoyée à : {label}")
                time.sleep(random.uniform(2.5, 4.0))
            except Exception:
                continue

    print(f"\n🎉 Connexions envoyées pour ce créneau : {connected}/{total_target}")
    return connected

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Growth Full Runner")
    parser.add_argument("--slot", choices=["morning", "noon"], default="morning", help="Créneau (morning=8h, noon=12h)")
    args = parser.parse_args()

    print("=" * 65)
    print(f"🤖 WORKFLOW LINKEDIN AUTO (v2.0) — CRÉNEAU : {args.slot.upper()}")
    print("=" * 65)

    # 1. Vérification Vacances / Jours Fériés (Recommandation 5)
    is_paused, reason = is_holiday_or_weekend()
    if is_paused:
        print(f"🛑 REPOS / PAUSE RÉSEAU : {reason}")
        print("Aucune publication ni connexion pour préserver le taux d'engagement.")
        return

    # 2. Préparation du Post (Recommandation 1 & 4)
    # Vérifier d'abord s'il y a un ancien post à recycler (repurposing)
    repurposed_post = get_post_ready_for_repurpose()
    if repurposed_post:
        print("♻️ Recyclage d'un post à fort engagement antérieur !")
        post_data = {
            "title": f"Post Recyclé ({args.slot.capitalize()})",
            "text": repurposed_post["text"],
            "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80",
            "image_name": "repurposed_post.jpg"
        }
    else:
        # Génération dynamique ArXiv / IEEE / NVIDIA
        post_data = generate_dynamic_post(slot=args.slot)

    connections_target = 13 if args.slot == "morning" else 12

    # 3. Pilotage Chrome via CDP
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        publish_post(page, post_data)
        send_auto_connections(page, total_target=connections_target)

    print(f"\n✅ EXÉCUTION DU CRÉNEAU {args.slot.upper()} TERMINÉE AVEC SUCCÈS !")

if __name__ == "__main__":
    main()
