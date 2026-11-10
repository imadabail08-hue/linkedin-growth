"""
Skill 10 : Tracker d'Engagement & Bibliothèque de Repurposing des Meilleurs Posts
Sauvegarde les posts à fort engagement pour un recyclage intelligent après 60 jours
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Windows 10\.gemini\antigravity\scratch\linkedin-growth")
TOP_POSTS_LIBRARY = BASE_DIR / "top_posts_library.json"

def init_library():
    if not TOP_POSTS_LIBRARY.exists():
        TOP_POSTS_LIBRARY.write_text(json.dumps({"top_posts": []}, indent=2, ensure_ascii=False), encoding="utf-8")

def log_post_performance(post_text: str, likes: int, comments: int, source_link: str = ""):
    """Enregistre un post performant dans la bibliothèque pour futur recyclage."""
    init_library()
    data = json.loads(TOP_POSTS_LIBRARY.read_text(encoding="utf-8"))
    
    # Seuil de qualification pour "Top Post" (ex: >= 15 réactions ou discussion active)
    if likes >= 15 or comments >= 3:
        entry = {
            "id": f"top_{len(data['top_posts']) + 1}",
            "text": post_text,
            "likes": likes,
            "comments": comments,
            "source_link": source_link,
            "published_at": datetime.now().strftime("%Y-%m-%d"),
            "repurpose_after": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
            "repurposed": False
        }
        data["top_posts"].append(entry)
        TOP_POSTS_LIBRARY.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"🌟 Post performant ajouté à la bibliothèque de recyclage (Likes: {likes}, Comms: {comments})")

def get_post_ready_for_repurpose() -> dict | None:
    """Retourne un ancien post à succès prêt à être revisité sous un nouvel angle."""
    init_library()
    data = json.loads(TOP_POSTS_LIBRARY.read_text(encoding="utf-8"))
    today_str = datetime.now().strftime("%Y-%m-%d")

    for p in data["top_posts"]:
        if not p.get("repurposed") and p.get("repurpose_after", "") <= today_str:
            p["repurposed"] = True
            TOP_POSTS_LIBRARY.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            return p
    return None

if __name__ == "__main__":
    init_library()
    print("Bibliothèque de recyclage opérationnelle :", TOP_POSTS_LIBRARY.name)
