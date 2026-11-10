@echo off
chcp 65001 > nul
cls
echo ======================================================================
echo    🚀 LINKEDIN DAILY GROWTH — ANTIGRAVITY MULTI-SKILLS AGENT
echo ======================================================================
echo.
echo  [1] Lancer le créneau Matin (08h00) : Post Analytique VLA + 13 Connexions
echo  [2] Lancer le créneau Midi (12h00)  : Post Embarqué IoT + 12 Connexions
echo  [3] Vérifier Calendrier & Jours Fériés (Holiday Checker)
echo  [4] Prévisualiser le Contenu Dynamique (ArXiv / IEEE / NVIDIA)
echo  [5] Quitter
echo.
set /p choice="Choisissez une option [1-5] : "

if "%choice%"=="1" (
    echo.
    echo [*] Lancement du créneau Matin...
    python daily_linkedin_runner.py --slot morning
    pause
    goto end
)

if "%choice%"=="2" (
    echo.
    echo [*] Lancement du créneau Midi...
    python daily_linkedin_runner.py --slot noon
    pause
    goto end
)

if "%choice%"=="3" (
    echo.
    echo [*] Vérification du calendrier ouvrable...
    python holiday_checker.py
    pause
    goto end
)

if "%choice%"=="4" (
    echo.
    echo [*] Génération des posts dynamiques du jour :
    python -c "import dynamic_content_curator; m = dynamic_content_curator.generate_dynamic_post('morning'); print('\n--- POST MATIN ---'); print(m['text']); n = dynamic_content_curator.generate_dynamic_post('noon'); print('\n--- POST MIDI ---'); print(n['text'])"
    pause
    goto end
)

:end
