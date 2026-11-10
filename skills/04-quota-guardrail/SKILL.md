---
name: quota-guardrail
description: Limite à 25 contacts/jour et impose un délai dynamique (90 à 180s) entre chaque action d'outreach.
---

# Quota Guardrail Skill

## Rôle
Assurer le respect intransigeant des règles de sécurité réseau LinkedIn pour éviter tout avertissement ou restriction de compte.

## Règles P1 Codées
1. **Hard-Limit Quotidien** : Plafond strict de 25 invitations émises par tranche de 24h (date locale).
2. **Temporisation Anti-Détection** : Délai aléatoire obligatoire entre 90 et 180 secondes entre deux sollicitations.
3. **Plage Horaire Autorisée** : Exécution permise exclusivement entre 08h00 et 18h00 heure locale (`Africa/Casablanca`).
4. **Week-end Interdit** : Aucune action le samedi et le dimanche.

## Sortie
```json
{
  "allow_dispatch": true,
  "daily_sent_count": 14,
  "daily_quota_max": 25,
  "next_delay_seconds": 127.4
}
```
Si le quota est atteint (25/25) : `allow_dispatch: false`, déclenchement de l'arrêt complet de la boucle d'outreach.
