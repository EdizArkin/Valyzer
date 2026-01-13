# models/travel_forecaster.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


class TravelForecaster:
    """
    Travel price forecaster that analyzes flight prices and recommends
    the optimal number of days before departure to buy a ticket.
    
    The model learns from the price patterns in the data window and
    predicts: "If you want to fly on date X, buy your ticket Y days before."
    """
    
    def __init__(self):
        self.model = None
        self.rmse = None
        self.forecast_df = None
        self.target_date = None
        self.min_price_data = None
        
    def preprocess(self, df: pd.DataFrame, flight_date: str) -> pd.DataFrame:
        """
        Preprocess the flight data for training.
        
        Args:
            df: DataFrame with columns ['date', 'price', ...]
            flight_date: Target flight date (the date user wants to travel)
            
        Returns:
            Cleaned DataFrame ready for training
        """
        df = df.copy()
        self.target_date = pd.to_datetime(flight_date)
        today = pd.to_datetime(datetime.today().date())
        
        # Parse date and price
        df["ds"] = pd.to_datetime(df["date"])
        
        # Extract numeric price (handle formats like "123.45 EUR" or "123.45 EUR - for [2 Adults]")
        df["y"] = df["price"].astype(str).str.extract(r'([\d.]+)')[0].astype(float)
        
        # Calculate days until flight for each row
        # This represents: "How many days before the flight date is this price for?"
        df["days_until_flight"] = (df["ds"] - today).dt.days
        
        # Feature engineering
        df["day_of_week"] = df["ds"].dt.dayofweek  # 0=Monday, 6=Sunday
        df["is_weekend"] = df["ds"].dt.dayofweek >= 5
        df["week_of_year"] = df["ds"].dt.isocalendar().week.astype(int)
        df["month"] = df["ds"].dt.month
        
        # Days from target date (negative = before target, positive = after target)
        df["days_from_target"] = (df["ds"] - self.target_date).dt.days
        
        # Keep minimum price per date (best offer for each day)
        df_grouped = df.groupby("ds").agg({
            "y": "min",
            "days_until_flight": "first",
            "day_of_week": "first",
            "is_weekend": "first",
            "week_of_year": "first",
            "month": "first",
            "days_from_target": "first"
        }).reset_index()
        
        print(f"\n[DEBUG] Preprocessed {len(df_grouped)} unique dates")
        print(f"[DEBUG] Target flight date: {self.target_date.strftime('%Y-%m-%d')}")
        print(f"[DEBUG] Price range: {df_grouped['y'].min():.2f} - {df_grouped['y'].max():.2f}")
        
        return df_grouped
    
    def train(self, df: pd.DataFrame):
        """
        Train the forecasting model using the preprocessed data.
        
        The model learns the relationship between:
        - Days until flight
        - Day of week patterns
        - Seasonal patterns
        And the corresponding prices.
        """
        if len(df) < 5:
            print("[WARNING] Not enough data points for reliable training")
            self.rmse = None
            return
            
        # Features for training
        feature_cols = ["days_until_flight", "day_of_week", "is_weekend", "month", "days_from_target"]
        X = df[feature_cols].values
        y = df["y"].values
        
        # Train-test split (if enough data)
        if len(df) >= 10:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
        else:
            X_train, X_test, y_train, y_test = X, X, y, y
        
        # Train Gradient Boosting model
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.1,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        
        # Calculate RMSE on test set
        y_pred = self.model.predict(X_test)
        self.rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"[DEBUG] Model trained with RMSE: {self.rmse:.2f}")
        
        # Store the data for recommendations
        self.min_price_data = df.copy()
    
    def forecast(self, flight_date: str, window: int = 14) -> pd.DataFrame:
        """
        Generate price forecasts for buying tickets at different days before the flight.
        
        Args:
            flight_date: The date user wants to travel
            window: How many days back to analyze for purchase recommendation
            
        Returns:
            DataFrame with forecasted prices for each purchase day
        """
        if self.model is None:
            return pd.DataFrame()
            
        target_date = pd.to_datetime(flight_date)
        today = pd.to_datetime(datetime.today().date())
        
        # Generate dates from today to flight date
        days_to_flight = (target_date - today).days
        
        if days_to_flight <= 0:
            # Flight is today or in the past
            return pd.DataFrame()
        
        # Create future dates for prediction (from today to flight date)
        future_dates = pd.date_range(today, target_date - timedelta(days=1))
        
        # Build prediction dataframe
        predictions = []
        for purchase_date in future_dates:
            days_until = (target_date - purchase_date).days
            
            features = {
                "ds": purchase_date,
                "days_until_flight": days_until,
                "day_of_week": purchase_date.dayofweek,
                "is_weekend": purchase_date.dayofweek >= 5,
                "month": purchase_date.month,
                "days_from_target": (purchase_date - target_date).days
            }
            predictions.append(features)
        
        if not predictions:
            return pd.DataFrame()
            
        df_future = pd.DataFrame(predictions)
        
        # Predict prices
        feature_cols = ["days_until_flight", "day_of_week", "is_weekend", "month", "days_from_target"]
        X_future = df_future[feature_cols].values
        df_future["yhat"] = self.model.predict(X_future)
        
        # Add confidence interval (simple estimate based on RMSE)
        if self.rmse:
            df_future["yhat_lower"] = df_future["yhat"] - 1.96 * self.rmse
            df_future["yhat_upper"] = df_future["yhat"] + 1.96 * self.rmse
        else:
            df_future["yhat_lower"] = df_future["yhat"]
            df_future["yhat_upper"] = df_future["yhat"]
        
        self.forecast_df = df_future
        return df_future
    
    def recommend_buy_day(self) -> tuple:
        """
        Recommend the best day to buy the ticket based on the forecast.
        
        Returns:
            tuple: (days_before_flight, predicted_price)
                - days_before_flight: Optimal number of days before departure to buy
                - predicted_price: Expected price if bought on that day
        """
        # Strategy 1: Use forecast if available
        if self.forecast_df is not None and not self.forecast_df.empty:
            best_row = self.forecast_df.loc[self.forecast_df["yhat"].idxmin()]
            days_before = int(best_row["days_until_flight"])
            best_price = float(best_row["yhat"])
            return days_before, round(best_price, 2)
        
        # Strategy 2: Use actual data if forecast not available
        if self.min_price_data is not None and not self.min_price_data.empty:
            best_row = self.min_price_data.loc[self.min_price_data["y"].idxmin()]
            days_before = int(best_row["days_until_flight"])
            best_price = float(best_row["y"])
            return days_before, round(best_price, 2)
        
        return None, None
    
    def get_model_rmse(self) -> float:
        """Return the model's RMSE score."""
        return self.rmse
    
    def get_price_trend_summary(self) -> dict:
        """
        Get a summary of price trends from the data.
        
        Returns:
            Dictionary with trend insights
        """
        if self.min_price_data is None or self.min_price_data.empty:
            return {}
        
        df = self.min_price_data
        
        # Weekend vs weekday analysis
        weekend_avg = df[df["is_weekend"]]["y"].mean() if df["is_weekend"].any() else None
        weekday_avg = df[~df["is_weekend"]]["y"].mean() if (~df["is_weekend"]).any() else None
        
        # Best day of week
        day_avg = df.groupby("day_of_week")["y"].mean()
        best_day = day_avg.idxmin() if not day_avg.empty else None
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        return {
            "weekend_avg": round(weekend_avg, 2) if weekend_avg else None,
            "weekday_avg": round(weekday_avg, 2) if weekday_avg else None,
            "best_day_of_week": day_names[best_day] if best_day is not None else None,
            "min_price": round(df["y"].min(), 2),
            "max_price": round(df["y"].max(), 2),
            "avg_price": round(df["y"].mean(), 2)
        }
