import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(BASE_DIR, "student_model.pkl")
SCALER_FILE = os.path.join(BASE_DIR, "scaler.pkl")

class StudentModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.features = ['attendance', 'study_hours', 'previous_grades', 
                        'assignments_completed', 'participation']
        self.load_model()

    def load_model(self):
        """Load model and scaler from disk if they exist"""
        if os.path.exists(MODEL_FILE) and os.path.exists(SCALER_FILE):
            try:
                self.model = joblib.load(MODEL_FILE)
                self.scaler = joblib.load(SCALER_FILE)
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model = None
                self.scaler = None

    def train(self, df):
        """Train the model and save it"""
        if df.empty:
            return False

        # Calculate performance if not present (logic preserved from original app.py)
        if 'performance' not in df.columns:
             df['performance'] = (
                df['attendance'] * 0.25 +
                df['study_hours'] * 3 * 0.20 +
                df['previous_grades'] * 0.30 +
                df['assignments_completed'] * 0.15 +
                (df['participation'] / 3 * 100) * 0.10
            )

        X = df[self.features]
        y = df['performance']

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)

        # Save model and scaler
        joblib.dump(self.model, MODEL_FILE)
        joblib.dump(self.scaler, SCALER_FILE)
        return True

    def predict(self, data):
        """Predict performance for a single student"""
        if self.model is None or self.scaler is None:
            # Fallback to heuristic calculation if model isn't trained
            predicted_score = (
                data['attendance'] * 0.25 +
                data['study_hours'] * 3 * 0.20 +
                data['previous_grades'] * 0.30 +
                data['assignments_completed'] * 0.15 +
                (data['participation'] / 3 * 100) * 0.10
            )
            return min(predicted_score, 100)

        features_arr = np.array([[
            data['attendance'],
            data['study_hours'],
            data['previous_grades'],
            data['assignments_completed'],
            data['participation']
        ]])
        
        features_scaled = self.scaler.transform(features_arr)
        predicted_score = self.model.predict(features_scaled)[0]
        return min(predicted_score, 100)

    def get_feature_importance(self):
        """Return feature importance dict"""
        if self.model is None:
            return {}
        
        importances = self.model.feature_importances_
        return dict(zip(self.features, importances))
