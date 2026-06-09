#!/usr/bin/env python3
"""
Script de test direct des composants optimisés
SOLITAIRE HACK - Test sans serveur
"""

import sys
import os
import io
import time
from datetime import datetime

# Rediriger stdout pour éviter les problèmes d'encodage
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.model_loader import preload_model_registry
from app.services.model_router import ModelRouter
from app.services.prediction_service import PredictionService
from app.schemas.request_schema import PredictionRequest

def test_cache_system():
    """Test le système de cache"""
    print("="*60)
    print("TEST: Système de Cache Intelligent")
    print("="*60)
    
    models_dir = "models"
    
    try:
        # Charger les modèles
        print("\nChargement des modèles...")
        registry = preload_model_registry(models_dir)
        print(f"✓ {registry.models_loaded} modèles chargés")
        
        # Initialiser le service de prédiction
        print("\nInitialisation du service de prédiction...")
        service = PredictionService(registry)
        print(f"✓ Service initialisé avec {service.models_loaded} modèles")
        
        # Vérifier que le cache est activé
        print("\nVérification du cache...")
        if hasattr(service._fusion_engine, '_cache'):
            print("✓ Cache intelligent activé")
            cache_stats = service._fusion_engine.get_cache_stats()
            print(f"  Statistiques initiales: {cache_stats}")
        else:
            print("✗ Cache non disponible")
            return False
        
        # Test de prédiction avec cache
        print("\nTest de prédiction #1 (cache miss attendu)...")
        request1 = PredictionRequest(
            league="Test League",
            home_team="Team A",  # SOLITAIRE HACK: Utiliser le nom réel du champ
            away_team="Team B",  # SOLITAIRE HACK: Utiliser le nom réel du champ
            home_odds=2.5,
            draw_odds=3.2,
            away_odds=2.8,
            match_datetime=datetime.now(),
            game_mode="penalty",
            game_version="FC26"
        )
        
        start_time = time.time()
        result1 = service.predict_fusion(request1)
        elapsed1 = time.time() - start_time
        
        print(f"✓ Prédiction #1 terminée en {elapsed1:.3f}s")
        print(f"  Résultat: {result1['score_prediction']}")
        
        # Vérifier les stats après la première prédiction
        cache_stats_after_1 = service._fusion_engine.get_cache_stats()
        print(f"  Stats après #1: {cache_stats_after_1}")
        
        # Test de prédiction identique (cache hit attendu)
        print("\nTest de prédiction #2 (cache hit attendu)...")
        request2 = PredictionRequest(
            league="Test League",
            home_team="Team A",  # SOLITAIRE HACK: Utiliser le nom réel du champ
            away_team="Team B",  # SOLITAIRE HACK: Utiliser le nom réel du champ
            home_odds=2.5,
            draw_odds=3.2,
            away_odds=2.8,
            match_datetime=datetime.now(),
            game_mode="penalty",
            game_version="FC26"
        )
        
        start_time = time.time()
        result2 = service.predict_fusion(request2)
        elapsed2 = time.time() - start_time
        
        print(f"✓ Prédiction #2 terminée en {elapsed2:.3f}s")
        print(f"  Résultat: {result2['score_prediction']}")
        
        # Vérifier les stats après la deuxième prédiction
        cache_stats_after_2 = service._fusion_engine.get_cache_stats()
        print(f"  Stats après #2: {cache_stats_after_2}")
        
        # Comparer les temps
        speedup = elapsed1 / elapsed2 if elapsed2 > 0 else 1.0
        print(f"\n⚡ Amélioration de performance: {speedup:.2f}x plus rapide")
        
        # Vérifier que les résultats sont identiques
        if result1['score_prediction'] == result2['score_prediction']:
            print("✓ Résultats identiques (consistance du cache)")
        else:
            print("✗ Résultats différents (problème de cache)")
            return False
        
        # Test de vidage du cache
        print("\nTest de vidage du cache...")
        service._fusion_engine.clear_cache()
        cache_stats_after_clear = service._fusion_engine.get_cache_stats()
        print(f"✓ Cache vidé: {cache_stats_after_clear}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_routing():
    """Test le système de routage intelligent"""
    print("\n" + "="*60)
    print("TEST: Système de Routage Intelligent")
    print("="*60)
    
    models_dir = "models"
    
    try:
        registry = preload_model_registry(models_dir)
        router = ModelRouter(registry)
        
        print(f"✓ Routeur initialisé avec {registry.models_loaded} modèles")
        
        # Test de sélection pour différents contextes
        test_contexts = [
            {"game_mode": "penalty", "game_version": "FC26"},
            {"league": "Champions League"},
            {"game_mode": "3x3"},
            {"game_version": "FC25"},
        ]
        
        print("\nTests de sélection de modèle:")
        for context in test_contexts:
            selected = router.select_model_for_context(**context)
            print(f"  Contexte {context} -> {selected}")
        
        # Obtenir les contextes disponibles
        contexts = router.get_available_contexts()
        print(f"\n✓ Contextes disponibles:")
        print(f"  Modes de jeu: {contexts['game_modes']}")
        print(f"  Compétitions: {contexts['competitions']}")
        print(f"  Pays: {contexts['countries']}")
        print(f"  Versions: {contexts['game_versions']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("SOLITAIRE HACK - Test des Composants Optimisés")
    print("="*60)
    
    # Test 1: Cache system
    cache_ok = test_cache_system()
    
    # Test 2: Model routing
    routing_ok = test_model_routing()
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    print(f"Système de Cache: {'✓ SUCCÈS' if cache_ok else '✗ ÉCHEC'}")
    print(f"Routage Intelligent: {'✓ SUCCÈS' if routing_ok else '✗ ÉCHEC'}")
    
    if cache_ok and routing_ok:
        print("\n✓ TOUS LES TESTS RÉUSSIS - SYSTÈME OPTIMISÉ OPÉRATIONNEL")
        print("\nAméliorations implémentées:")
        print("  • Cache intelligent avec TTL pour les prédictions")
        print("  • Statistiques de performance en temps réel")
        print("  • Gestion améliorée des erreurs avec logging détaillé")
        print("  • Endpoints API enrichis avec métriques")
        print("  • Routage intelligent optimisé")
        return 0
    else:
        print("\n✗ CERTAINS TESTS ONT ÉCHOUÉ")
        return 1

if __name__ == "__main__":
    sys.exit(main())