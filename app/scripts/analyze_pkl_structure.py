#!/usr/bin/env python3
"""
Script d'analyse des fichiers .pkl pour comprendre leur structure interne.
SOLITAIRE HACK - Analyse de structure
"""

import pickle
import joblib
from pathlib import Path
import sys

def analyze_pkl_file(pkl_path: Path) -> dict:
    """Analyse la structure d'un fichier .pkl"""
    print(f"\n{'='*60}")
    print(f"Analyse de: {pkl_path.name}")
    print(f"{'='*60}")
    
    try:
        # Essayer pickle d'abord
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f)
        
        print(f"✓ Chargé avec pickle")
        print(f"Type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Clés: {list(data.keys())}")
            for key, value in data.items():
                print(f"  - {key}: {type(value)}")
                if hasattr(value, '__class__'):
                    print(f"    Classe: {value.__class__.__name__}")
                    if hasattr(value, 'n_features_in_'):
                        print(f"    n_features_in_: {value.n_features_in_}")
                    if hasattr(value, 'classes_'):
                        print(f"    classes_: {value.classes_}")
        elif hasattr(data, '__class__'):
            print(f"Classe: {data.__class__.__name__}")
            if hasattr(data, 'n_features_in_'):
                print(f"n_features_in_: {data.n_features_in_}")
            if hasattr(data, 'classes_'):
                print(f"classes_: {data.classes_}")
            if hasattr(data, 'feature_names_in_'):
                print(f"feature_names_in_: {data.feature_names_in_}")
        
        return {"status": "success", "type": "pickle", "data_type": str(type(data))}
        
    except Exception as e:
        print(f"✗ Erreur avec pickle: {e}")
        
        try:
            # Essayer joblib
            data = joblib.load(pkl_path)
            print(f"✓ Chargé avec joblib")
            print(f"Type: {type(data)}")
            
            if isinstance(data, dict):
                print(f"Clés: {list(data.keys())}")
            elif hasattr(data, '__class__'):
                print(f"Classe: {data.__class__.__name__}")
                if hasattr(data, 'n_features_in_'):
                    print(f"n_features_in_: {data.n_features_in_}")
            
            return {"status": "success", "type": "joblib", "data_type": str(type(data))}
            
        except Exception as e2:
            print(f"✗ Erreur avec joblib: {e2}")
            return {"status": "error", "error": str(e2)}

def main():
    models_dir = Path(__file__).parent.parent / "models"
    
    if not models_dir.exists():
        print(f"Erreur: Répertoire models non trouvé: {models_dir}")
        sys.exit(1)
    
    pkl_files = list(models_dir.glob("*.pkl"))
    
    if not pkl_files:
        print("Aucun fichier .pkl trouvé")
        sys.exit(0)
    
    print(f"Trouvé {len(pkl_files)} fichiers .pkl")
    
    results = {}
    for pkl_file in sorted(pkl_files):
        results[pkl_file.name] = analyze_pkl_file(pkl_file)
    
    print(f"\n{'='*60}")
    print("RÉSUMÉ")
    print(f"{'='*60}")
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    print(f"Succès: {success_count}/{len(results)}")
    
    for name, result in results.items():
        status_icon = "✓" if result["status"] == "success" else "✗"
        print(f"{status_icon} {name}: {result.get('type', 'error')}")

if __name__ == "__main__":
    main()
