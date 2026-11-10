import time
import random
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"C:\Users\Windows 10\.gemini\antigravity\scratch\linkedin-growth")
IMAGE_PATH = BASE_DIR / "robotics_ai.jpg"

POST_TEXT = """🤖 Les systèmes embarqués et l'IA en temps réel transforment notre vision de l'industrie et de la robotique !

En intégrant des modèles d'Edge AI directement sur des plateformes NVIDIA Jetson et des microcontrôleurs avancés, nous franchissons un nouveau cap :
• Traitement ultra-rapide en Computer Vision à la milliseconde
• Réduction de la dépendance au Cloud pour les environnements industriels
• Convergence matérielle et logicielle pour l'automatisation de pointe

Passionné par les systèmes embarqués, la robotique et les nouvelles technologies. Échangeons sur vos projets et vos innovations ! 🚀

#EmbeddedSystems #Robotics #ComputerVision #EdgeAI #NVIDIA #IndustrialIoT #Innovation"""

def run_automation():
    print("Connexion à Chrome sur le port 9222...")
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        
        # Trouver ou ouvrir l'onglet LinkedIn Feed
        page = None
        for pg in context.pages:
            if "linkedin.com" in pg.url:
                page = pg
                break
        if not page:
            page = context.new_page()
            page.goto("https://www.linkedin.com/feed/")
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3)

        print(f"Page active : {page.title()} ({page.url})")

        # 1. PARTIE PUBLICATION DE POST AVEC PHOTO
        print("\n--- 1. CRÉATION DU POST AVEC PHOTO ---")
        page.goto("https://www.linkedin.com/feed/")
        time.sleep(3)

        # Cliquer sur "Commencer un post" / "Start a post"
        start_post_btn = page.locator("button:has-text('Commencer un post'), button:has-text('Start a post'), button[class*='share-box-feed-entry__trigger']").first
        if start_post_btn.is_visible():
            start_post_btn.click()
            time.sleep(2)

            # Remplir le texte du post
            editor = page.locator("div.ql-editor, div[contenteditable='true'][role='textbox']").first
            editor.fill(POST_TEXT)
            time.sleep(1)

            # Ajouter la photo
            file_input = page.locator("input[type='file'][accept*='image']").first
            if file_input.count() == 0:
                # Cliquer sur l'icône photo si l'input file n'est pas directement présent
                photo_icon = page.locator("button[aria-label*='médias'], button[aria-label*='photo'], button[aria-label*='Add media']").first
                if photo_icon.is_visible():
                    photo_icon.click()
                    time.sleep(1)
                file_input = page.locator("input[type='file']").first

            if file_input.count() > 0 and IMAGE_PATH.exists():
                print(f"Upload de l'image : {IMAGE_PATH}")
                file_input.set_input_files(str(IMAGE_PATH))
                time.sleep(3)

                # Cliquer sur 'Suivant' / 'Next' si présent dans le dialogue média
                next_btn = page.locator("button:has-text('Suivant'), button:has-text('Next')").first
                if next_btn.is_visible():
                    next_btn.click()
                    time.sleep(2)

            # Bouton Publier
            publish_btn = page.locator("button:has-text('Publier'), button:has-text('Post')").filter(has_not_text="Commencer").first
            print("Post prêt ! Prêt pour publication.")
            # publish_btn.click() # Activé dès validation
            print("Post configuré avec succès.")
        else:
            print("Bouton 'Commencer un post' non trouvé sur le flux.")

        # 2. PARTIE DEMANDES DE CONNEXION (25 PROFILS CIBLES SANS MESSAGE)
        print("\n--- 2. DEMANDES DE CONNEXION AUTOMATIQUES ---")
        queries = [
            "Embedded Systems Engineer",
            "Robotics PhD student",
            "Computer Vision Specialist",
            "NVIDIA CUDA Engineer"
        ]

        total_connected = 0
        target_connections = 25

        for query in queries:
            if total_connected >= target_connections:
                break

            search_url = f"https://www.linkedin.com/search/results/people/?keywords={query.replace(' ', '%20')}&origin=SWITCH_SEARCH_VERTICAL"
            print(f"\nRecherche pour : {query}...")
            page.goto(search_url)
            time.sleep(4)

            # Trouver les boutons "Se connecter" ou "Connect"
            connect_buttons = page.locator("button:has-text('Se connecter'), button:has-text('Connect')").all()
            print(f"Boutons de connexion trouvés : {len(connect_buttons)}")

            for btn in connect_buttons:
                if total_connected >= target_connections:
                    break
                try:
                    btn_text = btn.inner_text().strip()
                    if "Se connecter" in btn_text or "Connect" in btn_text:
                        btn.scroll_into_view_if_needed()
                        time.sleep(1)
                        btn.click()
                        time.sleep(1.5)

                        # Si une modale demande d'ajouter une note, cliquer sur "Envoyer sans note" / "Send without a note"
                        send_now_btn = page.locator("button:has-text('Envoyer sans note'), button:has-text('Send without a note'), button:has-text('Envoyer'), button:has-text('Send')").filter(has_not_text="Ajouter").first
                        if send_now_btn.is_visible():
                            send_now_btn.click()
                            time.sleep(1)

                        total_connected += 1
                        print(f"[{total_connected}/{target_connections}] Demande de connexion envoyée !")
                        # Pause humaine aléatoire pour respecter les quotas et éviter les détections
                        time.sleep(random.uniform(2.5, 4.5))
                except Exception as e:
                    print(f"Saut d'un bouton : {e}")
                    continue

        print(f"\nTerminé ! Total connexions envoyées : {total_connected}")

if __name__ == "__main__":
    run_automation()
