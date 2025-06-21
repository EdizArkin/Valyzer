# Valyzer

**Smarter Prices, Sharper Insights**

Valyzer is an AI-powered dynamic pricing and demand forecasting platform that helps businesses make data-driven pricing decisions. It leverages time-series forecasting, competitor analysis, weather data, and trend signals to recommend optimal prices for both daily essentials and travel-related services.

---

## 🚀 Features

- 📊 Demand forecasting using LSTM and Prophet  
- 💸 Pricing optimization with XGBoost  
- 🌦️ Weather and trend integration (OpenWeatherMap, Google Trends, Twitter)  
- 🔍 Competitor price scraping (e-commerce & travel sites)  
- 📈 Streamlit dashboard for interactive predictions  
- 🔁 Modular structure for easy extensibility  

---

## 🗂️ Project Structure

```
valyzer/
├── data/                               # Raw and processed datasets
├── models/                             # Trained ML models
├── notebooks/                          # Jupyter notebooks (EDA, model tests)
├── src/                                # Core modules (pricing, scraping, APIs)
│   ├── daily_essentials/
│   ├── travel/
│   ├── external/
│   └── config.py, utils.py, ...
├── app/                                # Streamlit app
│   ├── Valyzer.py                      # Main Valyzer page
│   └── pages/
│       ├── 1_Daily_Essentials.py       # Daily Essentials page   
│       └── 2_Travel.py                 # Travel and accomodation page
├── tests/                              # Unit tests
├── .env.example                        # Environment variable template
├── requirements.txt
└── README.md
```

---

## 🧪 Requirements

Python 3.8+ and the following libraries:

```bash
numpy
pandas
scikit-learn
xgboost
tensorflow
prophet
matplotlib
seaborn
streamlit
requests
beautifulsoup4
lxml
tweepy
pytrends
python-dotenv
    .
    .
    .
```

Install with:

```bash
pip install -r requirements.txt
```

---

## 🛠️ Quick Start

```bash
# Clone the repo
git clone https://github.com/EdizArkin/valyzer.git
cd valyzer

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app/Valyzer.py
```

---

## 🔐 Environment Variables

Create a `.env` file based on the provided `.env.example`:

```env
OPENWEATHERMAP_API_KEY=your_key
TWITTER_API_KEY=your_key
GOOGLE_TRENDS_REGION=TR
```

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 👨‍💻 Author

Ediz Arkın Kobak  
GitHub: [@EdizArkin](https://github.com/EdizArkin)
