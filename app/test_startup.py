#!/usr/bin/env python3
"""
Test simple du démarrage de l'application.
SOLITAIRE HACK - Test Startup
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, '..')

print("Test d'import et de configuration...")
try:
    from app.main import app
    print("Application importee avec succes")
    
    from app.core.model_loader import preload_model_registry
    print("Module model_loader importe")
    
    registry = preload_model_registry("models")
    print(f"Modeles charges: {registry.models_loaded}")
    
    from app.services.prediction_service import PredictionService
    service = PredictionService(registry)
    print("Service de prediction initialise")
    
    print("\nSUCCES: L'application peut demarrer correctement")
    
except Exception as e:
    print(f"ERREUR: {e}")
    import traceback
    traceback.print_exc()
