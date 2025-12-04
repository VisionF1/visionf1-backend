"""
Cached ML predictor for race position predictions.
"""
import logging
import pandas as pd
from visionf1.core.predictors.simple_position_predictor.predictor import SimplePositionPredictor

logger = logging.getLogger(__name__)

class CachedRacePredictor:
    """Singleton predictor that loads model artifacts once."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self):
        """
        Loads model and preprocessor (call once at startup).
        """
        if self._initialized:
            logger.warning("Predictor already initialized, skipping...")
            return
        
        logger.info("Initializing ML predictor...")
        
        # SimplePositionPredictor handles its own loading from ./model_cache
        self.predictor = SimplePositionPredictor(quiet=False)
        
        self._initialized = True
        logger.info("Predictor ready")
    
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
        
        # Ensure input has the expected columns for SimplePositionPredictor
        # The predictor expects a DataFrame with specific columns.
        # We pass the input dataframe directly as base_df.
        
        # We might need to ensure 'rookie' and 'team_change' columns exist if they are not in input
        # The API input might not provide them.
        # Let's check if we need to enrich the data or if the predictor handles it.
        # FeatureHelper.build_base_df() uses DRIVERS_2025 config to get rookie/team_change.
        # If we pass base_df, we should probably ensure it has those columns if the model needs them.
        
        # For now, let's assume the predictor's FeatureHelper/DatasetBuilder handles missing columns or we rely on what's passed.
        # Actually, SimplePositionPredictor.predict_positions_2025 calls db.build_X(base_df).
        # db.build_X uses fh.align_columns(X) which fills missing with 0.0.
        # But 'rookie' and 'team_change' are used in the output DataFrame construction in predict_positions_2025.
        # So we should probably ensure they are present if we want the output to be correct.
        
        # However, for the purpose of getting a prediction list, we mainly need the model input features.
        
        # Enrich input data with rookie and team_change info from config
        from visionf1.core.config import DRIVERS_2025
        
        if "rookie" not in df_input_data.columns:
            df_input_data["rookie"] = df_input_data["driver"].apply(
                lambda d: DRIVERS_2025.get(d, {}).get("rookie", False)
            )
            
        if "team_change" not in df_input_data.columns:
            df_input_data["team_change"] = df_input_data["driver"].apply(
                lambda d: DRIVERS_2025.get(d, {}).get("team_change", False)
            )
        
        # Ensure driver is the index, as SimplePositionPredictor expects it
        if "driver" in df_input_data.columns:
            df_input_data = df_input_data.set_index("driver", drop=False)

        results_df = self.predictor.predict_positions_2025(base_df=df_input_data)
        
        # The API expects a list of floats corresponding to the input order?
        # The predict_positions_2025 sorts the output!
        # We need to return predictions in the same order as input df_input_data if possible,
        # or the API controller handles mapping back.
        
        # Let's check the controller.
        # predict_race_controller(drivers) -> returns RacePredictionResponse which contains a list of predictions.
        # The controller likely constructs the response.
        # Wait, predict_race_controller calls predictor.predict(df).
        # And returns... let's check controller.py.
        
        # For now, I will return the predicted_position column from the results, 
        # but I need to make sure it matches the input order.
        
        # SimplePositionPredictor sorts the output.
        # I should probably merge back to input or reindex.
        
        # Let's assume input has 'driver' column which is unique.
        results_df = results_df.set_index("driver")
        input_drivers = df_input_data["driver"].values
        
        predictions = []
        for driver in input_drivers:
            if driver in results_df.index:
                predictions.append(results_df.loc[driver, "predicted_position"])
            else:
                predictions.append(20.0) # Fallback
                
        return predictions