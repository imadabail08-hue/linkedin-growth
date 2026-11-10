"""
Skill 04 Extension : Module Jours Fériés & Mode Pause / Vacances
Gère le calendrier des jours fériés marocains et internationaux pour sécuriser l'engagement
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("Africa/Casablanca")

# Liste des jours fériés civils et nationaux au Maroc (mois, jour)
FIXED_HOLIDAYS_MOROCCO = [
    (1, 1),    # Jour de l'An
    (1, 11),   # Manifeste de l'Indépendance
    (5, 1),    # Fête du Travail
    (7, 30),   # Fête du Trône
    (8, 14),   # Allégeance Oued Eddahab
    (8, 20),   # Révolution du Roi et du Peuple
    (8, 21),   # Fête de la Jeunesse
    (11, 6),   # Marche Verte
    (11, 18),  # Fête de l'Indépendance
]

def is_holiday_or_weekend(check_date: date = None) -> tuple[bool, str]:
    """
    Retourne (True, motif) si le jour est un samedi, dimanche ou jour férié.
    """
    if check_date is None:
        check_date = datetime.now(TIMEZONE).date()

    # 1. Vérification Week-end (Samedi = 5, Dimanche = 6)
    if check_date.weekday() in (5, 6):
        day_name = "Samedi" if check_date.weekday() == 5 else "Dimanche"
        return True, f"Week-end ({day_name}) - Pause d'engagement LinkedIn recommandée"

    # 2. Vérification Jours Fériés Fixes
    for month, day in FIXED_HOLIDAYS_MOROCCO:
        if check_date.month == month and check_date.day == day:
            return True, f"Jour férié national Maroc ({day:02d}/{month:02d}) - Engagement faible"

    return False, "Jour ouvrable standard"

if __name__ == "__main__":
    is_paused, reason = is_holiday_or_weekend()
    print(f"Date : {datetime.now(TIMEZONE).strftime('%Y-%m-%d')} | Statut : {'PAUSE' if is_paused else 'ACTIF'} ({reason})")
