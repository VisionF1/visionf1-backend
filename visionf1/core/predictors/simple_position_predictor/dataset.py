import os
import pickle
import numpy as np
import pandas as pd
from visionf1.core.training.enhanced_data_preparer import EnhancedDataPreparer
from .paths import BEFORE_FE_PATH, CACHED_DATA_PKL

class InferenceDatasetBuilder:
    def __init__(self, logger, feature_helper, manifest_helper):
        self._log = logger.log
        self.dp = EnhancedDataPreparer(quiet=True, manifest_helper=manifest_helper)
        self.fh = feature_helper
        self.mh = manifest_helper
        self._last_weather_stats = None

    @property
    def last_weather_stats(self):
        return self._last_weather_stats

    def _ensure_hist(self):
        hist_df = None
        if os.path.exists(CACHED_DATA_PKL):
            try:
                hist_df = pickle.load(open(CACHED_DATA_PKL, "rb"))
                if not isinstance(hist_df, pd.DataFrame):
                    hist_df = pd.DataFrame(hist_df)
            except Exception as e:
                self._log(f"⚠️ No se pudo cargar histórico (PKL): {e}")
        if (hist_df is None or hist_df.empty) and os.path.exists(BEFORE_FE_PATH):
            try:
                hist_df = pd.read_csv(BEFORE_FE_PATH)
            except Exception as e:
                self._log(f"⚠️ No se pudo leer histórico (CSV): {e}")
        return hist_df

    def build_X(self, base_df: pd.DataFrame) -> pd.DataFrame:
        # Simplificación: confiamos en base_df como la fuente de verdad para la inferencia actual.
        # No intentamos mezclar con histórico complejo que puede filtrar filas si no coinciden.
        
        # 1. Preparar features usando EnhancedDataPreparer (que ya maneja encoding y alineación de features)
        X, _, _, _ = self.dp.prepare_enhanced_features(base_df.copy(), inference=True)
        
        # 2. Asegurar que sea DataFrame
        X = pd.DataFrame(X) if not isinstance(X, pd.DataFrame) else X
        
        # 3. Asegurar que el índice coincida con base_df para que el predictor pueda mapear resultados
        if X.shape[0] != base_df.shape[0]:
             self._log(f"⚠️ Cardinalidad inesperada en build_X: X={X.shape[0]} vs base={base_df.shape[0]}. Ajustando.")
             # Si por alguna razón cambió, intentamos reindexar o cortar
             if X.shape[0] > base_df.shape[0]:
                 X = X.iloc[:base_df.shape[0]]
             else:
                 # Si faltan filas, es problemático. Reindexamos llenando con 0
                 X = X.reindex(range(len(base_df))).fillna(0)
        
        X.index = base_df.index
        
        # 4. Alinear columnas finales (orden correcto para el modelo)
        return self.fh.align_columns(X)
