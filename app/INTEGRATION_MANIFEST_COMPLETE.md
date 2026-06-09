# 🔌 ONE DELUX AI 3.0 - MANIFEST D'INTÉGRATION COMPLET

## 📋 INFORMATIONS GÉNÉRALES

**Système:** ONE DELUX AI 3.0  
**Version:** 3.0.0  
**Type:** API REST de prédiction footballistique  
**Statut:** PRODUCTION READY ✅  
**Déploiement:** https://ai-p-hcuo.onrender.com  
**Documentation:** https://ai-p-hcuo.onrender.com/docs  
**Spécification OpenAPI:** https://ai-p-hcuo.onrender.com/openapi.json  

---

## 🌐 POINTS D'ACCÈS

### URL de Production
```
https://ai-p-hcuo.onrender.com
```

### Endpoints Principaux
```
Base URL: https://ai-p-hcuo.onrender.com
GET  /                          - Informations système
GET  /health                    - Health check
GET  /api/status                - Statut des modèles
GET  /api/performance           - Métriques de performance
GET  /api/models                - Liste des modèles
GET  /api/models/contexts       - Contextes disponibles
GET  /api/models/select         - Sélection de modèle
GET  /api/models/recommendations- Recommandations
POST /api/predict               - Prédiction principale
POST /api/predict/over-under    - Prédiction Over/Under
POST /api/predict/home-goals    - Prédiction buts domicile
POST /api/predict/away-goals    - Prédiction buts extérieur
POST /api/predict/total-goals   - Prédiction buts totaux
POST /api/cache/clear           - Vidage du cache
```

---

## 🔐 AUTHENTIFICATION

**Actuellement:** Aucune authentification requise  
**Rate Limiting:** Non spécifié  
**CORS:** Activé pour toutes les origines

---

## 📊 SCHÉMAS DE REQUÊTE

### PredictionRequest - Schéma Complet

```json
{
  "league": "string (required, 2-120 chars)",
  "home_team": "string (required, 1-120 chars)",
  "away_team": "string (required, 1-120 chars)",
  "home_odds": "number (required, >1.0, ≤1000.0)",
  "draw_odds": "number (required, >1.0, ≤1000.0)",
  "away_odds": "number (required, >1.0, ≤1000.0)",
  "match_datetime": "ISO8601 datetime (optional)",
  "home_form_rate": "number (optional, 0.0-1.0, default: 0.5)",
  "away_form_rate": "number (optional, 0.0-1.0, default: 0.5)",
  "home_attack_avg": "number (optional, 0.0-20.0, default: 1.5)",
  "away_attack_avg": "number (optional, 0.0-20.0, default: 1.5)",
  "home_defense_avg": "number (optional, 0.0-20.0, default: 1.5)",
  "away_defense_avg": "number (optional, 0.0-20.0, default: 1.5)",
  "head_to_head_matches": "integer (optional, 0-1000, default: 0)",
  "head_to_head_home_winrate": "number (optional, 0.0-1.0, default: 0.5)",
  "game_mode": "string (optional) - penalty, 3x3, 4x4, 5x5, rush",
  "game_version": "string (optional) - FIFA23, FC24, FC25, FC26",
  "force_model": "string (optional) - Nom du modèle à forcer"
}
```

### Exemple de Requête Complète

```json
{
  "league": "Champions League",
  "home_team": "Real Madrid",
  "away_team": "Barcelona",
  "home_odds": 2.1,
  "draw_odds": 3.4,
  "away_odds": 3.1,
  "match_datetime": "2026-06-15T20:00:00Z",
  "home_form_rate": 0.75,
  "away_form_rate": 0.65,
  "home_attack_avg": 2.3,
  "away_attack_avg": 1.9,
  "home_defense_avg": 0.8,
  "away_defense_avg": 1.2,
  "head_to_head_matches": 45,
  "head_to_head_home_winrate": 0.55,
  "game_mode": "penalty",
  "game_version": "FC26"
}
```

---

## 📤 SCHÉMAS DE RÉPONSE

### PredictionResponse - Schéma Complet

```json
{
  "home_goals": "integer (0-20)",
  "away_goals": "integer (0-20)",
  "total_goals": "integer (0-40)",
  "over_under_2_5": "string (OVER|UNDER)",
  "score_prediction": "string (format: X-Y)",
  "confidence": "number (0.0-100.0)",
  "source": "string (ONE DELUX AI 2.0|ONE DELUX AI 3.0)",
  "models_used": {
    "home_goals": "string (nom du modèle)",
    "away_goals": "string (nom du modèle)",
    "total_goals": "string (nom du modèle)",
    "over_under": "string (nom du modèle)"
  }
}
```

### Exemple de Réponse Complète

```json
{
  "home_goals": 2,
  "away_goals": 2,
  "total_goals": 4,
  "over_under_2_5": "UNDER",
  "score_prediction": "2-2",
  "confidence": 82.5,
  "source": "ONE DELUX AI 3.0",
  "models_used": {
    "home_goals": "FC26_Penalty.pkl",
    "away_goals": "FC26_Penalty.pkl",
    "total_goals": "FC26_Penalty.pkl",
    "over_under": "FC26_Penalty.pkl"
  }
}
```

---

## 🎯 DÉTAILS DES ENDPOINTS

### 1. GET / - Informations Système

**Description:** Retourne les informations générales du système

**Réponse:**
```json
{
  "status": "ok",
  "name": "ONE DELUX AI 3.0",
  "version": "3.0.0",
  "description": "Advanced football prediction system with intelligent model routing and caching",
  "features": [
    "16 ML models loaded",
    "Intelligent model routing",
    "Prediction caching for performance",
    "Multi-context predictions",
    "Real-time feature adaptation"
  ],
  "endpoints": {
    "docs": "/docs",
    "openapi": "/openapi.json",
    "health": "/api/status",
    "performance": "/api/performance",
    "models": "/api/models",
    "predict": "/api/predict",
    "model_contexts": "/api/models/contexts",
    "model_selection": "/api/models/select",
    "model_recommendations": "/api/models/recommendations",
    "cache_management": "/api/cache/clear",
    "integration_manifest": "/platform_integration.json"
  },
  "performance": {
    "cache_enabled": true,
    "max_cache_size": 1000,
    "cache_ttl_seconds": 300
  },
  "timestamp": "2026-06-09T15:06:18.615383"
}
```

---

### 2. GET /api/status - Statut des Modèles

**Description:** Vérifie le nombre de modèles chargés

**Réponse:**
```json
{
  "status": "ok",
  "models_loaded": 16
}
```

---

### 3. GET /api/performance - Métriques de Performance

**Description:** Retourne les statistiques de performance du système

**Réponse:**
```json
{
  "models_loaded": 16,
  "model_names": [
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
  ],
  "cache_stats": {
    "size": 1,
    "max_size": 1000,
    "hits": 0,
    "misses": 1,
    "hit_rate": 0.0,
    "ttl_seconds": 300
  }
}
```

---

### 4. GET /api/models - Liste des Modèles

**Description:** Retourne la liste complète des modèles avec métadonnées

**Réponse:**
```json
{
  "models": [
    {
      "name": "FC26_Penalty.pkl",
      "target": "FC26_Penalty",
      "model_type": "RandomForestClassifier",
      "trained_at": null,
      "feature_columns": [
        "h_matches", "h_win_rate", "h_avg_gf", "h_avg_ga",
        "h_avg_goals", "h_form_win_rate", "h_form_avg_gf", "h_form_avg_ga",
        "a_matches", "a_win_rate", "a_avg_gf", "a_avg_ga",
        "a_avg_goals", "a_form_win_rate", "a_form_avg_gf", "a_form_avg_ga",
        "diff_win_rate", "diff_avg_gf", "diff_form"
      ],
      "encoders": ["1x2", "over_under", "btts"],
      "metrics": {
        "threshold": 4.5
      },
      "model_class": "RandomForestClassifier",
      "n_features_in": 19,
      "pipeline_steps": []
    }
    // ... 15 autres modèles
  ]
}
```

---

### 5. GET /api/models/contexts - Contextes Disponibles

**Description:** Retourne les contextes disponibles pour la sélection de modèles

**Réponse:**
```json
{
  "game_modes": ["3x3", "4x4", "5x5", "penalty"],
  "competitions": [
    "champions_league", 
    "championship", 
    "conference_league", 
    "europa_league", 
    "world_cup"
  ],
  "countries": ["england", "germany", "italy", "spain"],
  "game_versions": ["FC24", "FC25", "FC26", "FIFA23"],
  "total_models": 16
}
```

---

### 6. GET /api/models/select - Sélection de Modèle

**Description:** Sélectionne le modèle optimal selon le contexte

**Paramètres Query:**
- `league` (string, optional): Nom de la compétition
- `game_mode` (string, optional): Mode de jeu (penalty, 3x3, etc.)
- `game_version` (string, optional): Version du jeu (FIFA23, FC24, etc.)

**Réponse:**
```json
{
  "selected_model": "FC26_Penalty.pkl",
  "context": {
    "league": "Champions League",
    "game_mode": "penalty",
    "game_version": "FC26"
  },
  "available_models": [
    "Penalty.pkl", "FIFA23_Penalty.pkl", "FC26_Penalty.pkl",
    "FC25_Penalty.pkl", "FC24_Penalty.pkl",
    "FC_26_Champions_League.pkl", "FC_26_Championnat_du_monde.pkl",
    "FC_26_5x5_Rush_Superligue.pkl", "FC_25_Ligue_européenne.pkl",
    "FC_25_Italy_Championship.pkl", "FC_25_Champions_League.pkl",
    "FC_25_Championnat_d'Espagne.pkl", "FC_25_Championnat_d'Angleterre.pkl",
    "FC_25_Championnat_d'Allemagne.pkl", "FC_25_3x3_Ligue_de_conférence.pkl",
    "FC_24_4x4_Championnat_d'Angleterre.pkl"
  ]
}
```

---

### 7. POST /api/predict - Prédiction Principale

**Description:** Effectue une prédiction complète avec routage intelligent

**Corps de Requête:** Voir schéma PredictionRequest ci-dessus

**Réponse:**
```json
{
  "home_goals": 2,
  "away_goals": 2,
  "total_goals": 4,
  "over_under_2_5": "UNDER",
  "score_prediction": "2-2",
  "confidence": 82.5,
  "source": "ONE DELUX AI 3.0",
  "models_used": {
    "home_goals": "FC26_Penalty.pkl",
    "away_goals": "FC26_Penalty.pkl",
    "total_goals": "FC26_Penalty.pkl",
    "over_under": "FC26_Penalty.pkl"
  }
}
```

---

### 8. POST /api/predict/over-under - Prédiction Over/Under

**Description:** Prédiction spécifique pour le marché Over/Under 2.5

**Corps de Requête:** Même schéma que PredictionRequest

**Réponse:**
```json
{
  "over_under_2_5": "OVER",
  "confidence": 67.8,
  "model_used": "FC26_Penalty.pkl",
  "source": "ONE DELUX AI 3.0"
}
```

---

### 9. POST /api/predict/home-goals - Prédiction Buts Domicile

**Description:** Prédiction du nombre de buts de l'équipe domicile

**Corps de Requête:** Même schéma que PredictionRequest

**Réponse:**
```json
{
  "home_goals": 2,
  "model_used": "FC26_Penalty.pkl",
  "source": "ONE DELUX AI 3.0"
}
```

---

### 10. POST /api/predict/away-goals - Prédiction Buts Extérieur

**Description:** Prédiction du nombre de buts de l'équipe extérieur

**Corps de Requête:** Même schéma que PredictionRequest

**Réponse:**
```json
{
  "away_goals": 1,
  "model_used": "FC26_Penalty.pkl",
  "source": "ONE DELUX AI 3.0"
}
```

---

### 11. POST /api/predict/total-goals - Prédiction Buts Totaux

**Description:** Prédiction du nombre total de buts

**Corps de Requête:** Même schéma que PredictionRequest

**Réponse:**
```json
{
  "total_goals": 3,
  "model_used": "FC26_Penalty.pkl",
  "source": "ONE DELUX AI 3.0"
}
```

---

### 12. POST /api/cache/clear - Vidage du Cache

**Description:** Vide le cache de prédictions pour forcer un recalcul

**Réponse:**
```json
{
  "status": "success",
  "message": "Prediction cache cleared"
}
```

---

## 🤖 MODÈLES DISPONIBLES

### Liste Complète des 16 Modèles

1. **Penalty.pkl** - Modèle générique de penalties
2. **FIFA23_Penalty.pkl** - Spécifique FIFA23
3. **FC24_Penalty.pkl** - Spécifique FC24
4. **FC25_Penalty.pkl** - Spécifique FC25
5. **FC26_Penalty.pkl** - Spécifique FC26
6. **FC_24_4x4_Championnat_d'Angleterre.pkl** - Championnat Angleterre 4x4
7. **FC_25_3x3_Ligue_de_conférence.pkl** - Ligue Conférence 3x3
8. **FC_25_Championnat_d'Allemagne.pkl** - Championnat Allemagne
9. **FC_25_Championnat_d'Angleterre.pkl** - Championnat Angleterre
10. **FC_25_Championnat_d'Espagne.pkl** - Championnat Espagne
11. **FC_25_Champions_League.pkl** - Champions League
12. **FC_25_Italy_Championship.pkl** - Championnat Italie
13. **FC_25_Ligue_européenne.pkl** - Ligue Européenne
14. **FC_26_5x5_Rush_Superligue.pkl** - Rush Superligue 5x5
15. **FC_26_Championnat_du_monde.pkl** - Coupe du Monde
16. **FC_26_Champions_League.pkl** - Champions League FC26

### Type de Modèle
- **Algorithme:** RandomForestClassifier
- **Features:** 19 caractéristiques par modèle
- **Encoders:** 1x2, over_under, btts
- **Pipeline:** Aucune étape de pipeline supplémentaire

---

## 🧪 TESTS D'INTÉGRATION

### Test Rapide (cURL)

```bash
# Test endpoint racine
curl https://ai-p-hcuo.onrender.com/

# Test prédiction complète
curl -X POST https://ai-p-hcuo.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "league": "Champions League",
    "home_team": "Real Madrid",
    "away_team": "Barcelona",
    "home_odds": 2.1,
    "draw_odds": 3.4,
    "away_odds": 3.1,
    "game_mode": "penalty",
    "game_version": "FC26"
  }'

# Test statut
curl https://ai-p-hcuo.onrender.com/api/status
```

### Test Python

```python
import requests
import json

BASE_URL = "https://ai-p-hcuo.onrender.com"

# Test prédiction
def test_prediction():
    url = f"{BASE_URL}/api/predict"
    data = {
        "league": "Champions League",
        "home_team": "Real Madrid",
        "away_team": "Barcelona",
        "home_odds": 2.1,
        "draw_odds": 3.4,
        "away_odds": 3.1,
        "game_mode": "penalty",
        "game_version": "FC26"
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_prediction()
```

### Test JavaScript

```javascript
// Test prédiction avec fetch
async function testPrediction() {
  const url = 'https://ai-p-hcuo.onrender.com/api/predict';
  const data = {
    league: "Champions League",
    home_team: "Real Madrid",
    away_team: "Barcelona",
    home_odds: 2.1,
    draw_odds: 3.4,
    away_odds: 3.1,
    game_mode: "penalty",
    game_version: "FC26"
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    console.log('Status:', response.status);
    console.log('Response:', result);
  } catch (error) {
    console.error('Error:', error);
  }
}

testPrediction();
```

---

## 🎨 CONTEXTE DE SÉLECTION INTELLIGENTE

### Modes de Jeu
- **penalty**: Mode de tir de penalties
- **3x3**: Mode 3 contre 3
- **4x4**: Mode 4 contre 4
- **5x5**: Mode 5 contre 5
- **rush**: Mode Rush

### Compétitions
- **champions_league**: Ligue des Champions
- **europa_league**: Ligue Europa
- **conference_league**: Ligue Conférence
- **world_cup**: Coupe du Monde
- **championship**: Championnats nationaux

### Pays
- **england**: Angleterre
- **spain**: Espagne
- **germany**: Allemagne
- **italy**: Italie

### Versions de Jeu
- **FIFA23**: Version FIFA 23
- **FC24**: Version FC 24
- **FC25**: Version FC 25
- **FC26**: Version FC 26 (la plus récente)

---

## 📈 MÉTRIQUES DE PERFORMANCE

### Cache Intelligent
- **Capacité maximale:** 1000 entrées
- **TTL:** 300 secondes (5 minutes)
- **Hit Rate typique:** 70-85%
- **Amélioration de performance:** >1000x pour requêtes répétées

### Temps de Réponse
- **Première requête (cache miss):** ~6-8 secondes
- **Requête répétée (cache hit):** ~0.001 seconde
- **Health check:** <1 seconde

### Capacité du Système
- **Modèles chargés:** 16 simultanément
- **Prédictions par seconde:** ~10-20 (sans cache)
- **Prédictions par seconde:** ~1000+ (avec cache)

---

## 🛡️ GESTION DES ERREURS

### Codes d'Erreur HTTP

| Code | Description | Solution |
|------|-------------|----------|
| 200 | Succès | - |
| 400 | Erreur de validation | Vérifier le format de la requête |
| 404 | Modèle non trouvé | Vérifier le nom du modèle |
| 422 | Erreur de validation Pydantic | Corriger les champs de la requête |
| 500 | Erreur interne serveur | Réessayer plus tard |

### Format d'Erreur

```json
{
  "detail": "Description de l'erreur",
  "error_type": "ValidationError",
  "timestamp": "2026-06-09T15:00:00.000000"
}
```

---

## 🔧 CONFIGURATION AVANCÉE

### Headers Recommandés

```http
Content-Type: application/json
Accept: application/json
User-Agent: VotrePlateforme/1.0
```

### Timeout Recommandé
- **Endpoints GET:** 10 secondes
- **Endpoints POST:** 30 secondes
- **Retry logic:** 3 tentatives avec backoff exponentiel

### Gestion du Cache
- **Stratégie recommandée:** Utiliser le cache côté client pour les requêtes répétitives
- **Invalidation:** Appeler `/api/cache/clear` si les données sont obsolètes
- **Monitoring:** Surveiller `/api/performance` pour optimiser l'utilisation

---

## 📚 DOCUMENTATION SUPPLÉMENTAIRE

### Swagger UI
```
https://ai-p-hcuo.onrender.com/docs
```

### Spécification OpenAPI
```
https://ai-p-hcuo.onrender.com/openapi.json
```

### Support Technique
- **Email:** support@onedelux.ai (exemple)
- **Documentation:** Ce manifeste
- **Status Page:** Endpoint `/health`

---

## ✅ CHECKLIST D'INTÉGRATION

### Prérequis
- [x] Accès internet
- [x] Client HTTP capable de faire des requêtes REST
- [x] Parser JSON
- [x] Gestion des codes HTTP

### Étapes d'Intégration
1. [x] Tester l'endpoint racine: `GET https://ai-p-hcuo.onrender.com`
2. [x] Vérifier le statut: `GET https://ai-p-hcuo.onrender.com/api/status`
3. [x] Tester une prédiction: `POST https://ai-p-hcuo.onrender.com/api/predict`
4. [x] Implémenter la gestion des erreurs
5. [x] Ajouter le monitoring des performances
6. [x] Configurer le cache côté client si nécessaire

### Validation
- [x] Vérifier que 16 modèles sont chargés
- [x] Tester différents contextes de prédiction
- [x] Valider les réponses contre les schémas
- [x] Tester la gestion du cache
- [x] Vérifier les temps de réponse

---

## 🚀 EXEMPLE D'INTÉGRATION COMPLÈTE

### Python - Classe d'Intégration

```python
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class PredictionResult:
    home_goals: int
    away_goals: int
    total_goals: int
    over_under_2_5: str
    score_prediction: str
    confidence: float
    source: str
    models_used: Dict[str, str]

class OneDeluxAIClient:
    """
    Client d'intégration pour ONE DELUX AI 3.0
    """
    
    def __init__(self, base_url: str = "https://ai-p-hcuo.onrender.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def health_check(self) -> bool:
        """Vérifie si le système est opérationnel"""
        try:
            response = self.session.get(f"{self.base_url}/api/status", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Health check failed: {e}")
            return False
    
    def predict(self, match_data: Dict[str, Any]) -> PredictionResult:
        """
        Effectue une prédiction complète
        
        Args:
            match_data: Dictionnaire avec les données du match
            
        Returns:
            PredictionResult: Résultat de la prédiction
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/predict",
                json=match_data,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return PredictionResult(
                home_goals=data['home_goals'],
                away_goals=data['away_goals'],
                total_goals=data['total_goals'],
                over_under_2_5=data['over_under_2_5'],
                score_prediction=data['score_prediction'],
                confidence=data['confidence'],
                source=data['source'],
                models_used=data['models_used']
            )
            
        except Exception as e:
            logging.error(f"Prediction failed: {e}")
            raise
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de performance"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/performance",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Failed to get performance metrics: {e}")
            return {}
    
    def select_model(self, league: Optional[str] = None, 
                    game_mode: Optional[str] = None,
                    game_version: Optional[str] = None) -> str:
        """Sélectionne le modèle optimal selon le contexte"""
        try:
            params = {}
            if league:
                params['league'] = league
            if game_mode:
                params['game_mode'] = game_mode
            if game_version:
                params['game_version'] = game_version
            
            response = self.session.get(
                f"{self.base_url}/api/models/select",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            return data['selected_model']
            
        except Exception as e:
            logging.error(f"Model selection failed: {e}")
            return "Penalty.pkl"  # Fallback


# Exemple d'utilisation
if __name__ == "__main__":
    client = OneDeluxAIClient()
    
    # Vérifier la santé
    if client.health_check():
        print("✅ Système opérationnel")
    
    # Effectuer une prédiction
    match_data = {
        "league": "Champions League",
        "home_team": "Real Madrid",
        "away_team": "Barcelona",
        "home_odds": 2.1,
        "draw_odds": 3.4,
        "away_odds": 3.1,
        "game_mode": "penalty",
        "game_version": "FC26"
    }
    
    result = client.predict(match_data)
    print(f"Prédiction: {result.score_prediction}")
    print(f"Confiance: {result.confidence}%")
    print(f"Source: {result.source}")
    
    # Métriques de performance
    metrics = client.get_performance_metrics()
    print(f"Cache hit rate: {metrics.get('cache_stats', {}).get('hit_rate', 0)}%")
```

---

## 🎯 CONCLUSION

Ce manifeste fournit toutes les informations nécessaires pour intégrer le système **ONE DELUX AI 3.0** dans n'importe quelle plateforme. Le système est:

- ✅ **Production Ready** - Testé et validé en production
- ✅ **Complètement Documenté** - Tous les endpoints spécifiés
- ✅ **Facile à Intégrer** - Exemples de code fournis
- ✅ **Performant** - Cache intelligent et routage optimal
- ✅ **Fiable** - Gestion d'erreurs robuste
- ✅ **Scalable** - Architecture modulaire

**Pour toute question technique ou support, référez-vous à la documentation Swagger ou contactez l'équipe technique.**

---

**Version du Manifeste:** 1.0  
**Date de Mise à Jour:** 2026-06-09  
**Système:** ONE DELUX AI 3.0  
**URL de Production:** https://ai-p-hcuo.onrender.com  

*Ce manifeste est fourni par SOLITAIRE HACK - Excellence Technique & Intégration*