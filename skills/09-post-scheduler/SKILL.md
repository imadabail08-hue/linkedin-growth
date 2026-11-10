---
name: post-scheduler
description: Programme et exécute la publication des posts aux déclencheurs de 8h00 et 12h00 via la session LinkedIn active.
---

# Post Scheduler Skill

## Rôle
Prendre le post rédigé et son image associée, et déclencher la publication sur le compte LinkedIn à l'heure exacte.

## Processus d'Exécution
1. Ouvrir le flux d'actualité LinkedIn (`/feed/`).
2. Cliquer sur le créateur de publication (`Create a post`).
3. Attacher le fichier image via le gestionnaire de fichier Playwright.
4. Valider l'étape de prévisualisation image (`Next`).
5. Insérer le texte complet (avec les mentions de sources).
6. Cliquer sur le bouton `Post` / `Publier`.
7. Vérifier la confirmation visuelle et journaliser l'ID/horodatage.
