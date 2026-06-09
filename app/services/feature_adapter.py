"""
SOLITAIRE HACK - Adaptateur de features pour les modèles .pkl
Transforme les features du système vers le format attendu par les modèles .pkl.
"""

from __future__ import annotations

from typing import Dict, Any
import pandas as pd

class FeatureAdapter:
    """
    Adaptateur qui transforme les features standard du système vers le format 
    spécifique attendu par les modèles .pkl (h_*, a_*, diff_*)
    """
    
    # Mapping des features du système vers les features des modèles .pkl
    SYSTEM_TO_PKL_MAPPING = {
        # Features home (h_*)
        'head_to_head_matches': 'h_matches',  # Nombre de matchs entre les équipes
        'home_form_rate': 'h_win_rate',        # Taux de victoire domicile
        'home_attack_avg': 'h_avg_gf',         # Average goals for (home)
        'home_defense_avg': 'h_avg_ga',       # Average goals against (home)
        'home_form_rate': 'h_form_win_rate',  # Form win rate (home)
        'home_attack_avg': 'h_form_avg_gf',   # Form average goals for (home)
        'home_defense_avg': 'h_form_avg_ga',  # Form average goals against (home)
        
        # Features away (a_*)
        'head_to_head_matches': 'a_matches',  # Nombre de matchs entre les équipes
        'away_form_rate': 'a_win_rate',        # Taux de victoire extérieur
        'away_attack_avg': 'a_avg_gf',         # Average goals for (away)
        'away_defense_avg': 'a_avg_ga',       # Average goals against (away)
        'away_form_rate': 'a_form_win_rate',  # Form win rate (away)
        'away_attack_avg': 'a_form_avg_gf',   # Form average goals for (away)
        'away_defense_avg': 'a_form_avg_ga',  # Form average goals against (away)
        
        # Features diff (diff_*)
        # Calculées comme différences entre home et away
    }
    
    @classmethod
    def adapt_features(cls, system_features: Dict[str, Any]) -> Dict[str, float]:
        """
        Transforme les features du système vers le format .pkl.
        
        Args:
            system_features: Dictionnaire des features du système
            
        Returns:
            Dictionnaire des features au format .pkl
        """
        pkl_features = {}
        
        # Features home (h_*)
        pkl_features['h_matches'] = system_features.get('head_to_head_matches', 0)
        pkl_features['h_win_rate'] = system_features.get('home_form_rate', 0.5)
        pkl_features['h_avg_gf'] = system_features.get('home_attack_avg', 1.5)
        pkl_features['h_avg_ga'] = system_features.get('home_defense_avg', 1.5)
        pkl_features['h_avg_goals'] = system_features.get('home_attack_avg', 1.5)  # Approximation
        pkl_features['h_form_win_rate'] = system_features.get('home_form_rate', 0.5)
        pkl_features['h_form_avg_gf'] = system_features.get('home_attack_avg', 1.5)
        pkl_features['h_form_avg_ga'] = system_features.get('home_defense_avg', 1.5)
        
        # Features away (a_*)
        pkl_features['a_matches'] = system_features.get('head_to_head_matches', 0)
        pkl_features['a_win_rate'] = system_features.get('away_form_rate', 0.5)
        pkl_features['a_avg_gf'] = system_features.get('away_attack_avg', 1.5)
        pkl_features['a_avg_ga'] = system_features.get('away_defense_avg', 1.5)
        pkl_features['a_avg_goals'] = system_features.get('away_attack_avg', 1.5)  # Approximation
        pkl_features['a_form_win_rate'] = system_features.get('away_form_rate', 0.5)
        pkl_features['a_form_avg_gf'] = system_features.get('away_attack_avg', 1.5)
        pkl_features['a_form_avg_ga'] = system_features.get('away_defense_avg', 1.5)
        
        # Features diff (diff_*) - Calculées
        pkl_features['diff_win_rate'] = (
            system_features.get('home_form_rate', 0.5) - 
            system_features.get('away_form_rate', 0.5)
        )
        pkl_features['diff_avg_gf'] = (
            system_features.get('home_attack_avg', 1.5) - 
            system_features.get('away_attack_avg', 1.5)
        )
        pkl_features['diff_form'] = (
            system_features.get('home_form_rate', 0.5) - 
            system_features.get('away_form_rate', 0.5)
        )
        
        return pkl_features
    
    @classmethod
    def adapt_dataframe(cls, df: pd.DataFrame, target_features: list[str]) -> pd.DataFrame:
        """
        Adaptte un DataFrame de features du système vers le format .pkl.
        
        Args:
            df: DataFrame avec les features du système
            target_features: Liste des features attendues par le modèle
            
        Returns:
            DataFrame avec les features au format .pkl
        """
        adapted_data = []
        
        for _, row in df.iterrows():
            system_features = row.to_dict()
            pkl_features = cls.adapt_features(system_features)
            adapted_data.append(pkl_features)
        
        adapted_df = pd.DataFrame(adapted_data)
        
        # S'assurer que toutes les colonnes target sont présentes
        for feature in target_features:
            if feature not in adapted_df.columns:
                adapted_df[feature] = 0.0  # Valeur par défaut
        
        # Ne garder que les colonnes demandées
        return adapted_df[target_features]
