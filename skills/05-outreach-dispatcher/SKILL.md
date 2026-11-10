---
name: outreach-dispatcher
description: Exécute la demande de mise en relation personnalisée via la session connectée et enregistre le statut.
---

# Outreach Dispatcher Skill

## Rôle
Prendre un prospect à l'état `PITCH_READY`, vérifier l'autorisation auprès de `quota-guardrail`, et déclencher le clic d'invitation avec ou sans note.

## Déroulement
1. Vérification accord `allow_dispatch == true`.
2. Navigation sur l'URL du profil ou le bouton d'invitation dans les résultats.
3. Clic sur `Connect`.
4. Si note : insertion de l'accroche issue de `icebreaker-generator` ; sinon : clic sur `Send without a note`.
5. Horodatage ISO 8601 de l'envoi.
6. Basculement de l'état du lead vers `INVITED` dans `lead_state_machine.json`.
7. Journalisation dans `logs/outreach_audit_YYYY-MM-DD.log`.

## Sortie
```json
{
  "lead_id": "lead_xxx",
  "status": "INVITED",
  "timestamp": "2026-11-10T08:15:30+01:00"
}
```
