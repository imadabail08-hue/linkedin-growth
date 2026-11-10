---
name: visual-generator
description: Génère les visuels d'accompagnement (infographies SVG natives autonomes, carrousels ou bannières aux ratios 1:1 ou 4:5).
---

# Visual Generator Skill

## Rôle
Créer ou formater le visuel accompagnant chaque publication sans dépendance logicielle externe fragile :
- **Format 1** : SVG vectoriel natif haute résolution 1080x1080 (Ratio 1:1) avec palette industrielle (Slate, Emerald, Sky).
- **Format 2** : Téléchargement et optimisation d'une image réelle haute résolution libre de droits (Unsplash) associée à son crédit explicite.

## Sortie
Génère le fichier image local (`post_image.jpg` ou `visual.svg`) prêt à être injecté par `post-scheduler`.
