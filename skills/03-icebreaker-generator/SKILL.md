---
name: icebreaker-generator
description: Rédige un message d'accroche personnalisé de 300 caractères max basé sur l'enrichissement du profil.
---

# Icebreaker Generator Skill

## Rôle
Rédiger une phrase d'accroche polie, naturelle et spécifique, strictement limitée à 300 caractères (limite LinkedIn note de connexion).

## Contraintes P1 & P2
- Longueur maximale : 300 caractères (espaces compris).
- Ton : Confraternel, professionnel, orienté échange technique.
- Zéro pitch commercial agressif ou vente de service.
- Référence obligatoire à un sujet technique partagé (Edge AI, Robotique, Systèmes embarqués).

## Sortie
```json
{
  "lead_id": "lead_xxx",
  "icebreaker": "Bonjour [Prénom], j'ai vu vos récents travaux sur [Sujet]. Travaillant également sur les systèmes embarqués et l'Edge AI, ce serait un plaisir d'échanger avec vous !",
  "char_count": 215,
  "status": "PITCH_READY"
}
```
Mise à jour automatique de la matrice `lead_state_machine.json` vers `PITCH_READY`.
