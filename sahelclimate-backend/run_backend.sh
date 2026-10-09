#!/bin/bash
echo "=== Démarrage de SahelClimate-AI Backend ==="
source venv/Scripts/activate 2>/dev/null || true

if [ -f "app/main.py" ]; then
    echo "Fichier app/main.py trouvé. Lancement d'Uvicorn..."
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
elif [ -f "main.py" ]; then
    echo "Fichier main.py trouvé. Lancement d'Uvicorn..."
    uvicorn main:app --reload --host 127.0.0.1 --port 8000
else
    echo "ERREUR : Fichier main.py introuvable dans ce dossier ou dans ./app/"
fi
