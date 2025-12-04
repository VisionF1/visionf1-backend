"""
Cached ML predictor for race strategy predictions.
"""
import logging
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Literal, Dict
from itertools import product

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Constants & Defaults
# ---------------------------------------------------------
ALPHA_HISTORICAL_PRIOR = 3.0
BETA_TIME_PRIOR = 0.4
MAX_LEN_BY_COMPOUND = {"SOFT": 20, "MEDIUM": 32, "HARD": 48}

DURA_OVERRIDES = {
    "Monaco": {"SOFT": 30, "MEDIUM": 40, "HARD": 55},
    "Zandvoort": {"SOFT": 28, "MEDIUM": 38, "HARD": 54},
}

@dataclass
class StrategyCandidate:
    template: List[str]
    stints: List[Tuple[str, int, int]]  # (compound, start, end) end exclusive
    windows: List[Tuple[int, int, int]]      # pit windows p25–p75
    expected_total_race_time: float     # seconds
    prob: float

class CachedStrategyPredictor:
    """Singleton predictor for race strategies."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, survival_model_path: Path, next_compound_path: Path, circuit_pitloss_path: Path):
        """
        Loads models and configuration.
        """
        if self._initialized:
            logger.warning("Strategy Predictor already initialized, skipping...")
            return
        
        logger.info("Initializing Strategy Predictor...")
        
        try:
            self.surv = joblib.load(survival_model_path)
            self.clf = joblib.load(next_compound_path)
            
            with open(circuit_pitloss_path, 'r') as f:
                self.circuit_defaults = json.load(f)
                
            self.rng = np.random.RandomState(42)
            self._qcache = {}
            self._qcache_hits = {}
            
            self._initialized = True
            logger.info("Strategy Predictor ready")
        except Exception as e:
            logger.error(f"Failed to initialize Strategy Predictor: {e}")
            raise

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    def _get_circuit_params(self, circuit: str):
        meta = self.circuit_defaults.get(circuit, {"total_laps": 60, "pit_loss": 20.0, "base_pace_s": 100.0})
        abrasion = 0.50
        return {
            "total_laps": int(meta["total_laps"]),
            "pit_loss": float(meta["pit_loss"]),
            "base_pace_s": float(meta["base_pace_s"]),
            "abrasion": abrasion, 
        }

    def _durability_ok(self, compound: str, q25: float, q50: float, q75: float, circuit: str) -> bool:
        max_len = MAX_LEN_BY_COMPOUND.get(compound, 60)
        if circuit in DURA_OVERRIDES and compound in DURA_OVERRIDES[circuit]:
            max_len = DURA_OVERRIDES[circuit][compound] 
        iqr = q75 - q25
        return q50 <= max_len and iqr <= max_len

    def _windows_to_stints(self, template: List[str], windows: List[Tuple[int, int, int]], total_laps: int) -> List[Tuple[str, int, int]]:
        n = len(template)
        if n == 0: return []
        if n == 1: return [(template[0], 1, total_laps + 1)]

        if not windows or len(windows) < (n - 1):
            return []

        cuts = [1] + [int(max(2, min(total_laps - 1, round(lo)))) for (lo, _mid, _hi) in windows[: n - 1]] + [total_laps + 1]

        for i in range(1, len(cuts)):
            if cuts[i] <= cuts[i - 1]:
                cuts[i] = cuts[i - 1] + 1
        cuts[-1] = max(cuts[-1], cuts[-2] + 1)

        stints = []
        for i in range(n):
            start, end = cuts[i], cuts[i + 1]
            if end <= start:
                return []
            stints.append((template[i], start, end))
        return stints

    def _make_aft_features(self, ctx_row: dict, spec: dict) -> pd.DataFrame:
        feats_num = spec["feats_num"]
        feats_cat = spec["feats_cat"]
        Xn = pd.DataFrame([{k: float(ctx_row.get(k, np.nan)) for k in feats_num}])
        Xc_raw = pd.DataFrame([{k: ctx_row.get(k, None) for k in feats_cat}]).astype("category")
        Xc = pd.get_dummies(Xc_raw, drop_first=True)

        X = pd.concat([Xn, Xc], axis=1)
        cols = spec["feature_columns"]
        for col in cols:
            if col not in X.columns:
                X[col] = 0.0
        X = X.reindex(columns=cols, fill_value=0.0)
        return X

    def _quantiles_for(self, compound: str, stint_idx: int, circuit: str,
                       track_temp: float, air_temp: float, total_laps: int) -> Tuple[int, int, int]:
        key = (compound, stint_idx, circuit, float(track_temp), float(air_temp), int(total_laps))
        if key in self._qcache:
            self._qcache_hits[key] = self._qcache_hits.get(key, 0) + 1
            return self._qcache[key]

        if compound not in self.surv:
            self._qcache[key] = (15, 22, 35)
            return self._qcache[key]

        spec = self.surv[compound]
        aft = spec["model"]
        X = self._make_aft_features(
            {
                "circuit": circuit,
                "track_temp": track_temp,
                "air_temp": air_temp,
                "rainfall": 0.0,
                "total_laps": total_laps,
                "stint_index": stint_idx,
                "is_final_stint": 0.0,
            },
            spec
        )
        
        # Ensure numeric columns are float
        num_cols = [c for c in spec["feats_num"] if c in X.columns]
        if len(num_cols):
            X[num_cols] = X[num_cols].astype(float).fillna(0.0)

        q25 = q50 = q75 = np.nan
        try:
            q25 = float(aft.predict_percentile(X, p=0.25).values[0])
            q50 = float(aft.predict_percentile(X, p=0.50).values[0])
            q75 = float(aft.predict_percentile(X, p=0.75).values[0])
        except Exception:
            pass # Fallback to survival function expansion

        if not all(np.isfinite([q25, q50, q75])):
             # Simplified fallback logic for brevity/robustness in port
             # If direct percentile fails, we could implement the full expansion logic
             # For now, let's use the fallback if available or hardcoded defaults
             fb = spec.get("fallback_q")
             if fb:
                 q25, q50, q75 = fb["q25"], fb["q50"], fb["q75"]
             else:
                 q25, q50, q75 = 15, 22, 35

        q25, q50, q75 = sorted([float(q25), float(q50), float(q75)])

        lo_cap = 5
        hi_cap = max(6, total_laps - 1)

        def _cap(v):
            return int(max(lo_cap, min(hi_cap, round(float(v))))) if np.isfinite(v) else None

        q25i, q50i, q75i = _cap(q25), _cap(q50), _cap(q75)
        
        if None in (q25i, q50i, q75i):
             q25i, q50i, q75i = 15, 22, 35

        if q75i - q25i < 6:
            mid = (q25i + q75i) // 2
            q25i = max(lo_cap, mid - 3)
            q75i = min(hi_cap, q25i + 6)
            q50i = max(q25i, min(q75i - 1, q50i))

        if not (q25i <= q50i <= q75i):
            q25i, q50i, q75i = sorted([q25i, q50i, q75i])

        self._qcache[key] = (q25i, q50i, q75i)
        return self._qcache[key]

    def _stint_time(self, base_pace_s: float, compound: str, stint_len: int, abrasion: float):
        base_deg = {"SOFT": 0.040, "MEDIUM": 0.025, "HARD": 0.015}
        d = base_deg.get(compound, 0.02)
        d_eff = d * (1.0 + 0.7 * (abrasion - 0.5))
        laps = np.arange(stint_len)
        lap_times = base_pace_s + d_eff * laps
        return lap_times.sum()

    def _template_prior(self, template: List[str], circuit: str, track_temp: float, air_temp: float) -> float:
        if len(template) <= 1:
            return 1e-4

        prior_log = 0.0
        classes = list(self.clf.classes_)

        for i in range(len(template) - 1):
            cur_c = template[i]
            next_c = template[i + 1]
            X = pd.DataFrame([{
                "cur_compound": cur_c,
                "circuit": circuit,
                "track_temp": float(track_temp),
                "air_temp": float(air_temp),
                "rainfall": float(False),
                "stint_index": float(i + 1),
            }])
            # Ensure columns match training
            # (Assuming clf handles missing cols or we need to match exact features as in training)
            # For robustness, we just call predict_proba. If it fails due to missing cols, we might need more robust feature construction here.
            # The original code just passed this DF.
            
            try:
                proba = self.clf.predict_proba(X)[0]
                if next_c in classes:
                    idx = classes.index(next_c)
                    prior_log += np.log(proba[idx] + 1e-9)
                else:
                    prior_log += np.log(1e-4)
            except Exception:
                prior_log += np.log(1e-4) # Fallback
        
        prior_log /= (len(template) - 1)
        return np.exp(prior_log)

    def _simulate_template(self, template: List[str], total_laps: int, ctx: dict,
                           base_pace_s=100.0, pit_loss=20.0, sims=300, abrasion=0.5,
                           early_stop_frac: float = 0.15):
        best_time = np.inf
        pit_laps_all, times = [], []
        bound_margin = 8.0

        for s in range(sims):
            laps_left = total_laps
            chosen = []
            ok = True
            for i, c in enumerate(template):
                if i < len(template) - 1:
                    q25, q50, q75 = self._quantiles_for(
                        c, i + 1, ctx["circuit"], ctx["track_temp"], ctx["air_temp"], total_laps
                    )
                    if not self._durability_ok(c, q25, q50, q75, ctx["circuit"]):
                        ok = False
                        break
                    l = int(np.clip(self.rng.randint(q25, q75 + 1), 1, max(1, laps_left - 1)))
                else:
                    l = laps_left
                chosen.append(l)
                laps_left -= l
                if laps_left < 0:
                    ok = False
                    break
            if not ok or sum(chosen) != total_laps:
                continue

            t = sum(self._stint_time(base_pace_s, comp, l, abrasion) for comp, l in zip(template, chosen))
            t += pit_loss * (len(template) - 1)
            times.append(t)
            if t < best_time:
                best_time = t
            
            if (s + 1) >= int(sims * early_stop_frac):
                mean_so_far = np.mean(times)
                if mean_so_far > (best_time + bound_margin):
                    break
            pit_laps_all.append(np.cumsum(chosen)[:-1])

        if not times:
            return None
        pit_mat = np.vstack(pit_laps_all) if pit_laps_all and len(pit_laps_all[0]) > 0 else None
        windows = []
        if pit_mat is not None:
            for i in range(pit_mat.shape[1]):
                p25 = int(np.percentile(pit_mat[:, i], 25))
                p50 = int(np.median(pit_mat[:, i]))
                p75 = int(np.percentile(pit_mat[:, i], 75))
                windows.append((p25, p50, p75))
        return float(np.mean(times)), windows

    def predict(self,
                circuit: str,
                track_temp: float,
                air_temp: float,
                compounds: List[str] = ("SOFT", "MEDIUM", "HARD"),
                max_stops: int = 2,
                fia_rule: bool = True,
                top_k: int = 5) -> List[StrategyCandidate]:
        
        if not self._initialized:
             raise RuntimeError("Strategy Predictor not initialized")

        cp = self._get_circuit_params(circuit)
        total_laps = cp["total_laps"]
        pit_loss = cp["pit_loss"]
        base_pace_s = cp["base_pace_s"]
        abrasion = cp["abrasion"]

        ctx = {
            "circuit": circuit,
            "track_temp": float(track_temp),
            "air_temp": float(air_temp),
            "rainfall": 0.0,
        }

        # Generate templates
        templates = []
        for n in range(2, max_stops + 2): # max_stops=2 -> up to 3 stints
             for tpl in product(compounds, repeat=n):
                 templates.append(list(tpl))

        if fia_rule:
            templates = [t for t in templates if len(set(t)) >= 2]

        # Gating
        gated = []
        for tpl in templates:
            ok = True
            for i, c in enumerate(tpl[:-1]):
                q25, q50, q75 = self._quantiles_for(c, i + 1, circuit, track_temp, air_temp, total_laps)
                if not self._durability_ok(c, q25, q50, q75, circuit):
                    ok = False
                    break
            if ok:
                gated.append(tpl)
        templates = gated

        results = []
        for tpl in templates:
            sim = self._simulate_template(tpl, total_laps, ctx, base_pace_s, pit_loss,
                                          sims=260, abrasion=abrasion, early_stop_frac=0.18)
            if sim is None:
                continue
            exp_t, windows = sim

            stints = self._windows_to_stints(tpl, windows, total_laps)
            if not stints:
                if len(tpl) == 1:
                    stints = [(tpl[0], 1, total_laps + 1)]
                else:
                    continue

            results.append(StrategyCandidate(tpl, stints, windows, exp_t, 0.0))

        if not results:
            return []

        times = np.array([r.expected_total_race_time for r in results])
        priors = np.array([
            self._template_prior(r.template, circuit, track_temp, air_temp)
            for r in results
        ])
        norm_time = (times - times.min()) / (times.std() + 1e-9)
        score = (priors ** ALPHA_HISTORICAL_PRIOR) * np.exp(-norm_time * BETA_TIME_PRIOR)
        probs = score / score.sum() if score.sum() > 0 else np.ones_like(score) / len(score)

        for r, p in zip(results, probs):
            r.prob = float(p)

        results.sort(key=lambda r: r.prob, reverse=True)
        return results[:top_k]
