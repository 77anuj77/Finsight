"""
Categorization Service - Rule-based + ML auto-categorization
"""
from typing import Dict, List, Optional
import re

# Optional ML
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class CategorizationService:
    """Service for automatic transaction categorization."""

    # Rule-based keyword mapping (category_id -> keywords)
    CATEGORY_KEYWORDS = {
        1: ["salary", "allowance", "stipend", "income", "wage", "payroll"],  # Income
        2: ["zomato", "swiggy", "uber eats", "food", "restaurant", "cafe", "mess", "canteen", "dining", "lunch", "dinner", "breakfast"],  # Food & Dining
        3: ["uber", "ola", "rapido", "metro", "bus", "train", "petrol", "fuel", "gas", "auto", "rickshaw", "cab", "taxi"],  # Transport
        4: ["rent", "hostel", "pg", "accommodation", "housing", "lease"],  # Rent
        5: ["college", "university", "course", "exam", "fee", "tuition", "book", "education", "udemy", "coursera"],  # Education
        6: ["netflix", "spotify", "prime", "hotstar", "subscription", "apple music", "youtube premium", "git hub", "github"],  # Subscriptions
        7: ["amazon", "flipkart", "myntra", "ajio", "shopping", "clothes", "electronics", "mobile", "laptop"],  # Shopping
        8: ["movie", "cinema", "game", "steam", "playstation", "xbox", "entertainment", "concert", "event"],  # Entertainment
        9: ["pharmacy", "medicine", "doctor", "hospital", "clinic", "health", "gym", "fitness", "medical"],  # Health
        10: ["savings", "investment", "mutual fund", "sip", "fd", "rd", "ppf", "nps"],  # Savings
        11: ["other", "misc", "miscellaneous", "unknown"],  # Other
    }

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.is_trained = False

    def predict(self, payee: str = "", notes: str = "") -> int:
        """
        Predict category from payee and notes.
        Returns category_id (default 11 for Other).
        """
        text = f"{payee} {notes}".lower().strip()

        if not text:
            return 11  # Other

        # Rule-based matching
        for cat_id, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    return cat_id

        # ML fallback (if trained)
        if self.is_trained and SKLEARN_AVAILABLE:
            try:
                return self._ml_predict(text)
            except:
                pass

        return 11  # Other

    def _ml_predict(self, text: str) -> int:
        """Predict using trained ML model."""
        if self.model is None or self.vectorizer is None:
            return 11

        X = self.vectorizer.transform([text])
        prediction = self.model.predict(X)[0]
        return int(prediction)

    def train(self, training_data: List[Dict]) -> None:
        """
        Train ML model on labeled data.
        training_data: list of {"text": "payee notes", "category_id": int}
        """
        if not SKLEARN_AVAILABLE or not training_data:
            return

        texts = [item["text"].lower() for item in training_data]
        labels = [item["category_id"] for item in training_data]

        # Create pipeline
        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        self.model = LogisticRegression(max_iter=1000, random_state=42)

        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)
        self.is_trained = True

    def save_model(self, path: str) -> None:
        """Save trained model to disk."""
        if SKLEARN_AVAILABLE and self.is_trained:
            joblib.dump({
                "model": self.model,
                "vectorizer": self.vectorizer,
                "is_trained": self.is_trained,
            }, path)

    def load_model(self, path: str) -> bool:
        """Load trained model from disk."""
        if not SKLEARN_AVAILABLE:
            return False

        try:
            import joblib
            data = joblib.load(path)
            self.model = data["model"]
            self.vectorizer = data["vectorizer"]
            self.is_trained = data["is_trained"]
            return True
        except:
            return False

    def get_category_suggestions(self, text: str, top_k: int = 3) -> List[Dict]:
        """Get top category suggestions with confidence."""
        text = text.lower().strip()

        if not text:
            return []

        # Rule-based scores
        scores = {}
        for cat_id, keywords in self.CATEGORY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 1
            if score > 0:
                scores[cat_id] = score

        # ML scores if available
        if self.is_trained and SKLEARN_AVAILABLE and self.model is not None:
            try:
                X = self.vectorizer.transform([text])
                probas = self.model.predict_proba(X)[0]
                classes = self.model.classes_
                for cls, prob in zip(classes, probas):
                    if cls in scores:
                        scores[cls] += prob * 2  # Weight ML higher
                    else:
                        scores[cls] = prob * 2
            except:
                pass

        # Sort and return top k
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [
            {"category_id": cat_id, "confidence": min(score / 3.0, 1.0)}
            for cat_id, score in sorted_cats
        ]