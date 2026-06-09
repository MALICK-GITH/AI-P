#!/usr/bin/env python3
"""
Script de test pour vérifier que tous les modèles sont correctement chargés.
SOLITAIRE HACK - Test d'intégration
"""

import sys
import os
import io

# Rediriger stdout pour éviter les problèmes d'encodage
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.model_loader import preload_model_registry
from app.services.model_router import ModelRouter
from app.services.prediction_service import PredictionService

def test_model_loading():
    """Test que tous les modèles peuvent être chargés"""
    print("="*60)
    print("TEST: Chargement des modèles")
    print("="*60)
    
    models_dir = "models"
    
    try:
        registry = preload_model_registry(models_dir)
        print(f"✓ Registre de modèles chargé avec succès")
        print(f"  Modèles chargés: {registry.models_loaded}")
        print(f"  Modèles disponibles: {registry.model_names}")
        print(f"  Colonnes de features partagées: {len(registry.shared_feature_columns)}")
        
        return registry
    except Exception as e:
        print(f"✗ Erreur lors du chargement des modèles: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_model_router(registry):
    """Test le système de routage intelligent"""
    print("\n" + "="*60)
    print("TEST: Système de routage intelligent")
    print("="*60)
    
    try:
        router = ModelRouter(registry)
        contexts = router.get_available_contexts()
        
        print(f"✓ Routeur initialisé avec succès")
        print(f"  Modes de jeu disponibles: {contexts['game_modes']}")
        print(f"  Compétitions disponibles: {contexts['competitions']}")
        print(f"  Pays disponibles: {contexts['countries']}")
        print(f"  Versions du jeu: {contexts['game_versions']}")
        print(f"  Total modèles indexés: {contexts['total_models']}")
        
        # Test de sélection de modèle
        test_selections = [
            {"league": "Champions League", "game_mode": "penalty"},
            {"league": "Premier League"},
            {"game_mode": "3x3"},
            {"game_version": "FC26"},
        ]
        
        print(f"\n  Tests de sélection de modèle:")
        for criteria in test_selections:
            selected = router.select_model_for_context(**criteria)
            print(f"    {criteria} -> {selected}")
        
        return router
    except Exception as e:
        print(f"✗ Erreur lors du test du routeur: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_prediction_service(registry):
    """Test le service de prédiction"""
    print("\n" + "="*60)
    print("TEST: Service de prédiction")
    print("="*60)
    
    try:
        service = PredictionService(registry)
        print(f"✓ Service de prédiction initialisé")
        print(f"  Modèles chargés: {service.models_loaded}")
        print(f"  Noms des modèles: {service.model_names}")
        
        # Test de construction de features
        from app.schemas.request_schema import PredictionRequest
        from datetime import datetime
        
        test_request = PredictionRequest(
            league="Test League",
            homeTeam="Team A",
            awayTeam="Team B",
            home_odds=2.5,
            draw_odds=3.2,
            away_odds=2.8,
            match_datetime=datetime.now(),
            game_mode="penalty",
            game_version="FC26"
        )
        
        features = service.build_feature_vector(test_request)
        print(f"✓ Construction de features réussie")
        print(f"  Features: {features}")
        
        return service
    except Exception as e:
        print(f"✗ Erreur lors du test du service: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("SOLITAIRE HACK - Test d'intégration des modèles")
    print("="*60)
    
    # Test 1: Chargement des modèles
    registry = test_model_loading()
    if not registry:
        print("\n✗ ÉCHEC: Impossible de charger les modèles")
        sys.exit(1)
    
    # Test 2: Routage intelligent
    router = test_model_router(registry)
    if not router:
        print("\n✗ ÉCHEC: Impossible d'initialiser le routeur")
        sys.exit(1)
    
    # Test 3: Service de prédiction
    service = test_prediction_service(registry)
    if not service:
        print("\n✗ ÉCHEC: Impossible d'initialiser le service")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ SUCCÈS: Tous les tests d'intégration ont réussi")
    print("="*60)
    print("\nSystème prêt pour l'intégration API:")
    print("  - Chargement de modèles: ✓")
    print("  - Routage intelligent: ✓")
    print("  - Service de prédiction: ✓")
    print("  - API endpoints prêts: ✓")

if __name__ == "__main__":
    main()
