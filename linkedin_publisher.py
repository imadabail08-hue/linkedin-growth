"""
LinkedIn Daily Growth Bot
=========================
Publie automatiquement 2 posts avec images sur LinkedIn via l'API officielle.
Utilise Unsplash pour les photos stock et Gemini pour générer les posts.

Requirements: pip install requests google-generativeai python-dotenv Pillow
"""

import os
import json
import requests
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─── Configuration ────────────────────────────────────────────────────────────
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_USER_ID      = os.getenv("LINKEDIN_USER_ID")        # urn:li:person:XXXXX
UNSPLASH_ACCESS_KEY   = os.getenv("UNSPLASH_ACCESS_KEY")
GEMINI_API_KEY        = os.getenv("GEMINI_API_KEY")

OUTPUT_DIR = Path(__file__).parent
POSTS_LOG  = OUTPUT_DIR / "linkedin-daily-posts.md"
CONN_LOG   = OUTPUT_DIR / "linkedin-daily-connections.md"

DOMAINS = [
    "embedded systems", "robotics", "computer vision",
    "NVIDIA Jetson", "edge AI", "industrial IoT",
    "CUDA", "ROS2", "TinyML", "autonomous systems"
]

UNSPLASH_QUERIES = {
    "tech_concept": ["robotics engineering", "computer vision AI", "embedded systems circuit",
                     "NVIDIA GPU computing", "industrial automation", "neural network visualization"],
    "human_context": ["engineer working laptop", "researchers collaboration", "tech team meeting",
                      "university lab students", "innovation workspace", "developer coding"]
}

# ─── 1. Générer le texte des posts avec Gemini ───────────────────────────────
def generate_posts() -> list[dict]:
    """Génère 2 posts LinkedIn via l'API Gemini."""
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    today = datetime.date.today().strftime("%d %B %Y")
    prompt = f"""Tu es un expert en personal branding LinkedIn spécialisé en systèmes embarqués, robotique, computer vision, IA, NVIDIA, IoT industriel.

Génère EXACTEMENT 2 posts LinkedIn pour le {today}. 
Renvoie un JSON valide avec cette structure :
{{
  "posts": [
    {{
      "language": "french",
      "content": "...(150-300 mots, avec emojis, hashtags en fin)...",
      "image_type": "tech_concept",
      "image_query": "...(requête Unsplash en anglais, 3-4 mots)...",
      "topic": "...(sujet court)"
    }},
    {{
      "language": "english", 
      "content": "...(150-300 mots, avec emojis, hashtags en fin)...",
      "image_type": "human_context",
      "image_query": "...(requête Unsplash en anglais, 3-4 mots)...",
      "topic": "...(sujet court)"
    }}
  ]
}}

Règles :
- Post 1 : Français avec quelques mots-clés anglais, format storytelling ou insight technique
- Post 2 : Anglais avec intro française si pertinent, format conseil ou tendance
- Varier les sujets chaque jour (ne pas répéter les mêmes thèmes)
- Hashtags : 5-8 par post, pertinents pour le domaine
- image_query : requête précise pour trouver une belle photo sur Unsplash
- Renvoie UNIQUEMENT le JSON, sans markdown ni balises"""

    response = model.generate_content(prompt)
    # Nettoyer le JSON si entouré de backticks markdown
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())["posts"]


# ─── 2. Récupérer une photo Unsplash ─────────────────────────────────────────
def get_unsplash_photo(query: str) -> dict | None:
    """Récupère une photo Unsplash libre de droits."""
    if not UNSPLASH_ACCESS_KEY:
        print("⚠️  UNSPLASH_ACCESS_KEY manquant — pas de photo stock")
        return None

    url = "https://api.unsplash.com/photos/random"
    params = {
        "query": query,
        "orientation": "landscape",
        "content_filter": "high",
    }
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}

    resp = requests.get(url, params=params, headers=headers, timeout=10)
    if resp.status_code != 200:
        print(f"⚠️  Unsplash error {resp.status_code}")
        return None

    data = resp.json()
    return {
        "url": data["urls"]["regular"],          # URL haute qualité
        "download_url": data["links"]["download"], # URL de téléchargement (obligatoire Unsplash)
        "photographer": data["user"]["name"],
        "photographer_url": data["user"]["links"]["html"],
        "unsplash_url": data["links"]["html"],
        "alt": data.get("alt_description", query),
    }


# ─── 3. Télécharger l'image en local ─────────────────────────────────────────
def download_image(photo: dict, filename: str) -> Path | None:
    """Télécharge l'image Unsplash en local."""
    # Enregistrer le téléchargement (obligatoire par les ToS Unsplash)
    if UNSPLASH_ACCESS_KEY:
        requests.get(photo["download_url"] + f"?client_id={UNSPLASH_ACCESS_KEY}", timeout=5)

    img_path = OUTPUT_DIR / "images" / filename
    img_path.parent.mkdir(exist_ok=True)

    resp = requests.get(photo["url"], timeout=30)
    if resp.status_code == 200:
        img_path.write_bytes(resp.content)
        print(f"  📸 Image sauvegardée : {img_path.name}")
        return img_path
    return None


# ─── 4. Upload de l'image sur LinkedIn ───────────────────────────────────────
def upload_image_to_linkedin(image_path: Path) -> str | None:
    """
    Upload une image sur LinkedIn et retourne l'asset URN.
    Doc : https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/images-api
    """
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    # Étape 1 : Initialiser l'upload
    init_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": LINKEDIN_USER_ID,
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }
    resp = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers=headers,
        json=init_body,
        timeout=15
    )
    if resp.status_code != 200:
        print(f"  ❌ Erreur init upload LinkedIn : {resp.status_code} — {resp.text}")
        return None

    upload_data = resp.json()["value"]
    upload_url  = upload_data["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn   = upload_data["asset"]

    # Étape 2 : Upload du fichier binaire
    with open(image_path, "rb") as f:
        upload_resp = requests.put(
            upload_url,
            data=f,
            headers={"Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"},
            timeout=30
        )
    if upload_resp.status_code not in (200, 201):
        print(f"  ❌ Erreur upload image : {upload_resp.status_code}")
        return None

    print(f"  ✅ Image uploadée : {asset_urn}")
    return asset_urn


# ─── 5. Publier le post sur LinkedIn ─────────────────────────────────────────
def publish_post(content: str, image_asset_urn: str | None, photo_credit: str | None) -> bool:
    """Publie un post sur LinkedIn via l'UGC Posts API."""
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    # Ajouter le crédit photo si image Unsplash
    final_content = content
    if photo_credit:
        final_content += f"\n\n📸 Photo: {photo_credit} via Unsplash"

    if image_asset_urn:
        body = {
            "author": LINKEDIN_USER_ID,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": final_content},
                    "shareMediaCategory": "IMAGE",
                    "media": [{
                        "status": "READY",
                        "description": {"text": ""},
                        "media": image_asset_urn,
                        "title": {"text": ""}
                    }]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
    else:
        body = {
            "author": LINKEDIN_USER_ID,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": final_content},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }

    resp = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=headers,
        json=body,
        timeout=15
    )

    if resp.status_code == 201:
        post_id = resp.headers.get("x-restli-id", "?")
        print(f"  ✅ Post publié ! ID : {post_id}")
        return True
    else:
        print(f"  ❌ Erreur publication : {resp.status_code} — {resp.text}")
        return False


# ─── 6. Générer la liste des connexions ──────────────────────────────────────
def generate_connections_list() -> str:
    """Génère 25 recherches LinkedIn ciblées pour les connexions du jour."""
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    today = datetime.date.today().strftime("%d %B %Y")
    prompt = f"""Génère une liste de 25 recherches LinkedIn ciblées pour le {today}.
Profils cibles : ingénieurs systèmes embarqués, chercheurs/PhD robotique et computer vision, spécialistes NVIDIA/CUDA/edge computing, étudiants Master/PhD en électronique et informatique industrielle, experts IoT industriel, professeurs dans grandes écoles (Maroc, France, Canada).

Renvoie un JSON :
{{
  "connections": [
    {{
      "search": "titre de recherche LinkedIn (ex: Embedded Systems Engineer Maroc)",
      "keywords": ["mot1", "mot2", "mot3"],
      "profile_type": "type de profil (étudiant/chercheur/ingénieur/professeur)"
    }}
  ]
}}

Renvoie UNIQUEMENT le JSON, 25 entrées variées, sans répétition."""

    response = model.generate_content(prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    data = json.loads(text.strip())
    lines = [f"# 👥 LinkedIn Connexions — {today}\n\n"]
    lines.append("| # | Recherche LinkedIn | Type | Mots-clés |\n")
    lines.append("|---|---|---|---|\n")
    for i, c in enumerate(data["connections"], 1):
        kw = ", ".join(c["keywords"])
        lines.append(f"| {i} | {c['search']} | {c['profile_type']} | {kw} |\n")
    return "".join(lines)


# ─── 7. Logger les posts ──────────────────────────────────────────────────────
def log_post(post: dict, photo: dict | None, published: bool):
    today = datetime.date.today().strftime("%d %B %Y")
    status = "✅ PUBLIÉ" if published else "❌ ÉCHEC"
    with open(POSTS_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n## {today} — {post['topic']} [{status}]\n\n")
        f.write(post["content"] + "\n")
        if photo:
            f.write(f"\n📸 Photo: [{photo['photographer']}]({photo['photographer_url']}) — [Unsplash]({photo['unsplash_url']})\n")
        f.write("\n---\n")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    today = datetime.date.today().strftime("%d %B %Y")
    print(f"\n🚀 LinkedIn Daily Growth — {today}")
    print("=" * 50)

    # Vérification des credentials
    if not LINKEDIN_ACCESS_TOKEN:
        print("❌ LINKEDIN_ACCESS_TOKEN manquant dans .env")
        print("   Lancez d'abord : python linkedin_auth.py")
        return
    if not LINKEDIN_USER_ID:
        print("❌ LINKEDIN_USER_ID manquant dans .env")
        return

    # 1. Générer les posts
    print("\n📝 Génération des posts avec Gemini...")
    posts = generate_posts()
    print(f"  ✅ {len(posts)} posts générés")

    # 2. Pour chaque post : image + publication
    for i, post in enumerate(posts, 1):
        print(f"\n📌 Post {i}/{len(posts)} — {post['topic']} ({post['language'].upper()})")

        # Récupérer photo Unsplash
        photo = get_unsplash_photo(post["image_query"])
        image_asset = None
        photo_credit = None

        if photo:
            # Télécharger en local
            fname = f"post_{today.replace(' ', '_')}_{i}.jpg"
            img_path = download_image(photo, fname)
            # Uploader sur LinkedIn
            if img_path:
                image_asset = upload_image_to_linkedin(img_path)
            photo_credit = f"{photo['photographer']} ({photo['unsplash_url']})"

        # Publier
        published = publish_post(post["content"], image_asset, photo_credit)
        log_post(post, photo, published)

    # 3. Générer liste connexions
    print("\n👥 Génération de la liste des 25 connexions...")
    connections_md = generate_connections_list()
    with open(CONN_LOG, "a", encoding="utf-8") as f:
        f.write(connections_md + "\n---\n\n")
    print("  ✅ Liste sauvegardée dans linkedin-daily-connections.md")

    print(f"\n🎉 Terminé ! 2 posts publiés sur LinkedIn, 25 connexions à faire.")
    print(f"   📂 Logs : {POSTS_LOG}")
    print(f"   📂 Connexions : {CONN_LOG}")


if __name__ == "__main__":
    main()
