---
name: profile-enricher
description: Extrait les 3 derniers posts et la bio d'un profil qualifié pour contextualiser le futur message d'accroche.
---

# Profile Enricher Skill

## Rôle
Collecter les éléments contextuels publics indispensables pour personnaliser l'invitation sans utiliser de messages génériques.

## Entrées
- `lead_id`: Identifiant du prospect qualifié.
- `profile_url`: URL LinkedIn du prospect.

## Traitement
1. Naviguer vers le profil public LinkedIn via la session active Chrome CDP.
2. Extraire la section "Infos" (Bio/About).
3. Extraire les 3 derniers posts ou activités publiés par l'utilisateur (sujets abordés, technologies citées).
4. Enregistrer les métadonnées dans le profil du lead sous `pipeline/lead_state_machine.json`.
5. Mettre à jour le statut du lead vers `ENRICHED`.

## Sortie
```json
{
  "lead_id": "lead_xxx",
  "status": "ENRICHED",
  "context": {
    "headline": "...",
    "recent_topics": ["ROS2", "SLAM", "Jetson Orin"],
    "summary_keywords": ["robotics", "embedded"]
  }
}
```
