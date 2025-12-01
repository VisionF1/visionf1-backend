import pandas as pd
import pickle
import os

class EnhancedDataPreparer:
    """
    Versión exportable fiel al pipeline original.
    No genera features nuevas: usa directamente el dataset de inferencia
    creado previamente por el pipeline completo del proyecto.
    """

    def __init__(self, quiet=True, manifest_helper=None):
        self.quiet = quiet
        self.mh = manifest_helper
        
        # Intentar cargar nombres de features esperadas
        self.feature_names = None
        feat_path = "./model_cache/feature_names.pkl"
        if os.path.exists(feat_path):
            with open(feat_path, "rb") as f:
                self.feature_names = pickle.load(f)
        else:
            print("⚠️  No se encontró feature_names.pkl, se usará todas las numéricas.")

    def prepare_enhanced_features(self, df=None, inference=True):
        """
        Prepara features para inferencia usando el DataFrame de entrada.
        """
        if df is None or df.empty:
            return pd.DataFrame(), None, None, None

        X = df.copy()

        # Codificar categóricas usando ManifestHelper
        if self.mh:
            for col in ["driver", "team", "race_name", "circuit_type"]:
                if col in X.columns:
                    # Usar apply para codificar cada valor
                    X[f"{col}_encoded"] = X[col].apply(lambda x: self.mh.encode_value(col, x))
                    # Llenar nulos con -1 o 0 si no se encuentra
                    X[f"{col}_encoded"] = X[f"{col}_encoded"].fillna(-1).astype(int)

        # Asegurar que todas las features esperadas estén presentes
        if self.feature_names:
            for f in self.feature_names:
                if f not in X.columns:
                    X[f] = 0.0
            X = X[self.feature_names]

        X = X.fillna(0.0)
        return X, None, None, None
