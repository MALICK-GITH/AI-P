#!/usr/bin/env python3
"""
Script de démarrage de l'API avec configuration correcte du PYTHONPATH.
SOLITAIRE HACK - Serveur API
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Maintenant importer et démarrer l'application
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Démarrage de l'API ONE DELUX AI 3.0...")
    print("Modèles intégrés:")
    print("  - 16 modèles .pkl chargés dynamiquement")
    print("  - Système de routage intelligent actif")
    print("  - Support de multiples contextes (jeux, championnats, pays)")
    print("\nEndpoints disponibles:")
    print("  - GET  /")
    print("  - GET  /docs")
    print("  - GET  /api/status")
    print("  - GET  /api/models")
    print("  - GET  /api/models/contexts")
    print("  - GET  /api/models/select")
    print("  - POST /api/predict")
    print("  - POST /api/predict/over-under")
    print("  - POST /api/predict/home-goals")
    print("  - POST /api/predict/away-goals")
    print("  - POST /api/predict/total-goals")
    print("  - POST /api/predict/fusion")
    print("\nServeur démarré sur http://127.0.0.1:8000")
    print("Appuyez sur Ctrl+C pour arrêter.")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False
    )
