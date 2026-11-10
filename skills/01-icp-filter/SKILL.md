---
name: icp-filter
description: Filtre les profils LinkedIn scrapés selon des critères ICP stricts (titre, pays, effectif) et élimine les doublons.
---

# ICP Filter Skill

## Rôle
Valider l'éligibilité d'un profil prospect selon le Persona défini (ICP) et éliminer les doublons dans `lead_state_machine.json`.

## Entrées
- `raw_profile`: Objet JSON contenant nom, titre, entreprise, localisation et URL.
- `icp_criteria`:
  - Titres autorisés : Embedded Systems, Robotics, Computer Vision, NVIDIA Jetson, IoT Industriel, PhD Student/Researcher.
  - Régions cibles : Maroc, France, Canada, Europe.
  - Tailles d'entreprise ciblées : Startups, PME, Laboratoires de recherche, Grandes ESN industrielles.

## Traitement
1. Vérifier si `profile_url` existe déjà dans `pipeline/lead_state_machine.json`. Si oui -> REJET DOUBLON.
2. Vérifier la correspondance des mots-clés du titre professionnel.
3. Vérifier la zone géographique.
4. Si critères validés : ajouter à la matrice d'état avec le statut `QUALIFIED`.

## Sortie
Objet JSON :
```json
{
  "lead_id": "lead_xxx",
  "status": "QUALIFIED | DISQUALIFIED",
  "reason": "ICP match validé | Titre non pertinent | Doublon"
}
```
