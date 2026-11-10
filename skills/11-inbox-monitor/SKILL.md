---
name: inbox-monitor
description: Détecte les réponses positives des 25 prospects contactés et classe les leads dans la machine d'état.
---

# Inbox Monitor Skill

## Rôle
Surveiller la messagerie LinkedIn à intervalles réguliers (ex: 10h00, 14h00, 17h00) :
1. Identifier les invitations acceptées parmi les prospects au statut `INVITED`.
2. Mettre à jour leur statut vers `ACCEPTED`.
3. Détecter les messages entrants et les classifier :
   - `REPLIED_POSITIVE` : Le prospect souhaite échanger / poser une question.
   - `REPLIED_NEUTRAL` : Simple remerciement ("Merci pour l'ajout").
   - `DISQUALIFIED` : Refus poli ou non-intérêt.
4. Mettre à jour `pipeline/lead_state_machine.json`.
