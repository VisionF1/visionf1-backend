"""
Cached ML predictor for race position predictions.
"""
import logging
from pathlib import Path
import pandas as pd
import xgboost as xgb
from visionf1.ml.slim_preprocessor import SlimPreprocessor

logger = logging.getLogger(__name__)

class CachedRacePredictor:
    """Singleton predictor that loads model artifacts once."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, model_path: Path, history_path: Path, features_path: Path):
        """
        Loads model and preprocessor (call once at startup).
        
        Args:
            model_path: Path to portable_xgb.json
            history_path: Path to history_store.pkl
            features_path: Path to feature_names.pkl
        """
        if self._initialized:
            logger.warning("Predictor already initialized, skipping...")
            return
        
        logger.info("🚀 Initializing ML predictor...")
        
        self.model = xgb.XGBRegressor()
        self.model.load_model(str(model_path))
        
        self.preprocessor = SlimPreprocessor(
            history_store_path=str(history_path),
            feature_names_path=str(features_path),
            quiet=True
        )
        
        self._initialized = True
        logger.info("✅ Predictor ready")
    
    def predict(self, df_input_data: pd.DataFrame) -> list[float]:
        """
        Predicts race positions from raw input.
        
        Args:
            df_input_data: DataFrame with columns: driver, team, race_name, year, 
                    session_air_temp, session_track_temp, session_humidity,
                    session_rainfall, circuit_type
        
        Returns:
            List of predicted positions (lower = better)
        """
        if not self._initialized:
            raise RuntimeError("Predictor not initialized. Call initialize() first.")
        
        X = self.preprocessor.transform(df_input_data)
        predictions = self.model.predict(X)
        
        return predictions.tolist()