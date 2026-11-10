---
name: content-curator
description: Sélectionne chaque jour les sujets d'actualité et d'expertise technique adaptés à l'audience cible avec sources réelles.
---

# Content Curator Skill

## Rôle
Veille technologique quotidienne ciblée sur 4 piliers :
1. Systèmes Embarqués & Microcontrôleurs (ARM Cortex, STM32, ESP32, RTOS).
2. Edge AI & NVIDIA (Jetson AGX Orin, TensorRT, CUDA, TinyML).
3. Robotique & Vision par Ordinateur (ROS2, SLAM, VLA, LiDAR).
4. Protocoles Industriels & IoT (CAN-FD, Modbus, MQTT, EtherCAT).

## Contrainte Source Réelle
Chaque sujet doit obligatoirement comporter :
- Un titre clair du sujet technique.
- Une source vérifiable (Whitepaper, NVIDIA News, IEEE, GitHub Open Source, ArXiv).
- Une photo représentative avec mention de ses crédits.

## Sortie
Génère `selected_topics.json` contenant les 2 sujets retenus pour les créneaux 8h00 et 12h00.
