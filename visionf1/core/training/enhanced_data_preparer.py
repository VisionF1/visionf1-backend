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

    def _process_weather_features(self, df: pd.DataFrame):
        import numpy as np
        defaults = {
            'session_air_temp': 25.0,
            'session_track_temp': 35.0,
            'session_humidity': 60.0,
            'session_rainfall': 0.0,
        }
        for c, v in defaults.items():
            if c not in df.columns:
                df[c] = v
            else:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(v)

        if 'heat_index' not in df.columns:
            air = df['session_air_temp']
            track = df['session_track_temp']
            hum = df['session_humidity']
            # Simple approximation used in training
            hi = (0.6 * air + 0.4 * track) / 100.0 - (hum - 50.0) * 0.001
            df['heat_index'] = np.clip(hi, 0.0, 1.0)

        if 'weather_difficulty_index' not in df.columns:
            df['weather_difficulty_index'] = (df['session_humidity'] / 100.0) + (df['session_rainfall'] * 3.0)

        return df

    def _load_history_store(self):
        path = "./model_cache/history_store.pkl"
        if os.path.exists(path):
            with open(path, "rb") as f:
                self.history_store = pickle.load(f)
        else:
            self.history_store = None

    def _get_race_index(self, year, race_name):
        if not self.history_store: return 100
        order = self.history_store.get("race_order", {}).get(int(year), [])
        try:
            return order.index(race_name) + 1
        except ValueError:
            return len(order) + 1

    def _prior_events(self, seq, year, race_name):
        if not seq: return []
        target_idx = self._get_race_index(year, race_name)
        return [x for x in seq if int(x["year"]) < int(year) or
                (int(x["year"]) == int(year) and int(x["race_index"]) < int(target_idx))]

    def _rolling_avg_points(self, seq, window):
        if not seq: return 0.0
        pts = [float(x.get("points", 0.0)) for x in seq]
        if not pts: return 0.0
        import numpy as np
        return float(np.mean(pts[-window:] if len(pts) >= window else pts))

    def _process_historical_features(self, df: pd.DataFrame):
        if not self.history_store:
            return df
        
        # Pre-load lookups
        driver_hist = self.history_store.get("driver_history", {})
        team_hist = self.history_store.get("team_history", {})
        defaults = self.history_store.get("defaults", {})
        rain_dry = self.history_store.get("driver_rain_dry_avgs", {})

        # Vectorized or row-wise? Row-wise is safer for complex logic
        dcomp_list = []
        tcomp_list = []
        pl3_list = []
        wet_list = []
        dry_list = []
        delta_list = []

        for _, row in df.iterrows():
            drv = str(row.get("driver", ""))
            team = str(row.get("team", ""))
            year = int(row.get("year", 2025))
            race = str(row.get("race_name", ""))

            # Driver Comp
            seq_d = self._prior_events(driver_hist.get(drv, []), year, race)
            dc = self._rolling_avg_points(seq_d, 10)
            if dc == 0.0 and not seq_d: dc = defaults.get("driver_competitiveness", 0.0)
            dcomp_list.append(dc)

            # Team Comp
            seq_t = self._prior_events(team_hist.get(team, []), year, race)
            tc = self._rolling_avg_points(seq_t, 10)
            if tc == 0.0 and not seq_t: tc = defaults.get("team_competitiveness", 0.0)
            tcomp_list.append(tc)

            # Points Last 3
            pts_seq = [float(x.get("points", 0.0)) for x in seq_d[-3:]]
            pl3 = sum(pts_seq) if pts_seq else defaults.get("points_last_3", 0.0)
            pl3_list.append(pl3)

            # Rain/Dry
            rd = rain_dry.get(drv, {"dry": 0.0, "rain": 0.0})
            dry_val = float(rd.get("dry", 0.0))
            wet_val = float(rd.get("rain", 0.0))
            dry_list.append(dry_val)
            wet_list.append(wet_val)
            delta_list.append(dry_val - wet_val)

        df["driver_competitiveness"] = dcomp_list
        df["team_competitiveness"] = tcomp_list
        df["points_last_3"] = pl3_list
        df["driver_avg_points_in_dry"] = dry_list
        df["driver_avg_points_in_rain"] = wet_list
        df["driver_rain_dry_delta"] = delta_list
        
        return df

    def prepare_enhanced_features(self, df=None, inference=True):
        """
        Prepara features para inferencia usando el DataFrame de entrada.
        """
        if df is None or df.empty:
            return pd.DataFrame(), None, None, None

        # Cargar histórico si no está cargado (lazy load)
        if not hasattr(self, "history_store"):
            self._load_history_store()

        X = df.copy()
        
        # 1. Calcular features derivadas (Clima)
        X = self._process_weather_features(X)
        
        # 2. Calcular features históricas
        X = self._process_historical_features(X)

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
