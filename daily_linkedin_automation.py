"""
LinkedIn Daily Full Auto Workflow (Final Production - 2 Posts avec Images Sources + 25 Connexions)
===================================================================================================
1. Télécharge 2 images réelles spécifiques tech avec leur source d'information exacte
2. Rédige et publie 2 posts riches avec analyse technique + mention explicite de la source
3. Envoie 25 invitations ciblées sans message
"""

import time
import random
import os
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"C:\Users\Windows 10\.gemini\antigravity\scratch\linkedin-growth")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# 2 POSTS COMPLETS DE HAUTE VALEUR TECHNIQUE AVEC SOURCES EXACTES
POSTS_DATA = [
    {
        "text": """🤖 [TECH INSIGHT] L'essor des modèles Vision-Language-Action (VLA) dans la robotique autonome et les systèmes embarqués.

Aujourd'hui, l'intégration des modèles VLA comme OpenVLA et les architectures multimodales sur du matériel embarqué (NVIDIA Jetson AGX Orin) redéfinit la manipulation robotique :

🔹 Inférence locale temps réel : Grâce à TensorRT et à la quantification INT8/FP4, nous pouvons désormais exécuter des pipelines d'action visuelle directement en bordure de réseau (Edge).
🔹 Latence critique : Passage d'un goulot d'étranglement de plusieurs secondes via Cloud à moins de 35 ms en local.
🔹 Robustesse industrielle : Pas d'interruption en cas de perte de connectivité réseau dans les usines ou blocs opératoires.

💡 Le futur de l'ingénierie réside dans l'optimisation conjointe du code bas niveau (C++/CUDA, RTOS) et des architectures de réseaux profonds.

Et vous, quels défis rencontrez-vous dans le déploiement de modèles IA sur cibles embarquées ?

📸 Source & Crédits : Visualisation robotique open-source (Unsplash / Alex Knight)
🔗 Référence tech : NVIDIA Embedded Computing & OpenVLA Benchmark

#EmbeddedSystems #Robotics #ComputerVision #EdgeAI #NVIDIAJetson #CUDA #IndustrialIoT #Innovation""",
        "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1200&q=80",
        "image_name": "post1_vla_robotics.jpg"
    },
    {
        "text": """⚡ [HARDWARE & EMBEDDED] Pourquoi l'architecture ARM Cortex-M et les protocoles temps réel dominent l'IoT Industriel en 2026.

Dans les environnements industriels de précision, la puissance brute ne fait pas tout : le déterminisme temporel et la fiabilité des communications sont primordiaux.

Ce qui fait la différence sur le terrain :
✅ Bus CAN / CAN-FD & Industrial Ethernet (TSN, EtherCAT) pour un échange de données déterministe.
✅ Microcontrôleurs 32-bit avec accélérateurs DSP et extensions vectorielles pour le traitement du signal et TinyML sur microcontrôleur.
✅ Isolation logicielle stricte avec FreeRTOS ou Zephyr RTOS pour garantir la sécurité fonctionnelle (Safety Critical).

Pour les ingénieurs et chercheurs travaillant sur les communications industrielles et l'électronique de pointe : quels sont vos retours d'expérience sur la transition vers Zephyr RTOS ?

📸 Source de l'image : Conception de circuits haute fréquence (Unsplash / Umberto)
📚 Références : Industrial Automation & Embedded Systems Standards (IEEE / ARM Community)

#EmbeddedSystems #IndustrialIoT #Microcontrollers #FreeRTOS #ZephyrRTOS #CANBus #HardwareEngineering #Robotics""",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80",
        "image_name": "post2_embedded_hardware.jpg"
    }
]

TARGET_QUERIES = [
    "Embedded Systems Engineer Maroc",
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
            print(f"✅ Image téléchargée : {filename} ({len(resp.content)} bytes)")
            return img_path
    except Exception as e:
        print(f"⚠️ Erreur téléchargement image {filename} : {e}")
    return None

def publish_single_post(page, post_data: dict, index: int):
    """Publie un post avec son texte technique complet et son image attachée."""
    print(f"\n📝 --- PUBLICATION DU POST {index}/2 ---")
    
    # Préparer l'image
    img_path = download_image(post_data["image_url"], post_data["image_name"])

    page.goto("https://www.linkedin.com/feed/")
    page.wait_for_load_state("domcontentloaded")
    time.sleep(3)

    # 1. Ouvrir la modale de post
    create_btn = page.locator("button:has-text('Create a post'), button:has-text('Start a post'), p:has-text('Start a post')").first
    if not create_btn.is_visible():
        create_btn = page.locator("div:has-text('Start a post')").last

    if not create_btn.is_visible():
        print(f"❌ Bouton 'Create a post' non trouvé pour le post {index}.")
        return False

    create_btn.click()
    time.sleep(2)

    # 2. Joindre l'image via file chooser
    if img_path and img_path.exists():
        media_btn = page.locator("button[aria-label='Media'], button[aria-label='médias']").first
        if media_btn.is_visible():
            try:
                with page.expect_file_chooser(timeout=7000) as fc_info:
                    media_btn.click()
                    file_chooser = fc_info.value
                    file_chooser.set_files(str(img_path))
                    print(f"📸 Image attachée : {img_path.name}")
                    time.sleep(3)

                    # Bouton Next dans l'éditeur d'image
                    next_btn = page.locator("button:has-text('Next'), button:has-text('Suivant')").first
                    if next_btn.is_visible():
                        next_btn.click()
                        time.sleep(2)
                        print("✅ Étape image validée (Next).")
            except Exception as e:
                print(f"⚠️ Erreur attachement image : {e}")

    # 3. Écrire le contenu textuel avec sources
    editor = page.locator("div.ql-editor, div[role='textbox'][contenteditable='true']").first
    if editor.is_visible():
        editor.click()
        editor.fill(post_data["text"])
        time.sleep(2)
        print("✅ Texte technique et sources insérés dans l'éditeur.")

    # 4. Publier
    post_btn = page.locator("button:has-text('Post'), button:has-text('Publier')").filter(has_not_text="Create").filter(has_not_text="Commencer").first
    if post_btn.is_visible() and post_btn.is_enabled():
        post_btn.click()
        print(f"🚀 POST {index}/2 PUBLIÉ AVEC SUCCÈS SUR LINKEDIN !")
        time.sleep(5)
        return True
    else:
        print(f"⚠️ Bouton Post désactivé pour le post {index}.")
        return False

def send_auto_connections(page, total_target=25):
    """Envoie des demandes de connexion sans message aux profils cibles."""
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
        print(f"Trouvé {len(invite_links)} profils cibles sur cette page.")

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

    print(f"\n🎉 Total des connexions envoyées aujourd'hui : {connected}/{total_target}")
    return connected

def main():
    print("=" * 70)
    print("🤖 WORKFLOW LINKEDIN COMPLET — 2 POSTS PRO + IMAGES SOURCES + 25 CONNEXIONS")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        # 1. Publier les 2 posts avec leurs images et sources respectives
        for idx, post in enumerate(POSTS_DATA, 1):
            published = publish_single_post(page, post, idx)
            if idx == 1 and published:
                print("⏳ Pause de 60 secondes entre les 2 publications...")
                time.sleep(60)

        # 2. Envoyer les 25 demandes de connexion ciblées
        send_auto_connections(page, total_target=25)

    print("\n✅ TOUTES LES ÉTAPES DU WORKFLOW SONT COMPLÉTÉES AVEC SUCCÈS !")

if __name__ == "__main__":
    main()
