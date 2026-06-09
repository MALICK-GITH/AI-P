#!/usr/bin/env python3
"""
Script de diagnostic rapide pour vérifier l'état des modèles
SOLITAIRE HACK - Diagnostic Rapide
"""

import sys
import os
import io
from pathlib import Path

# Rediriger stdout pour éviter les problèmes d'encodage
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def check_models_directory():
    """Vérifie que tous les fichiers modèles existent"""
    print("="*60)
    print("DIAGNOSTIC: Vérification des fichiers modèles")
    print("="*60)
    
    models_dir = Path("models")
    if not models_dir.exists():
        print("✗ Dossier models introuvable")
        return False
    
    # Liste des modèles attendus
    expected_models = [
        "Penalty.pkl",
        "FIFA23_Penalty.pkl", 
        "FC26_Penalty.pkl",
        "FC25_Penalty.pkl",
        "FC24_Penalty.pkl",
        "FC_26_Champions_League.pkl",
        "FC_26_Championnat_du_monde.pkl",
        "FC_26_5x5_Rush_Superligue.pkl",
        "FC_25_Ligue_européenne.pkl",
        "FC_25_Italy_Championship.pkl",
        "FC_25_Champions_League.pkl",
        "FC_25_Championnat_d'Espagne.pkl",
        "FC_25_Championnat_d'Angleterre.pkl",
        "FC_25_Championnat_d'Allemagne.pkl",
        "FC_25_3x3_Ligue_de_conférence.pkl",
        "FC_24_4x4_Championnat_d'Angleterre.pkl"
    ]
    
    found_models = []
    missing_models = []
    
    for model_name in expected_models:
        model_path = models_dir / model_name
        if model_path.exists():
            size = model_path.stat().st_size
            found_models.append((model_name, size))
            print(f"✓ {model_name:50} ({size:,} bytes)")
        else:
            missing_models.append(model_name)
            print(f"✗ {model_name:50} (MANQUANT)")
    
    print(f"\nRésumé:")
    print(f"  Modèles trouvés: {len(found_models)}/{len(expected_models)}")
    print(f"  Modèles manquants: {len(missing_models)}")
    
    if missing_models:
        print(f"\n⚠️  Modèles manquants: {missing_models}")
        return False
    
    return True

def check_api_files():
    """Vérifie que tous les fichiers API existent"""
    print("\n" + "="*60)
    print("DIAGNOSTIC: Vérification des fichiers API")
    print("="*60)
    
    required_files = [
        "main.py",
        "run_server.py",
        "core/model_loader.py",
        "services/prediction_service.py",
        "services/model_router.py",
        "services/feature_builder.py",
        "services/fusion_engine.py",
        "routers/predict.py",
        "routers/models.py",
        "routers/status.py",
        "routers/model_context.py",
        "schemas/request_schema.py",
        "schemas/response_schema.py"
    ]
    
    all_good = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (MANQUANT)")
            all_good = False
    
    return all_good

def check_dependencies():
    """Vérifie les dépendances Python"""
    print("\n" + "="*60)
    print("DIAGNOSTIC: Vérification des dépendances")
    print("="*60)
    
    required_packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"), 
        ("joblib", "joblib"),
        ("pydantic", "pydantic"),
        ("numpy", "numpy"),
        ("scikit-learn", "sklearn")
    ]
    
    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} (MANQUANT)")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Paquets manquants: {missing}")
        return False
    
    return True

def main():
    print("SOLITAIRE HACK - Diagnostic Rapide du Système")
    print("="*60)
    
    models_ok = check_models_directory()
    api_ok = check_api_files()
    deps_ok = check_dependencies()
    
    print("\n" + "="*60)
    print("RÉSUMÉ DU DIAGNOSTIC")
    print("="*60)
    print(f"Fichiers modèles: {'✓ OK' if models_ok else '✗ ÉCHEC'}")
    print(f"Fichiers API: {'✓ OK' if api_ok else '✗ ÉCHEC'}")
    print(f"Dépendances: {'✓ OK' if deps_ok else '✗ ÉCHEC'}")
    
    if models_ok and api_ok and deps_ok:
        print("\n✓ SYSTÈME PRÊT - Tous les composants sont présents")
        return 0
    else:
        print("\n✗ SYSTÈME INCOMPLET - Certains composants sont manquants")
        return 1

if __name__ == "__main__":
    sys.exit(main())