"""
Training Pipeline for FinSight ML Models
Orchestrates training of categorization and fraud detection models.
"""
import os
import sys
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ml.categorize import TransactionCategorizer
from backend.ml.fraud import FraudDetector


def train_all_models():
    """Train all ML models and generate model cards."""
    print("=" * 60)
    print("FinSight ML Training Pipeline")
    print("=" * 60)

    results = {
        "pipeline_run_at": datetime.utcnow().isoformat(),
        "models": {}
    }

    # Train categorization model
    print("\n[1/2] Training Transaction Categorization Model...")
    categorizer = TransactionCategorizer()
    cat_success = categorizer.train()

    results["models"]["categorization"] = {
        "model_type": "TF-IDF + Logistic Regression",
        "status": "success" if cat_success else "failed",
        "model_path": categorizer.model_path,
        "categories": categorizer.categories,
        "trained_at": datetime.utcnow().isoformat() if cat_success else None,
    }

    # Train fraud detection model
    print("\n[2/2] Training Fraud Detection Model...")
    detector = FraudDetector()
    fraud_success = detector.train()

    results["models"]["fraud_detection"] = {
        "model_type": "Isolation Forest",
        "status": "success" if fraud_success else "failed",
        "model_path": detector.model_path,
        "feature_names": detector.feature_names,
        "contamination": 0.02,
        "trained_at": datetime.utcnow().isoformat() if fraud_success else None,
    }

    # Save model card
    model_card_path = os.path.join(os.path.dirname(__file__), "model_card.md")
    generate_model_card(results, model_card_path)

    # Print summary
    print("\n" + "=" * 60)
    print("TRAINING PIPELINE COMPLETE")
    print("=" * 60)
    for name, info in results["models"].items():
        print(f"  {name}: {info['status'].upper()}")

    print(f"\nModel card saved to: {model_card_path}")
    return results


def generate_model_card(results: dict, output_path: str):
    """Generate model card markdown."""
    md = f"""# FinSight ML Model Card

**Pipeline Run:** {results['pipeline_run_at']}

---

## Models Overview

| Model | Type | Status | Path |
|-------|------|--------|------|
| Transaction Categorization | TF-IDF + Logistic Regression | {results['models']['categorization']['status'].upper()} | `{results['models']['categorization']['model_path']}` |
| Fraud Detection | Isolation Forest | {results['models']['fraud_detection']['status'].upper()} | `{results['models']['fraud_detection']['model_path']}` |

---

## Transaction Categorization Model

**Model Type:** TF-IDF Vectorizer + Logistic Regression
**Categories:** {len(results['models']['categorization']['categories'])} categories
**Training Data:** MongoDB `txn_analytics` collection (payee + notes → category_id)
**Fallback:** Rule-based keyword matching

### Category Mapping
"""

    for cat_id, cat_name in results['models']['categorization']['categories'].items():
        md += f"- **{cat_id}**: {cat_name}\n"

    md += f"""
### Performance Metrics (if trained)
- Accuracy: [from training output]
- Per-class Precision/Recall/F1: [from classification_report]

### Intended Use
Automatic categorization of user transactions based on payee name and notes.
Used when rule-based categorization fails to match.

### Limitations
- Requires sufficient training data per category
- May misclassify novel payees not seen during training
- Rule-based fallback handles common cases

---

## Fraud Detection Model

**Model Type:** Isolation Forest (Unsupervised Anomaly Detection)
**Contamination:** 2% (expected anomaly rate)
**Features:** {len(results['models']['fraud_detection']['feature_names'])} features

### Feature List
"""

    for i, feat in enumerate(results['models']['fraud_detection']['feature_names']):
        md += f"{i+1}. `{feat}`\n"

    md += f"""
### Training Data
MongoDB `txn_analytics` collection (EXPENSE transactions only)
User profiles built from historical spending patterns.

### Intended Use
Real-time anomaly scoring of new transactions.
Combines with rule-based scoring in `FraudService`.

### Risk Levels
- **High** (score ≥ 0.7): Flag as SUSPICIOUS, require user confirmation
- **Medium** (0.4 ≤ score < 0.7): Flag as REVIEW
- **Low** (score < 0.4): NORMAL

### Limitations
- Unsupervised - no ground truth labels for fraud
- Requires user feedback loop for continuous improvement
- Cold start problem for new users (uses population defaults)

---

## Data Pipeline

1. **Source:** PostgreSQL `transactions` table
2. **Sync:** `SyncService` denormalizes to MongoDB `txn_analytics`
3. **Features:** Computed per-user statistics (avg, std, known payees/categories)
4. **Training:** Batch job (monthly or on-demand)
5. **Serving:** Models loaded into `FraudService` and `CategorizationService`

---

## Monitoring & Retraining

- **Frequency:** Monthly retraining recommended
- **Drift Detection:** Monitor prediction distributions
- **Feedback Loop:** User confirm/reject of flagged transactions
- **A/B Testing:** Compare rule-based vs ML-enhanced scoring

---

## Ethical Considerations

- No PII used in features (user_id hashed, payee names only)
- No demographic data used
- Transparent scoring - users can see why transaction was flagged
- Human-in-the-loop for high-risk decisions
- Model cards updated with each retraining

---

*Generated by FinSight Training Pipeline*
"""

    with open(output_path, 'w') as f:
        f.write(md)


if __name__ == "__main__":
    train_all_models()