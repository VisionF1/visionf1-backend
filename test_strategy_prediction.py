import os
from fastapi.testclient import TestClient
from main import app

# Mock environment variables if needed, though we probably want to test with real ones if available
# os.environ["CLOUDINARY_CLOUD_NAME"] = "..." 

def test_strategy_prediction():
    payload = {
        "circuit": "Silverstone",
        "track_temp": 30.0,
        "air_temp": 25.0,
        "compounds": ["SOFT", "MEDIUM", "HARD"],
        "max_stops": 2,
        "fia_rule": False,
        "top_k": 3
    }
    
    with TestClient(app) as client:
        # Note: This might fail if artifacts are not downloaded or Cloudinary env var is missing in this context
        # But it's a good integration test.
        response = client.post("/predict/strategy/", json=payload)
        
        if response.status_code != 200:
            print(f"Failed: {response.status_code}")
            print(response.json())
        else:
            print("Success!")
            data = response.json()
            print(f"Received {len(data)} strategies.")
            for i, s in enumerate(data):
                print(f"Strategy {i+1}: {s['template']} - Time: {s['expected_race_time']:.2f}s")

if __name__ == "__main__":
    test_strategy_prediction()
