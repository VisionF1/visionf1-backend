MODEL_FILES = {
    "RandomForest": "./model_cache/randomforest_model.pkl",
    "XGBoost": "./model_cache/xgboost_model.pkl",
    "GradientBoosting": "./model_cache/gradientboosting_model.pkl",
}

AFTER_FE_PATH = "./model_cache/dataset_after_feature_engineering_latest.csv"
BEFORE_FE_PATH = "./model_cache/dataset_before_training_latest.csv"
CACHED_DATA_PKL = "./model_cache/cached_data.pkl"
FEATURE_NAMES_PKL = "./model_cache/feature_names.pkl"
INFERENCE_OUT = "./model_cache/inference_dataset_latest.csv"

MANIFEST_PATHS = [
    "./model_cache/inference_manifest.json",
    "/mnt/data/inference_manifest.json",
]

TRAINING_RESULTS_PKL = "./model_cache/training_results.pkl"
