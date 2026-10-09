"""
Transaction Categorization Model
TF-IDF + Logistic Regression classifier for transaction categorization.
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


class TransactionCategorizer:
    """ML model for transaction categorization."""

    def __init__(self, model_path: str = None):
        self.model = None
        self.vectorizer = None
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), "models", "categorizer.joblib"
        )
        self.categories = {
            1: "Income",
            2: "Food & Dining",
            3: "Transport",
            4: "Rent",
            5: "Education",
            6: "Subscriptions",
            7: "Shopping",
            8: "Entertainment",
            9: "Health",
            10: "Savings",
            11: "Other",
        }
        self.is_trained = False

    def prepare_training_data(self) -> List[Dict[str, Any]]:
        """Prepare training data from MongoDB."""
        mongo_db = get_mongo_db()
        if mongo_db is None:
            print("MongoDB not available, using synthetic training data")
            return self._get_synthetic_training_data()

        # Get transactions with category labels
        cursor = mongo_db.txn_analytics.find(
            {"category_id": {"$ne": 0}},  # Exclude transfers
            {"payee": 1, "notes": 1, "category_id": 1}
        ).limit(10000)

        training_data = []
        for doc in cursor:
            text = f"{doc.get('payee', '')} {doc.get('notes', '')}".strip().lower()
            if text and doc.get('category_id') in self.categories:
                training_data.append({
                    "text": text,
                    "category_id": doc['category_id']
                })

        print(f"Loaded {len(training_data)} training samples from MongoDB")
        return training_data

    def _get_synthetic_training_data(self) -> List[Dict[str, Any]]:
        """Generate synthetic training data for development."""
        synthetic = []
        # Income
        for payee in ["Monthly Allowance", "Stipend", "Part-time Job", "Freelance", "Internship", "Scholaryship"]:
            for _ in range(50):
                synthetic.append({"text": payee.lower(), "category_id": 1})

        # Food & Dining
        for payee in ["Zomato", "Swiggy", "College Canteen", "Local Restaurant", "Coffee Shop", "Mess Bill", "Food Court"]:
            for _ in range(80):
                synthetic.append({"text": payee.lower(), "category_id": 2})

        # Transport
        for payee in ["Uber", "Ola", "Rapido", "Metro Card", "Bus Pass", "Petrol Pump", "Auto Rickshaw", "Train Ticket"]:
            for _ in range(60):
                synthetic.append({"text": payee.lower(), "category_id": 3})

        # Rent
        for payee in ["Hostel Rent", "PG Accommodation", "Apartment Rent", "Security Deposit"]:
            for _ in range(40):
                synthetic.append({"text": payee.lower(), "category_id": 4})

        # Education
        for payee in ["College Fees", "Exam Fees", "Course Materials", "Online Course", "Certification", "Books"]:
            for _ in range(30):
                synthetic.append({"text": payee.lower(), "category_id": 5})

        # Subscriptions
        for payee in ["Netflix", "Spotify", "Amazon Prime", "YouTube Premium", "GitHub Copilot", "Cloud Storage"]:
            for _ in range(30):
                synthetic.append({"text": payee.lower(), "category_id": 6})

        # Shopping
        for payee in ["Amazon", "Flipkart", "Myntra", "Electronics Store", "Clothing Store", "Mobile Recharge"]:
            for _ in range(50):
                synthetic.append({"text": payee.lower(), "category_id": 7})

        # Entertainment
        for payee in ["Movie Theater", "Steam", "PlayStation Store", "Concert Tickets", "Gaming", "Events"]:
            for _ in range(30):
                synthetic.append({"text": payee.lower(), "category_id": 8})

        # Health
        for payee in ["Pharmacy", "Doctor Consultation", "Hospital", "Gym Membership", "Health Checkup", "Medicines"]:
            for _ in range(30):
                synthetic.append({"text": payee.lower(), "category_id": 9})

        # Savings
        for payee in ["SIP Investment", "Fixed Deposit", "PPF", "Emergency Fund", "Mutual Fund"]:
            for _ in range(20):
                synthetic.append({"text": payee.lower(), "category_id": 10})

        # Other
        for payee in ["Miscellaneous", "Cash Withdrawal", "Gift", "Donation", "Other"]:
            for _ in range(30):
                synthetic.append({"text": payee.lower(), "category_id": 11})

        print(f"Generated {len(synthetic)} synthetic training samples")
        return synthetic

    def train(self, training_data: List[Dict[str, Any]] = None):
        """Train the categorization model."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import Pipeline
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import classification_report, accuracy_score
        except ImportError:
            print("scikit-learn not available, skipping ML training")
            return False

        if training_data is None:
            training_data = self.prepare_training_data()

        if len(training_data) < 10:
            print("Insufficient training data")
            return False

        texts = [item["text"] for item in training_data]
        labels = [item["category_id"] for item in training_data]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )

        # Create pipeline
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        self.model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced',
            C=1.0
        )

        # Train
        X_train_vec = self.vectorizer.fit_transform(X_train)
        self.model.fit(X_train_vec, y_train)

        # Evaluate
        X_test_vec = self.vectorizer.transform(X_test)
        y_pred = self.model.predict(X_test_vec)

        accuracy = accuracy_score(y_test, y_pred)
        print(f"\nModel Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=[self.categories.get(i, f"Cat {i}") for i in sorted(set(y_test))]))

        self.is_trained = True

        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "vectorizer": self.vectorizer,
            "categories": self.categories,
            "is_trained": self.is_trained,
            "trained_at": datetime.utcnow().isoformat(),
        }, self.model_path)

        print(f"Model saved to {self.model_path}")
        return True

    def load_model(self) -> bool:
        """Load trained model from disk."""
        try:
            data = joblib.load(self.model_path)
            self.model = data["model"]
            self.vectorizer = data["vectorizer"]
            self.categories = data["categories"]
            self.is_trained = data["is_trained"]
            print(f"Model loaded from {self.model_path} (trained at {data.get('trained_at', 'unknown')})")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False

    def predict(self, payee: str = "", notes: str = "") -> int:
        """Predict category for a transaction."""
        text = f"{payee} {notes}".strip().lower()

        if not text:
            return 11  # Other

        # Rule-based fallback (from categorization_service)
        rule_based = self._rule_based_predict(text)
        if rule_based != 11:
            return rule_based

        # ML prediction
        if self.is_trained and self.model is not None and self.vectorizer is not None:
            try:
                X = self.vectorizer.transform([text])
                prediction = self.model.predict(X)[0]
                return int(prediction)
            except:
                pass

        return 11  # Other

    def predict_proba(self, payee: str = "", notes: str = "") -> Dict[int, float]:
        """Get prediction probabilities for all categories."""
        text = f"{payee} {notes}".strip().lower()

        if not text or not self.is_trained or self.model is None:
            return {}

        try:
            X = self.vectorizer.transform([text])
            probas = self.model.predict_proba(X)[0]
            classes = self.model.classes_
            return {int(cls): float(prob) for cls, prob in zip(classes, probas)}
        except:
            return {}

    def _rule_based_predict(self, text: str) -> int:
        """Rule-based categorization as fallback."""
        keywords = {
            1: ["salary", "allowance", "stipend", "income", "wage", "payroll"],
            2: ["zomato", "swiggy", "canteen", "restaurant", "cafe", "mess", "dining", "lunch", "dinner", "breakfast", "food"],
            3: ["uber", "ola", "rapido", "metro", "bus", "train", "petrol", "fuel", "gas", "auto", "rickshaw", "cab", "taxi"],
            4: ["rent", "hostel", "pg", "accommodation", "housing", "lease"],
            5: ["college", "university", "course", "exam", "fee", "tuition", "book", "education", "udemy", "coursera"],
            6: ["netflix", "spotify", "prime", "hotstar", "subscription", "apple music", "youtube premium", "github"],
            7: ["amazon", "flipkart", "myntra", "ajio", "shopping", "clothes", "electronics", "mobile", "laptop"],
            8: ["movie", "cinema", "game", "steam", "playstation", "xbox", "entertainment", "concert", "event"],
            9: ["pharmacy", "medicine", "doctor", "hospital", "clinic", "health", "gym", "fitness", "medical"],
            10: ["savings", "investment", "mutual fund", "sip", "fd", "rd", "ppf", "nps"],
        }

        for cat_id, kws in keywords.items():
            for kw in kws:
                if kw in text:
                    return cat_id

        return 11


def main():
    """Train the categorization model."""
    print("=" * 60)
    print("FinSight Categorization Model Training")
    print("=" * 60)

    categorizer = TransactionCategorizer()
    success = categorizer.train()

    if success:
        print("\nTraining completed successfully!")
    else:
        print("\nTraining failed or skipped.")


if __name__ == "__main__":
    main()