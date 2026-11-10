"""
Skill 06 & 07 : Curateur de Contenu Dynamique (ArXiv / NVIDIA RSS) & Générateur de Posts
Récupère les dernières actualités réelles de recherche en Robotique, Vision et Systèmes Embarqués
"""

import urllib.request
import xml.etree.ElementTree as ET
import json
import random
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Windows 10\.gemini\antigravity\scratch\linkedin-growth")
CACHE_FILE = BASE_DIR / "curated_news_cache.json"

FEEDS = [
    # ArXiv Robotics (cs.RO)
    {"url": "https://export.arxiv.org/rss/cs.RO", "domain": "Robotics & Autonomous Systems"},
    # ArXiv Computer Vision (cs.CV)
    {"url": "https://export.arxiv.org/rss/cs.CV", "domain": "Computer Vision & Edge AI"},
    # IEEE Spectrum Robotics / Tech
    {"url": "https://spectrum.ieee.org/feeds/topic/robotics.rss", "domain": "Industrial Robotics"},
]

UNSPLASH_TECH_IMAGES = [
    {"url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1200&q=80", "credit": "Visualisation robotique intelligente (Unsplash / Alex Knight)"},
    {"url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80", "credit": "Architecture matériel embarqué & microcontrôleur (Unsplash / Umberto)"},
    {"url": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=1200&q=80", "credit": "Système de contrôle & automatisation industrielle (Unsplash / Science in HD)"},
    {"url": "https://images.unsplash.com/photo-1555255707-c07966088b7b?w=1200&q=80", "credit": "Calcul haute performance & intelligence artificielle (Unsplash / DeepMind)"}
]

def fetch_latest_research():
    articles = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AntigravityCurator/1.0"}
    
    for feed in FEEDS:
        try:
            req = urllib.request.Request(feed["url"], headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                
                # Parser les items RSS standard
                items = root.findall(".//item")
                for item in items[:4]:
                    title = item.findtext("title", "").strip()
                    link = item.findtext("link", "").strip()
                    desc = item.findtext("description", "").strip()
                    
                    # Nettoyage simple des balises HTML
                    if "<" in desc:
                        import re
                        desc = re.sub(r"<[^>]+>", " ", desc)
                    desc = " ".join(desc.split())[:300]
                    
                    if title and link:
                        articles.append({
                            "title": title,
                            "link": link,
                            "summary": desc,
                            "domain": feed["domain"]
                        })
        except Exception as e:
            # Fallback silencieux en cas de coupure réseau RSS
            continue

    if articles:
        CACHE_FILE.write_text(json.dumps(articles, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"✅ {len(articles)} articles récents récupérés depuis ArXiv/IEEE.")
    return articles

def generate_dynamic_post(slot: str = "morning") -> dict:
    """Génère un post enrichi dynamiquement avec les derniers travaux ArXiv / IEEE."""
    articles = []
    if CACHE_FILE.exists():
        try:
            articles = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    if not articles:
        articles = fetch_latest_research()

    # Sélection d'un article ou fallback
    selected = random.choice(articles) if articles else None
    img_meta = random.choice(UNSPLASH_TECH_IMAGES)

    if slot == "morning":
        # Format 08h00 : Analytique & Tendance Edge AI / Robotique
        if selected:
            title_clean = selected['title'].split("(")[0].strip()
            text = f"""🤖 [VEILLE TECH EMBARQUÉ & IA] Décryptage de publication : {title_clean}

L'accélération de la recherche appliquée en robotique et vision par ordinateur franchit un nouveau palier :

🔹 Thématique clé : {selected['domain']}
🔹 Enjeu technique : L'inférence temps réel et la compression de modèles pour les cibles matérielles contraintes (DSP, GPU embarqué, Jetson).
🔹 Aperçu : {selected['summary'][:180]}...

💡 Dans les systèmes industriels et autonomes, le défi n'est plus seulement la précision algorithmique pure, mais la latence déterministe et l'efficacité énergétique par watt.

Quelle est votre approche actuelle pour le déploiement sur cibles contraintes ?

📸 Source de l'image : {img_meta['credit']}
📚 Référence académique vérifiable : {selected['link']}

#EmbeddedSystems #Robotics #ComputerVision #EdgeAI #NVIDIA #TechResearch #Innovation"""
        else:
            text = """🤖 [TECH INSIGHT] L'essor des modèles Vision-Language-Action (VLA) dans la robotique autonome.

L'intégration des modèles VLA comme OpenVLA sur du matériel embarqué (NVIDIA Jetson AGX Orin) redéfinit la manipulation robotique :
🔹 Inférence locale temps réel : Grâce à TensorRT et à la quantification INT8, exécution directement en bordure de réseau.
🔹 Latence critique : Moins de 35 ms en local vs plusieurs secondes via Cloud.
🔹 Déterminisme : Pas d'interruption lors de pertes réseau en milieu industriel.

📸 Source : Visualisation robotique open-source (Unsplash / Alex Knight)
🔗 Référence tech : NVIDIA Embedded Computing & OpenVLA Benchmark

#EmbeddedSystems #Robotics #ComputerVision #EdgeAI #NVIDIAJetson #CUDA #IndustrialIoT"""

        return {
            "title": "Post Matin (08h00)",
            "text": text,
            "image_url": img_meta["url"],
            "image_name": "post_morning_dynamic.jpg"
        }

    else:
        # Format 12h00 : Cas Pratique & Architecture Matérielle / IoT
        if selected:
            text = f"""⚡ [INGÉNIERIE & HARDWARE] Du papier de recherche à la réalité terrain : focus sur {selected['domain']}.

Transposer les avancées théoriques sur des microcontrôleurs industriels (ARM Cortex-M, STM32, ESP32) impose des règles strictes :
✅ Protocoles temps réel déterministes (Bus CAN, CAN-FD, EtherCAT) pour fiabiliser le flux de commande.
✅ Gestion mémoire statique stricte et ordonnancement sous RTOS (Zephyr RTOS / FreeRTOS).
✅ Intégration de briques TinyML pour le filtrage prédictif direct des capteurs sans latence.

Aperçu du travail de référence : "{selected['title'][:120]}..."

Pour les développeurs firmware et roboticiens : privilégiez-vous Zephyr ou FreeRTOS sur vos architectures récentes ?

📸 Source de l'image : {img_meta['credit']}
🔗 Source & détails : {selected['link']}

#EmbeddedSystems #IndustrialIoT #Microcontrollers #FreeRTOS #ZephyrRTOS #CANBus #HardwareEngineering"""
        else:
            text = """⚡ [HARDWARE & EMBEDDED] Pourquoi l'architecture ARM Cortex-M et les protocoles temps réel dominent l'IoT Industriel.

Dans les environnements industriels de précision, la puissance brute ne fait pas tout : le déterminisme temporel et la fiabilité des communications sont primordiaux.
✅ Bus CAN / CAN-FD & Industrial Ethernet pour un échange déterministe.
✅ Microcontrôleurs 32-bit avec accélérateurs vectoriels pour TinyML.
✅ Isolation logicielle avec FreeRTOS ou Zephyr RTOS.

📸 Source de l'image : Conception de circuits haute fréquence (Unsplash / Umberto)
📚 Références : Industrial Automation Standards (IEEE / ARM Community)

#EmbeddedSystems #IndustrialIoT #Microcontrollers #FreeRTOS #ZephyrRTOS #CANBus #HardwareEngineering"""

        return {
            "title": "Post Midi (12h00)",
            "text": text,
            "image_url": img_meta["url"],
            "image_name": "post_noon_dynamic.jpg"
        }

if __name__ == "__main__":
    fetch_latest_research()
    p = generate_dynamic_post("morning")
    print("\n--- Aperçu Post Dynamique Généré ---")
    print(p["text"][:300] + "...")
