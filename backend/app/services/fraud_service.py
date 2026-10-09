"""
Fraud Detection Service - Rule-based + ML anomaly detection
"""
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np

# For Isolation Forest (optional ML)
try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class FraudService:
    """Service for fraud/anomaly detection on transactions."""

    def __init__(self):
        self.model = None
        self.user_profiles = {}  # In-memory cache of user spending patterns

    def score_transaction(self, user_id: str, amount: Decimal, payee: str = None,
                         category_id: int = None, transacted_at: datetime = None,
                         account_id: str = None) -> float:
        """
        Score a transaction for fraud risk (0.0 to 1.0).
        Combines rule-based and ML approaches.
        """
        # Rule-based scoring
        rule_score = self._rule_based_score(user_id, amount, payee, category_id, transacted_at)

        # ML-based scoring (if available and trained)
        ml_score = 0.0
        if SKLEARN_AVAILABLE and self.model is not None:
            features = self._extract_features(user_id, amount, payee, category_id, transacted_at, account_id)
            ml_score = self._ml_score(features)

        # Weighted combination (70% rules, 30% ML if available)
        if SKLEARN_AVAILABLE and self.model is not None:
            final_score = 0.7 * rule_score + 0.3 * ml_score
        else:
            final_score = rule_score

        return min(max(final_score, 0.0), 1.0)

    def _rule_based_score(self, user_id: str, amount: Decimal, payee: str = None,
                         category_id: int = None, transacted_at: datetime = None) -> float:
        """Calculate rule-based fraud score."""
        score = 0.0
        profile = self.user_profiles.get(user_id, {})

        # 1. Amount deviation from user's mean (z-score)
        user_mean = profile.get("avg_amount", float(amount))
        user_std = profile.get("std_amount", 1.0)
        if user_std > 0:
            z_score = abs(float(amount) - user_mean) / user_std
            if z_score > 3:
                score += 0.4
            elif z_score > 2:
                score += 0.2

        # 2. New payee
        known_payees = profile.get("payees", set())
        if payee and payee not in known_payees:
            score += 0.25

        # 3. Time-based anomalies
        if transacted_at:
            hour = transacted_at.hour
            # Late night / early morning (12am - 5am)
            if 0 <= hour <= 5:
                score += 0.15
            # Weekend
            if transacted_at.weekday() >= 5:
                score += 0.05

        # 4. Velocity check (would need recent transaction count)
        # This would be implemented with a proper DB query
        recent_txn_count = profile.get("recent_txn_count_1hr", 0)
        if recent_txn_count >= 8:
            score += 0.2

        # 5. Category anomaly
        user_categories = profile.get("categories", set())
        if category_id and category_id not in user_categories:
            score += 0.1

        return min(score, 1.0)

    def _extract_features(self, user_id: str, amount: Decimal, payee: str = None,
                         category_id: int = None, transacted_at: datetime = None,
                         account_id: str = None) -> np.ndarray:
        """Extract features for ML model."""
        profile = self.user_profiles.get(user_id, {})

        features = [
            float(amount),
            profile.get("avg_amount", float(amount)),
            profile.get("std_amount", 1.0),
            1 if payee and payee not in profile.get("payees", set()) else 0,
            1 if category_id and category_id not in profile.get("categories", set()) else 0,
            transacted_at.hour if transacted_at else 12,
            1 if transacted_at and transacted_at.weekday() >= 5 else 0,
            profile.get("recent_txn_count_1hr", 0),
        ]

        return np.array(features).reshape(1, -1)

    def _ml_score(self, features: np.ndarray) -> float:
        """Get anomaly score from Isolation Forest."""
        try:
            # Isolation Forest returns -1 for anomalies, 1 for normal
            # We convert to 0-1 scale
            prediction = self.model.predict(features)[0]
            score = self.model.score_samples(features)[0]
            # Normalize score (more negative = more anomalous)
            normalized = max(0, min(1, -score / 0.5))
            return normalized if prediction == -1 else 0.0
        except:
            return 0.0

    def update_user_profile(self, user_id: str, transactions: List[Dict]) -> None:
        """Update user spending profile from transaction history."""
        if not transactions:
            return

        amounts = [float(t.get("amount", 0)) for t in transactions]
        payees = set(t.get("payee") for t in transactions if t.get("payee"))
        categories = set(t.get("category_id") for t in transactions if t.get("category_id"))

        self.user_profiles[user_id] = {
            "avg_amount": np.mean(amounts) if amounts else 0,
            "std_amount": np.std(amounts) if len(amounts) > 1 else 1.0,
            "payees": payees,
            "categories": categories,
            "txn_count": len(transactions),
        }

    def train_model(self, all_transactions: List[Dict]) -> None:
        """Train Isolation Forest model on historical data."""
        if not SKLEARN_AVAILABLE or not all_transactions:
            return

        # Extract features for all transactions
        X = []
        for txn in all_transactions:
            user_profile = self.user_profiles.get(txn.get("user_id"), {})
            features = [
                float(txn.get("amount", 0)),
                user_profile.get("avg_amount", 0),
                user_profile.get("std_amount", 1.0),
                1 if txn.get("payee") and txn.get("payee") not in user_profile.get("payees", set()) else 0,
                1 if txn.get("category_id") and txn.get("category_id") not in user_profile.get("categories", set()) else 0,
                txn.get("hour", 12),
                1 if txn.get("is_weekend", False) else 0,
                0,  # velocity - would need computation
            ]
            X.append(features)

        if len(X) > 10:
            X = np.array(X)
            self.model = IsolationForest(contamination=0.02, random_state=42)
            self.model.fit(X)