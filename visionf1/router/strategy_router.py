from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from visionf1.ml.strategy_predictor import CachedStrategyPredictor, StrategyCandidate

router = APIRouter(
    prefix="/predict/strategy",
    tags=["predictions"]
)

class StrategyRequest(BaseModel):
    circuit: str
    track_temp: float
    air_temp: float
    compounds: List[str] = ["SOFT", "MEDIUM", "HARD"]
    max_stops: int = 2
    fia_rule: bool = False
    top_k: int = 5

class Stint(BaseModel):
    compound: str
    start_lap: int
    end_lap: int

class Window(BaseModel):
    p25: int
    p50: int
    p75: int

class StrategyResponse(BaseModel):
    template: List[str]
    stints: List[Stint]
    windows: List[Window]
    expected_race_time: float
    probability: float

@router.post("/", response_model=List[StrategyResponse])
async def predict_strategy(req: StrategyRequest):
    predictor = CachedStrategyPredictor()
    try:
        candidates = predictor.predict(
            circuit=req.circuit,
            track_temp=req.track_temp,
            air_temp=req.air_temp,
            compounds=req.compounds,
            max_stops=req.max_stops,
            fia_rule=req.fia_rule,
            top_k=req.top_k
        )
        
        response = []
        for c in candidates:
            stints = [
                Stint(compound=s[0], start_lap=s[1], end_lap=s[2]) 
                for s in c.stints
            ]
            windows = [
                Window(p25=w[0], p50=w[1], p75=w[2])
                for w in c.windows
            ]
            response.append(StrategyResponse(
                template=c.template,
                stints=stints,
                windows=windows,
                expected_race_time=c.expected_total_race_time,
                probability=c.prob
            ))
            
        return response
        
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
