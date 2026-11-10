---
name: daily-reporter
description: Génère chaque soir à 18h00 un bilan factuel : posts publiés, invitations émises (sur 25), réponses reçues, et métriques [À mesurer].
---

# Daily Reporter Skill

## Rôle
Produire le rapport de synthèse journalier à 18h00 garantissant la traçabilité complète :
- Nombre de posts publiés (objectif : 2/2).
- Nombre total d'invitations émises dans la journée (objectif : 25/25).
- Taux de complétion et incidents éventuels.
- Application stricte de la règle **Anti-hallucination** :
  Toute métrique d'engagement non mesurable immédiatement en direct (portée à 72h, taux d'acceptation à 7 jours) est rigoureusement notée **`[À mesurer]`**.

## Fichier généré
`logs/daily_growth_report_YYYY-MM-DD.md`
