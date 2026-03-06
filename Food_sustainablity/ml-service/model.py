import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

MODEL_PATH = "surplus_model.pkl"

def generate_mock_data():
    """Generates synthetic data for training the surplus prediction model"""
    np.random.seed(42)
    n_samples = 1000
    
    # 0 = Mon, ..., 6 = Sun
    day_of_week = np.random.randint(0, 7, n_samples)
    
    # Weather: 0 = Clear, 1 = Rain, 2 = Storm
    weather = np.random.choice([0, 1, 2], n_samples, p=[0.7, 0.2, 0.1])
    
    # Events: 0 = No, 1 = Yes
    events = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
    
    # Historical sales (normalized 0 to 1)
    sales = np.random.rand(n_samples)
    
    # Label: 1 = Surplus Expected, 0 = No Surplus
    # Logic: More likely to have surplus if bad weather, or weekend, or event, or low sales
    surplus_prob = (
        (weather > 0) * 0.3 + 
        (day_of_week >= 5) * 0.2 + 
        (events == 1) * 0.4 + 
        (sales < 0.4) * 0.2
    )
    
    y = (surplus_prob + np.random.randn(n_samples) * 0.1) > 0.5
    y = y.astype(int)
    
    X = pd.DataFrame({
        'day_of_week': day_of_week,
        'weather': weather,
        'has_event': events,
        'recent_sales_ratio': sales
    })
    
    return X, y

def train_and_save_model():
    print("Generating mock dataset...")
    X, y = generate_mock_data()
    
    print("Training RandomForest model...")
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    print(f"Saving model to {MODEL_PATH}...")
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print("Done!")

class SurplusPredictor:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            train_and_save_model()
        
        with open(MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)

    def predict(self, day_of_week: int, weather: int, has_event: int, recent_sales_ratio: float, total_meals_cooked: int):
        X = pd.DataFrame([{
            'day_of_week': day_of_week,
            'weather': weather,
            'has_event': has_event,
            'recent_sales_ratio': recent_sales_ratio
        }])
        
        prob = self.model.predict_proba(X)[0][1]
        
        # Explain reasoning
        reasons = []
        if has_event:
            reasons.append("weekend event demand")
        if day_of_week >= 5:
            reasons.append("weekend historical surplus patterns")
        if weather > 0:
            reasons.append("poor weather conditions")
        if recent_sales_ratio < 0.5:
            reasons.append("lower than expected recent sales patterns")
            
        reason_str = "Prediction based on: " + " and ".join(reasons) if prob > 0.5 else "Low surplus expected based on normal operating patterns."
        
        if prob > 0.5 and not reasons:
            reason_str = "Prediction based on general historical surplus trends."

        expected_meals = int(total_meals_cooked * prob * 0.35)
        if expected_meals < 5: expected_meals = 5 # baseline prediction
            
        return {
            "surplus_probability": round(prob, 2),
            "is_surplus_expected": bool(prob > 0.5),
            "reason": reason_str,
            "predicted_quantity": f"{expected_meals} surplus meals expected",
            "suggested_time": "09:30 PM" if day_of_week >= 5 else "08:00 PM"
        }

if __name__ == "__main__":
    train_and_save_model()
