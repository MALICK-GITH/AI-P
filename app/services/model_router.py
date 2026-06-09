"""
SOLITAIRE HACK - Système de routage intelligent de modèles
Sélectionne automatiquement le modèle le plus approprié selon le contexte.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional
from app.core.model_loader import ModelRegistry

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ModelSelectionCriteria:
    """Critères pour la sélection de modèle"""
    game_mode: Optional[str] = None  # "penalty", "3x3", "4x4", "5x5"
    competition: Optional[str] = None  # "champions_league", "world_cup", etc.
    country: Optional[str] = None  # "england", "spain", "germany", "italy"
    game_version: Optional[str] = None  # "FIFA23", "FC24", "FC25", "FC26"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "game_mode": self.game_mode,
            "competition": self.competition,
            "country": self.country,
            "game_version": self.game_version,
        }


class ModelRouter:
    """
    Routeur intelligent pour la sélection de modèles selon le contexte.
    Analyse les requêtes et les métadonnées de modèles pour faire la meilleure sélection.
    """
    
    def __init__(self, registry: ModelRegistry) -> None:
        self._registry = registry
        self._model_index = self._build_model_index()
        
    def _build_model_index(self) -> Dict[str, ModelSelectionCriteria]:
        """
        Analyse les noms de modèles pour extraire leurs caractéristiques.
        SOLITAIRE HACK: Parsing intelligent des noms de fichiers
        """
        index = {}
        
        for model_name in self._registry.model_names:
            criteria = self._parse_model_name(model_name)
            index[model_name] = criteria
            logger.debug(f"Model {model_name} -> {criteria.to_dict()}")
            
        return index
    
    def _parse_model_name(self, model_name: str) -> ModelSelectionCriteria:
        """
        Extrait les caractéristiques d'un modèle depuis son nom de fichier.
        SOLITAIRE HACK: Pattern matching robuste
        """
        name_lower = model_name.lower()
        
        # Détection du mode de jeu
        game_mode = None
        if "penalty" in name_lower:
            game_mode = "penalty"
        elif "3x3" in name_lower or "3x3" in model_name:
            game_mode = "3x3"
        elif "4x4" in name_lower or "4x4" in model_name:
            game_mode = "4x4"
        elif "5x5" in name_lower or "5x5" in model_name:
            game_mode = "5x5"
        elif "rush" in name_lower:
            game_mode = "rush"
            
        # Détection de la compétition
        competition = None
        if "champions_league" in name_lower or "champions league" in name_lower:
            competition = "champions_league"
        elif "ligue_europ" in name_lower or "europ" in name_lower:
            competition = "europa_league"
        elif "ligue_de_conf" in name_lower or "conference" in name_lower:
            competition = "conference_league"
        elif "championnat_du_monde" in name_lower or "world_cup" in name_lower:
            competition = "world_cup"
        elif "championship" in name_lower:
            competition = "championship"
            
        # Détection du pays
        country = None
        if "angleterre" in name_lower or "england" in name_lower:
            country = "england"
        elif "espagne" in name_lower or "spain" in name_lower:
            country = "spain"
        elif "allemagne" in name_lower or "germany" in name_lower:
            country = "germany"
        elif "italy" in name_lower or "italie" in name_lower:
            country = "italy"
            
        # Détection de la version du jeu
        game_version = None
        if "fifa23" in name_lower:
            game_version = "FIFA23"
        elif "fc24" in name_lower:
            game_version = "FC24"
        elif "fc25" in name_lower:
            game_version = "FC25"
        elif "fc26" in name_lower:
            game_version = "FC26"
            
        return ModelSelectionCriteria(
            game_mode=game_mode,
            competition=competition,
            country=country,
            game_version=game_version,
        )
    
    def select_model_for_context(
        self, 
        league: str = None,
        game_mode: str = None,
        game_version: str = None,
        fallback: str = None
    ) -> str:
        """
        Sélectionne le modèle le plus approprié pour un contexte donné.
        
        Args:
            league: Nom de la ligue/compétition
            game_mode: Mode de jeu (penalty, 3x3, etc.)
            game_version: Version du jeu (FIFA23, FC24, etc.)
            fallback: Modèle par défaut si aucune correspondance
            
        Returns:
            Nom du fichier modèle à utiliser
        """
        if not self._model_index:
            logger.warning("No models available in registry")
            return fallback or list(self._registry.artifacts.keys())[0] if self._registry.artifacts else None
            
        # Normaliser les critères de recherche
        search_criteria = ModelSelectionCriteria(
            game_mode=game_mode,
            competition=self._extract_competition_from_league(league) if league else None,
            country=self._extract_country_from_league(league) if league else None,
            game_version=game_version,
        )
        
        # SOLITAIRE HACK: Algorithme de correspondance pondérée
        best_match = None
        best_score = -1
        
        for model_name, model_criteria in self._model_index.items():
            score = self._calculate_match_score(search_criteria, model_criteria)
            if score > best_score:
                best_score = score
                best_match = model_name
                
        if best_match:
            logger.info(
                f"Selected model {best_match} for context: "
                f"league={league}, game_mode={game_mode}, game_version={game_version} "
                f"(score={best_score})"
            )
            return best_match
            
        # Fallback au modèle par défaut ou au premier disponible
        if fallback and fallback in self._registry.artifacts:
            logger.info(f"Using fallback model: {fallback}")
            return fallback
            
        logger.warning("No matching model found, using first available")
        return list(self._registry.artifacts.keys())[0]
    
    def _extract_competition_from_league(self, league: str) -> Optional[str]:
        """Extrait le type de compétition depuis le nom de ligue"""
        if not league:
            return None
        league_lower = league.lower()
        
        if "champions" in league_lower:
            return "champions_league"
        elif "europa" in league_lower or "europ" in league_lower:
            return "europa_league"
        elif "conference" in league_lower:
            return "conference_league"
        elif "world cup" in league_lower or "mondial" in league_lower:
            return "world_cup"
            
        return None
    
    def _extract_country_from_league(self, league: str) -> Optional[str]:
        """Extrait le pays depuis le nom de ligue"""
        if not league:
            return None
        league_lower = league.lower()
        
        country_mapping = {
            "england": ["premier", "england", "english", "angleterre"],
            "spain": ["la liga", "spain", "spanish", "espagne"],
            "germany": ["bundesliga", "germany", "german", "allemagne"],
            "italy": ["serie a", "italy", "italian", "italie"],
            "france": ["ligue 1", "france", "french"],
        }
        
        for country, keywords in country_mapping.items():
            if any(keyword in league_lower for keyword in keywords):
                return country
                
        return None
    
    def _calculate_match_score(
        self, 
        search: ModelSelectionCriteria, 
        model: ModelSelectionCriteria
    ) -> float:
        """
        Calcule un score de correspondance entre les critères de recherche et le modèle.
        SOLITAIRE HACK: Scoring pondéré pour correspondances partielles
        """
        score = 0.0
        
        # Poids des différents critères
        weights = {
            "game_mode": 3.0,      # Plus important
            "competition": 2.5,    # Important
            "country": 2.0,        # Moyennement important
            "game_version": 1.5,   # Moins critique
        }
        
        # Correspondance exacte
        if search.game_mode and search.game_mode == model.game_mode:
            score += weights["game_mode"]
        elif search.game_mode and model.game_mode:
            score += weights["game_mode"] * 0.5  # Correspondance partielle
            
        if search.competition and search.competition == model.competition:
            score += weights["competition"]
            
        if search.country and search.country == model.country:
            score += weights["country"]
            
        if search.game_version and search.game_version == model.game_version:
            score += weights["game_version"]
            
        return score
    
    def get_available_contexts(self) -> Dict[str, Any]:
        """Retourne les contextes disponibles dans les modèles chargés"""
        contexts = {
            "game_modes": set(),
            "competitions": set(),
            "countries": set(),
            "game_versions": set(),
        }
        
        for criteria in self._model_index.values():
            if criteria.game_mode:
                contexts["game_modes"].add(criteria.game_mode)
            if criteria.competition:
                contexts["competitions"].add(criteria.competition)
            if criteria.country:
                contexts["countries"].add(criteria.country)
            if criteria.game_version:
                contexts["game_versions"].add(criteria.game_version)
        
        # Convertir les sets en listes pour la sérialisation
        return {
            "game_modes": sorted(list(contexts["game_modes"])),
            "competitions": sorted(list(contexts["competitions"])),
            "countries": sorted(list(contexts["countries"])),
            "game_versions": sorted(list(contexts["game_versions"])),
            "total_models": len(self._model_index),
        }
