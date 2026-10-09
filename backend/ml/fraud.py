"""
Fraud Detection Model
Isolation Forest for anomaly detection in transactions.
"""
import os
import sys
import joblib
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.db.mongo import get_mongo_db


class FraudDetector:
    """ML model for fraud/anomaly detection using Isolation Forest."""

    def __init__(self, model_path: str = None):
        self.model = None
        self.scaler = None
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), "models", "fraud_detector.joblib"
        )
        self.is_trained = False
        self.feature_names = [
            "amount",
            "user_avg_amount",
            "user_std_amount",
            "is_new_payee",
            "is_new_category",
            "hour_of_day",
            "is_weekend",
            "recent_txn_count_1hr",
            "amount_zscore",
            "days_since_last_txn",
        ]

    def prepare_training_data(self) -> np.ndarray:
        """Prepare feature matrix from MongoDB."""
        mongo_db = get_mongo_db()
        if mongo_db is None:
            print("MongoDB not available, generating synthetic training data")
            return self._generate_synthetic_features()

        # Get transactions with features
        cursor = mongo_db.txn_analytics.find(
            {"type": "EXPENSE"},
            {"features": 1, "amount": 1, "user_id": 1, "payee": 1, "category_id": 1, "transacted_at": 1}
        ).limit(20000)

        # First, build user profiles
        user_profiles = {}
        all_docs = list(cursor)

        for doc in all_docs:
            user_id = doc.get("user_id")
            if user_id not in user_profiles:
                user_profiles[user_id] = {"amounts": [], "payees": set(), "categories": set()}

            amount = doc.get("amount", 0)
            user_profiles[user_id]["amounts"].append(amount)
            if doc.get("payee"):
                user_profiles[user_id]["payees"].add(doc["payee"])
            if doc.get("category_id"):
                user_profiles[user_id]["categories"].add(doc["category_id"])

        # Compute user statistics
        for user_id, profile in user_profiles.items():
            amounts = profile["amounts"]
            profile["avg_amount"] = np.mean(amounts) if amounts else 0
            profile["std_amount"] = np.std(amounts) if len(amounts) > 1 else 1.0

        # Extract features
        features_list = []
        for doc in all_docs:
            features = self._extract_features(doc, user_profiles)
            features_list.append(features)

        X = np.array(features_list)
        print(f"Loaded {len(X)} samples with {X.shape[1]} features from MongoDB")
        return X

    def _generate_synthetic_features(self) -> np.ndarray:
        """Generate synthetic feature data for development."""
        n_samples = 10000
        n_features = len(self.feature_names)

        # Normal transactions (majority)
        n_normal = int(n_samples * 0.98)
        normal_features = np.random.randn(n_normal, n_features)

        # Scale features to realistic ranges
        normal_features[:, 0] = np.abs(normal_features[:, 0]) * 500 + 100  # amount
        normal_features[:, 1] = np.abs(normal_features[:, 1]) * 300 + 200  # user_avg
        normal_features[:, 2] = np.abs(normal_features[:, 2]) * 100 + 50   # user_std
        normal_features[:, 3] = np.random.binomial(1, 0.1, n_normal)       # is_new_payee
        normal_features[:, 4] = np.random.binomial(1, 0.05, n_normal)      # is_new_category
        normal_features[:, 5] = np.random.randint(0, 24, n_normal)         # hour
        normal_features[:, 6] = np.random.binomial(1, 0.3, n_normal)       # is_weekend
        normal_features[:, 7] = np.random.poisson(2, n_normal)             # recent_count
        normal_features[:, 8] = np.abs(np.random.randn(n_normal)) * 2      # zscore
        normal_features[:, 9] = np.random.exponential(2, n_normal)         # days_since

        # Anomalous transactions (2%)
        n_anomaly = n_samples - n_normal
        anomaly_features = np.random.randn(n_anomaly, n_features)

        anomaly_features[:, 0] = np.abs(anomaly_features[:, 0]) * 5000 + 1000  # high amount
        anomaly_features[:, 1] = np.abs(anomaly_features[:, 1]) * 300 + 200
        anomaly_features[:, 2] = np.abs(anomaly_features[:, 2]) * 100 + 50
        anomaly_features[:, 3] = 1  # always new payee
        anomaly_features[:, 4] = 1  # always new category
        anomaly_features[:, 5] = np.random.choice([1, 2, 3, 22, 23], n_anomaly)  # odd hours
        anomaly_features[:, 6] = np.random.binomial(1, 0.5, n_anomaly)
        anomaly_features[:, 7] = np.random.poisson(10, n_anomaly)  # high velocity
        anomaly_features[:, 8] = np.abs(np.random.randn(n_anomaly)) * 5 + 3  # high zscore
        anomaly_features[:, 9] = np.random.exponential(0.5, n_anomaly)

        X = np.vstack([normal_features, anomaly_features])
        np.random.shuffle(X)

        print(f"Generated {len(X)} synthetic samples")
        return X

    def _extract_features(self, doc: Dict, user_profiles: Dict) -> List[float]:
        """Extract features for a single transaction."""
        user_id = doc.get("user_id", "")
        profile = user_profiles.get(user_id, {})

        amount = doc.get("amount", 0)
        avg_amount = profile.get("avg_amount", amount)
        std_amount = profile.get("std_amount", 1.0)

        payee = doc.get("payee", "")
        category_id = doc.get("category_id", 0)
        transacted_at = doc.get("transacted_at")

        is_new_payee = 1 if payee and payee not in profile.get("payees", set()) else 0
        is_new_category = 1 if category_id and category_id not in profile.get("categories", set()) else 0

        # Time features
        hour = 12
        is_weekend = 0
        if transacted_at:
            if isinstance(transacted_at, str):
                try:
                    dt = datetime.fromisoformat(transacted_at.replace('Z', '+00:00'))
                    hour = dt.hour
                    is_weekend = 1 if dt.weekday() >= 5 else 0
                except:
                    pass
            elif hasattr(transacted_at, 'hour'):
                hour = transacted_at.hour
                is_weekend = 1 if transacted_at.weekday() >= 5 else 0

        # Z-score
        zscore = 0
        if std_amount > 0:
            zscore = abs(amount - avg_amount) / std_amount

        return [
            float(amount),
            float(avg_amount),
            float(std_amount),
            float(is_new_payee),
            float(is_new_category),
            float(hour),
            float(is_weekend),
            0.0,  # recent_txn_count_1hr - would need time window query
            float(zscore),
            0.0,  # days_since_last_txn
        ]

    def train(self, X: np.ndarray = None, contamination: float = 0.02):
        """Train the Isolation Forest model."""
        try:
            from sklearn.ensemble import IsolationForest
            from sklearn.preprocessing import StandardScaler
            from sklearn.model_selection import train_test_split
        except ImportError:
            print("scikit-learn not available, skipping ML training")
            return False

        if X is None:
            X = self.prepare_training_data()

        if len(X) < 50:
            print("Insufficient training data")
            return False

        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Train Isolation Forest
        self.model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=42,
            n_jobs=-1,
            max_samples='auto',
        )

        self.model.fit(X_scaled)
        self.is_trained = True

        # Evaluate on training data
        scores = self.model.score_samples(X_scaled)
        predictions = self.model.predict(X_scaled)
        n_anomalies = np.sum(predictions == -1)

        print(f"\nTraining completed:")
        print(f"  Samples: {len(X)}")
        print(f"  Detected anomalies: {n_anomalies} ({n_anomalies/len(X)*100:.2f}%)")
        print(f"  Score range: {scores.min():.4f} to {scores.max():.4f}")
        print(f"  Threshold (approx): {np.percentile(scores, contamination*100):.4f}")

        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "is_trained": self.is_trained,
            "contamination": contamination,
            "trained_at": datetime.utcnow().isoformat(),
        }, self.model_path)

        print(f"Model saved to {self.model_path}")
        return True

    def load_model(self) -> bool:
        """Load trained model from disk."""
        try:
            data = joblib.load(self.model_path)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.feature_names = data["feature_names"]
            self.is_trained = data["is_trained"]
            print(f"Model loaded from {self.model_path} (trained at {data.get('trained_at', 'unknown')})")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False

    def predict(self, features: List[float]) -> Dict[str, Any]:
        """Predict anomaly for a single transaction."""
        if not self.is_trained or self.model is None or self.scaler is None:
            return {"is_anomaly": False, "score": 0.0, "risk_level": "unknown"}

        try:
            X = np.array(features).reshape(1, -1)
            X_scaled = self.scaler.transform(X)

            # Get anomaly score (lower = more anomalous)
            score = self.model.score_samples(X_scaled)[0]
            prediction = self.model.predict(X_scaled)[0]

            # Convert to 0-1 risk score (higher = more risky)
            # Isolation Forest scores are negative, more negative = more anomalous
            # Normalize: clip and invert
            normalized_score = max(0, min(1, -score / 0.5))

            risk_level = "low"
            if normalized_score >= 0.7:
                risk_level = "high"
            elif normalized_score >= 0.4:
                risk_level = "medium"

            return {
                "is_anomaly": prediction == -1,
                "score": float(normalized_score),
                "raw_score": float(score),
                "risk_level": risk_level,
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            return {"is_anomaly": False, "score": 0.0, "risk_level": "error"}

    def predict_batch(self, features_list: List[List[float]]) -> List[Dict[str, Any]]:
        """Predict anomalies for multiple transactions."""
        if not self.is_trained or self.model is None or self.scaler is None:
            return [{"is_anomaly": False, "score": 0.0, "risk_level": "unknown"} for _ in features_list]

        try:
            X = np.array(features_list)
            X_scaled = self.scaler.transform(X)

            scores = self.model.score_samples(X_scaled)
            predictions = self.model.predict(X_scaled)

            results = []
            for score, pred in zip(scores, predictions):
                normalized = max(0, min(1, -score / 0.5))
                risk = "low"
                if normalized >= 0.7:
                    risk = "high"
                elif normalized >= 0.4:
                    risk = "medium"

                results.append({
                    "is_anomaly": pred == -1,
                    "score": float(normalized),
                    "raw_score": float(score),
                    "risk_level": risk,
                })

            return results
        except Exception as e:
            print(f"Batch prediction error: {e}")
            return [{"is_anomaly": False, "score": 0.0, "risk_level": "error"} for _ in features_list]


def main():
    """Train the fraud detection model."""
    print("=" * 60)
    print("FinSight Fraud Detection Model Training")
    print("=" * 60)

    detector = FraudDetector()
    success = detector.train()

    if success:
        print("\nTraining completed successfully!")
    else:
        print("\nTraining failed or skipped.")


if __name__ == "__main__":
    main()