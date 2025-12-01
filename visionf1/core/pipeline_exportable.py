# app/core/pipeline_exportable.py
import pandas as pd

from visionf1.core.predictors.simple_position_predictor.predictor import SimplePositionPredictor
from visionf1.core.predictors.quali_recent_predictor import RecentQualiPredictor
from visionf1.core.config import RACE_PREDICTION

class PipelineExportable:
    """
    Pipeline de SOLO INFERENCIA, fiel al comportamiento original:
    - Usa SimplePositionPredictor (carrera)
    - Usa RecentQualiPredictor (qualy)
    - NO entrena, NO descarga con fastf1, NO limpia datos crudos
    - Respeta manifest/encoders/feature_names si existen en models_cache
    """

    def __init__(self, *args, **kwargs):
        # Compatibilidad con la firma del pipeline original (se ignoran args)
        pass

    # ---------------- CARRERA ----------------
    def predict_next_race_positions(self) -> pd.DataFrame:
        spp = SimplePositionPredictor(quiet=True)
        df = spp.predict_positions_2025()
        try:
            spp.show_realistic_predictions(df)  # misma vista que usás hoy
        except Exception:
            pass
        return df

    # ---------------- QUALI ----------------
    def predict_quali_next_race(self) -> pd.DataFrame:
        from visionf1.core.config import PREDICTION_CONFIG
        import os

        qp = RecentQualiPredictor()
        model_path = "./model_cache/quali_recent_model.pkl"

        if os.path.exists(model_path):
            qp.load(model_path)
        else:
            print(f"⚠️ No se encontró el modelo {model_path}")

        nr = PREDICTION_CONFIG.get("next_race", {})
        year = int(nr.get("year", 2025))
        race_name = str(nr.get("race_name", ""))
        round_num = int(nr.get("race_number", 0)) or 0

        meta = {"year": year, "race_name": race_name, "round": round_num}

        df = qp.predict_next_event(meta)
        try:
            df.to_csv("./model_cache/quali_predictions_latest.csv", index=False)
        except Exception:
            pass
        return df

    def predict_race_from_quali_grid(self, beta: float | None = None):
        """
        Mezcla la predicción base de carrera con la grilla predicha (qualy).
        Usa el parámetro beta del config.py para ponderar ambas fuentes.
        Muestra también el Top 10 de la qualy predicha.
        """
        import os
        import pandas as pd
        from visionf1.core.config import RACE_PREDICTION

        race_file = "./model_cache/race_predictions_latest.csv"
        quali_file = "./model_cache/quali_predictions_latest.csv"

        print("📂 Verificando existencia de archivos:")
        print(f"   - Quali: {os.path.exists(quali_file)} ({quali_file})")
        print(f"   - Race:  {os.path.exists(race_file)} ({race_file})")

        # 1️⃣ Asegurar que existan predicciones previas
        if not os.path.exists(quali_file):
            print("⚠️ No se encontró la predicción de qualy, generándola...")
            self.predict_quali_next_race()
        if not os.path.exists(race_file):
            print("⚠️ No se encontró la predicción base de carrera, generándola...")
            race_df = self.predict_next_race_positions()
            try:
                race_df.to_csv(race_file, index=False)
                print(f"💾 Archivo de carrera generado: {race_file}")
            except Exception as e:
                print(f"⚠️ No se pudo guardar el archivo de carrera: {e}")

        # 2️⃣ Cargar dataframes
        quali = pd.read_csv(quali_file)
        race = pd.read_csv(race_file)

        print(f"✅ Cargadas: {len(quali)} filas (qualy), {len(race)} filas (carrera)")
        print(f"📋 Columnas quali: {list(quali.columns)}")
        print(f"📋 Columnas carrera: {list(race.columns)}")

        # 3️⃣ Mostrar TOP 10 de Qualy predicha
        if "pred_rank" in quali.columns:
            print("\n🏁 TOP 10 QUALY PREDICHA")
            print("Pos | Driver | Team        | Lap (s)")
            print("--------------------------------------")
            for _, row in quali.sort_values("pred_rank").head(10).iterrows():
                print(f"P{int(row['pred_rank']):<2} | {row['driver']:<4} | {row['team']:<10} | {row['pred_best_quali_lap_s']:<8.3f}")
        else:
            print("⚠️  No se encontró columna 'pred_rank' en la qualy; no se puede mostrar TOP 10.")

        # 4️⃣ Validar columnas necesarias
        if "pred_rank" not in quali.columns:
            print("❌ ERROR: 'pred_rank' no existe en qualy, no se puede mezclar.")
            return race

        if "predicted_position" not in race.columns:
            if "final_position" in race.columns:
                race["predicted_position"] = race["final_position"].astype(float)
            else:
                print("❌ ERROR: 'predicted_position' o 'final_position' no existen en carrera.")
                return race

        # 5️⃣ Parámetro de mezcla
        beta = beta or RACE_PREDICTION.get("grid_mix_beta", 0.35)
        print(f"\n⚙️  Aplicando mezcla con β = {beta:.2f}")

        for col in ["pred_rank", "mixed_score", "grid_position"]:
            if col in race.columns:
                race = race.drop(columns=[col])

        merged = pd.merge(race, quali[["driver", "pred_rank"]], on="driver", how="left")

        merged["grid_position"] = merged["pred_rank"].fillna(merged["final_position"])
        merged["mixed_score"] = (1 - beta) * merged["predicted_position"] + beta * merged["grid_position"]

        merged = merged.sort_values("mixed_score", ascending=True).reset_index(drop=True)
        merged["final_position"] = merged.index + 1

        print(f"✅ Mezcla completada. Total pilotos combinados: {len(merged)}")

        # 7️⃣ Guardar CSV final
        out_path = "./model_cache/race_predictions_latest.csv"
        merged.to_csv(out_path, index=False)
        print(f"💾 Predicción combinada guardada en {out_path}")

        # 8️⃣ Mostrar resumen final Top 10
        print("\n🏎️  RESULTADO MIXTO (TOP 10)")
        print("Pos | Driver | Grid | Model | Mixed")
        print("--------------------------------------")
        for _, row in merged.head(10).iterrows():
            print(f"P{int(row['final_position']):<2} | {row['driver']:<4} | "
                f"{int(row['grid_position']):<4} | {row['predicted_position']:<7.3f} | {row['mixed_score']:<7.3f}")

        return merged



    def train_and_predict_all(self) -> dict:
        """
        Conserva el nombre por compatibilidad; aquí NO se entrena.
        Genera qualy y carrera (mezclando con grilla si está disponible).
        """
        _quali = self.predict_quali_next_race()
        print("doing quali")
        _race = self.predict_race_from_quali_grid(beta=None)
        print("doing race")
        return {
            "quali_predictions": "./model_cache/quali_predictions_latest.csv",
            "race_predictions": "./model_cache/race_predictions_latest.csv",
        }
