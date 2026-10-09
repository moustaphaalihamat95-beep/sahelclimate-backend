#!/usr/bin/env bash
echo "=========================================="
echo "   Démarrage de SahelClimate Backend API   "
echo "=========================================="

source venv/Scripts/activate

echo "Lancement du serveur Uvicorn..."
uvicorn main:app --reload --host 127.0.0.1 --port 8000
