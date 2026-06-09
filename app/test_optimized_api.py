#!/usr/bin/env python3
"""
Script de test pour les API optimisées
SOLITAIRE HACK - Test des nouvelles fonctionnalités
"""

import sys
import os
import io
import time
import requests

# Rediriger stdout pour éviter les problèmes d'encodage
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(endpoint, description):
    """Test un endpoint et affiche le résultat"""
    try:
        print(f"\nTest: {description}")
        print(f"Endpoint: {endpoint}")
        
        start_time = time.time()
        if endpoint.startswith("/api/predict"):
            # Pour les endpoints POST, créer une requête de test
            from datetime import datetime
            payload = {
                "league": "Test League",
                "homeTeam": "Team A",
                "awayTeam": "Team B",
                "home_odds": 2.5,
                "draw_odds": 3.2,
                "away_odds": 2.8,
                "match_datetime": datetime.now().isoformat(),
                "game_mode": "penalty",
                "game_version": "FC26"
            }
            response = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=10)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        
        elapsed = time.time() - start_time
        
        print(f"  Status: {response.status_code}")
        print(f"  Temps: {elapsed:.3f}s")
        
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"  Exception: {e}")
        return False

def main():
    print("="*60)
    print("SOLITAIRE HACK - Test des API Optimisées")
    print("="*60)
    
    # Attendre que le serveur soit prêt
    print("\nAttente du serveur...")
    time.sleep(2)
    
    tests = [
        ("/", "Endpoint racine avec informations de performance"),
        ("/api/status", "Endpoint de statut"),
        ("/api/performance", "Endpoint de performance (NOUVEAU)"),
        ("/api/models", "Endpoint des modèles"),
        ("/api/models/contexts", "Endpoint des contextes"),
        ("/api/models/select?game_mode=penalty", "Endpoint de sélection de modèle"),
        ("/api/predict", "Endpoint de prédiction (fusion)"),
    ]
    
    results = []
    for endpoint, description in tests:
        success = test_endpoint(endpoint, description)
        results.append((description, success))
        time.sleep(0.5)  # Pause entre les tests
    
    # Test du cache
    print("\n" + "="*60)
    print("Test du Cache de Prédictions")
    print("="*60)
    
    print("\nPremière requête (devrait être un miss de cache):")
    test_endpoint("/api/predict", "Prédiction #1")
    
    print("\nDeuxième requête identique (devrait être un hit de cache):")
    test_endpoint("/api/predict", "Prédiction #2")
    
    print("\nVérification des statistiques de cache:")
    test_endpoint("/api/performance", "Statistiques de cache")
    
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    
    for description, success in results:
        status = "✓ SUCCÈS" if success else "✗ ÉCHEC"
        print(f"{status}: {description}")
    
    total = len(results)
    successful = sum(1 for _, success in results if success)
    
    print(f"\nTotal: {successful}/{total} tests réussis")
    
    if successful == total:
        print("\n✓ TOUS LES TESTS RÉUSSIS - SYSTÈME OPTIMISÉ OPÉRATIONNEL")
    else:
        print(f"\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")

if __name__ == "__main__":
    main()