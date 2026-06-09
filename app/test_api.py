#!/usr/bin/env python3
"""
Script de test des endpoints API.
SOLITAIRE HACK - Test API
"""

import sys
import io
import requests
import json
from datetime import datetime

# Configuration de l'encodage UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://127.0.0.1:8000"

def test_root_endpoint():
    """Test l'endpoint racine"""
    print("Test: GET /")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"  Erreur: {e}")
        return False

def test_status_endpoint():
    """Test l'endpoint de statut"""
    print("\nTest: GET /api/status")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"  Erreur: {e}")
        return False

def test_models_endpoint():
    """Test l'endpoint des modèles"""
    print("\nTest: GET /api/models")
    try:
        response = requests.get(f"{BASE_URL}/api/models")
        print(f"  Status: {response.status_code}")
        data = response.json()
        print(f"  Nombre de modèles: {len(data.get('models', []))}")
        return response.status_code == 200
    except Exception as e:
        print(f"  Erreur: {e}")
        return False

def test_contexts_endpoint():
    """Test l'endpoint des contextes"""
    print("\nTest: GET /api/models/contexts")
    try:
        response = requests.get(f"{BASE_URL}/api/models/contexts")
        print(f"  Status: {response.status_code}")
        data = response.json()
        print(f"  Contextes disponibles: {data}")
        return response.status_code == 200
    except Exception as e:
        print(f"  Erreur: {e}")
        return False

def test_prediction_endpoint():
    """Test l'endpoint de prédiction"""
    print("\nTest: POST /api/predict")
    try:
        payload = {
            "league": "Champions League",
            "homeTeam": "Real Madrid",
            "awayTeam": "Barcelona",
            "home_odds": 2.1,
            "draw_odds": 3.4,
            "away_odds": 3.2,
            "match_datetime": datetime.now().isoformat(),
            "game_mode": "penalty",
            "game_version": "FC26"
        }
        response = requests.post(f"{BASE_URL}/api/predict", json=payload)
        print(f"  Status: {response.status_code}")
        data = response.json()
        print(f"  Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"  Erreur: {e}")
        return False

def main():
    print("="*60)
    print("SOLITAIRE HACK - Test des endpoints API")
    print("="*60)
    
    tests = [
        ("Root Endpoint", test_root_endpoint),
        ("Status Endpoint", test_status_endpoint),
        ("Models Endpoint", test_models_endpoint),
        ("Contexts Endpoint", test_contexts_endpoint),
        ("Prediction Endpoint", test_prediction_endpoint),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"Erreur critique dans {test_name}: {e}")
            results[test_name] = False
    
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    for test_name, success in results.items():
        status = "✓ SUCCÈS" if success else "✗ ÉCHEC"
        print(f"  {test_name}: {status}")
    
    total_tests = len(results)
    successful_tests = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {successful_tests}/{total_tests} tests réussis")
    
    if successful_tests == total_tests:
        print("\n✓ TOUS LES TESTS RÉUSSIS - SYSTÈME PRÊT POUR LA PRODUCTION")
        return 0
    else:
        print("\n✗ CERTAINS TESTS ONT ÉCHOUÉ - VÉRIFICATION REQUISE")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
