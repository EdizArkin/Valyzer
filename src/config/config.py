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
# Get the project root directory (parent of src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "RawDatasets") + os.sep
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "ProcessedDatasets") + os.sep
MODEL_PATH = os.path.join(PROJECT_ROOT, "models") + os.sep
RESULTS_PATH = os.path.join(PROJECT_ROOT, "results") + os.sep
NOTEBOOK_PATH = os.path.join(PROJECT_ROOT, "notebooks") + os.sep
LOG_PATH = os.path.join(PROJECT_ROOT, "logs") + os.sep
SRC_PATH = os.path.join(PROJECT_ROOT, "src") + os.sep  
IMG_PATH = os.path.join(PROJECT_ROOT, "images") + os.sep

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
