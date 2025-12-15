
# VisionF1 Backend

**VisionF1 Backend** is the core content delivery and inference service for the VisionF1 platform. It acts as the central API hub, providing historical data, real-time race analytics, and ML-powered strategy predictions to the frontend application.

Unlike the training pipeline, this service is optimized for **low-latency read operations** and **inference**, serving cached models and pre-computed datasets directly to users.

---

## Key Features

*   **Race Analytics Engine**: Delivers sophisticated metrics including:
    *   **Race Pace**: Average lap times adjusted for fuel and tyre degradation.
    *   **Clean Air Pace**: Performance metrics filtering out traffic interaction.
    *   **Lap Time Distributions**: Statistical breakdown of driver consistency.
*   **ML Strategy Inference**: Real-time tire strategy prediction (`SOFT` -> `HARD`, etc.) using survival models downloaded from Cloudinary.
*   **Content Aggregation**: Central source of truth for:
    *   Driver & Team Standings
    *   Event Calendars (Summary & Detailed)
    *   Upcoming Grand Prix Metadata
*   **Cloudinary Integration**: Automatically downloads and initializes cached ML artifacts (models, encoders) at startup to ensure zero-latency inference.
*   **FastAPI Architecture**: Built for high-concurrency async performance.

---

## Tech Stack

*   **Framework**: FastAPI
*   **ML Operations**: Cloudinary (Artifact Storage), Scikit-learn, Joblib
*   **Data Processing**: Pandas, NumPy
*   **Database**: Integration with historical data sources
*   **Environment**: Docker / Heroku compatible

---

## API Endpoints

The API is served at `http://0.0.0.0:8000`. Full documentation at `/docs`.

### 1. Analytics & Telemetry

*   **GET** `/race-pace`
    Returns fuel-adjusted race pace for a specific event.
    *Query Params*: `season`, `round`, `event_id`

*   **GET** `/clean-air-race-pace`
    Pace metrics excluding laps affected by traffic (>2s gap).

*   **GET** `/lap-time-distributions`
    Violin plot data showing lap consistency and outliers.

### 2. Strategy Prediction

*   **POST** `/predict-strategy`
    Predicts the optimal pit stop strategy for a given circuit and conditions.

    **Body:**
    ```json
    {
      "circuit": "Silverstone",
      "track_temp": 30.0,
      "compounds": ["SOFT", "MEDIUM", "HARD"],
      "max_stops": 2
    }
    ```

### 3. Core Data

*   **GET** `/driver-standings` / `/team-standings`: Current championship points.
*   **GET** `/events`: Full calendar data with session times.
*   **GET** `/upcoming-gp`: Next race countdown and metadata.

---

## ML Pipeline

This service uses a **Cached Prediction Architecture**:
1.  **Startup**: Downloads latest trained models (`metrics.json`, `survival_models`, etc.) from a remote Cloudinary store.
2.  **Inference**: Runs tailored prediction logic (e.g., Tire Degradation Survival Analysis) locally in memory.
3.  **Updates**: Models are retrained externally and updated via restart, ensuring the API remains stateless and fast.

---

## Installation & Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/visionf1-backend.git
    cd visionf1-backend
    ```

2.  **Environment Setup:**
    Create a `.env` file with necessary keys (Cloudinary, etc.).

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the server:**
    ```bash
    fastapi run main.py
    ```

---

© 2025 VisionF1 Team
