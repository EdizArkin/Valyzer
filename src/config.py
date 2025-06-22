import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API KEYS ---

#------ Amadeus API ------
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

#------ Other APIs ------
TRAVELPAYOUTS_API_KEY = os.getenv("TRAVELPAYOUTS_API_KEY") # now out of limits, but kept for reference
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
GOOGLE_TRENDS_REGION = os.getenv("GOOGLE_TRENDS_REGION", "TR")
CALENDARIFIC_API_KEY = os.getenv("CALENDARIFIC_API_KEY")  # (optional, if using holiday API)

# --- PATHS ---
RAW_DATA_PATH = "data/raw/"
PROCESSED_DATA_PATH = "data/processed/"
MODEL_PATH = "models/"
NOTEBOOK_PATH = "notebooks/"
LOG_PATH = "logs/"
SRC_PATH = "src/"  

# --- MODEL PARAMETERS ---
FORECAST_DAYS = 30

XGBOOST_PARAMS = {
    "learning_rate": 0.1,
    "max_depth": 5,
    "n_estimators": 100,
    "objective": "reg:squarederror"
}

# --- OTHER SETTINGS ---
IS_DEBUG = os.getenv("DEBUG_MODE", "false").lower() == "true"
DEFAULT_CURRENCY = "TRY"
