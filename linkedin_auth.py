"""
LinkedIn OAuth2 Setup
=====================
Exécutez ce script UNE SEULE FOIS pour obtenir votre access token LinkedIn.
Il ouvre un navigateur pour l'autorisation, puis sauvegarde le token dans .env
"""

import os
import json
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import requests
from dotenv import load_dotenv, set_key

load_dotenv()

CLIENT_ID     = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI  = "http://localhost:8080/callback"
SCOPES        = "openid profile w_member_social"
ENV_FILE      = Path(__file__).parent / ".env"

auth_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family:sans-serif;text-align:center;padding:50px">
                <h2>&#x2705; Autorisation LinkedIn r&#xe9;ussie !</h2>
                <p>Vous pouvez fermer cette fen&#234;tre et revenir dans Antigravity.</p>
                </body></html>
            """)
        else:
            error = params.get("error", ["inconnu"])[0]
            self.send_response(400)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"<h2>Erreur : {error}</h2>".encode())

    def log_message(self, format, *args):
        pass  # Silencer les logs HTTP


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ LINKEDIN_CLIENT_ID et LINKEDIN_CLIENT_SECRET manquants dans .env")
        print("   Ajoutez-les dans le fichier .env et relancez ce script.")
        return

    # Construire l'URL d'autorisation
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        + urllib.parse.urlencode({
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "state": "linkedin_growth_bot"
        })
    )

    print("\n🔐 LinkedIn OAuth2 Setup")
    print("=" * 40)
    print("1. Ouverture du navigateur pour autorisation...")
    print(f"   URL : {auth_url}\n")
    webbrowser.open(auth_url)

    print("2. En attente du callback sur http://localhost:8080/callback ...")
    server = HTTPServer(("localhost", 8080), CallbackHandler)
    server.handle_request()  # Attend une seule requête

    if not auth_code:
        print("❌ Pas de code reçu. Vérifiez votre app LinkedIn.")
        return

    print(f"\n3. Code reçu : {auth_code[:10]}...")
    print("4. Échange du code contre un access token...")

    # Échanger le code contre un token
    token_resp = requests.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15
    )

    if token_resp.status_code != 200:
        print(f"❌ Erreur token : {token_resp.status_code} — {token_resp.text}")
        return

    token_data = token_resp.json()
    access_token = token_data["access_token"]
    expires_in   = token_data.get("expires_in", 5184000)  # ~60 jours par défaut

    # Récupérer l'ID utilisateur via OpenID Connect
    userinfo_resp = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10
    )
    user_id = None
    if userinfo_resp.status_code == 200:
        user_data = userinfo_resp.json()
        sub = user_data.get("sub", "")
        user_id = f"urn:li:person:{sub}"
        print(f"\n✅ Connecté en tant que : {user_data.get('name', '?')}")
        print(f"   User ID : {user_id}")

    # Sauvegarder dans .env
    set_key(str(ENV_FILE), "LINKEDIN_ACCESS_TOKEN", access_token)
    if user_id:
        set_key(str(ENV_FILE), "LINKEDIN_USER_ID", user_id)

    print(f"\n✅ Access token sauvegardé dans .env (expire dans {expires_in // 86400} jours)")
    print("\n🚀 Vous pouvez maintenant lancer : python linkedin_publisher.py")


if __name__ == "__main__":
    main()
