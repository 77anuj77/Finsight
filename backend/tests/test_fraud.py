"""
Tests for Fraud Detection Module
"""
import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock, patch

from backend.app.services.fraud_service import FraudService


class TestFraudService:
    """Test Fraud Detection Service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = FraudService()
        self.user_id = "test-user-id"

    def test_normal_transaction_low_score(self):
        """Test that normal transactions get low fraud scores."""
        # Set up user profile with normal spending
        self.service.user_profiles[self.user_id] = {
            "avg_amount": 500.0,
            "std_amount": 100.0,
            "payees": {"Restaurant A", "Uber", "Metro"},
            "categories": {2, 3},
            "recent_txn_count_1hr": 1,
        }

        score = self.service.score_transaction(
            user_id=self.user_id,
            amount=Decimal('450.00'),  # Close to average
            payee="Restaurant A",  # Known payee
            category_id=2,  # Known category
            transacted_at=datetime(2024, 1, 15, 12, 0),  # Normal hour, weekday
        )

        assert score < 0.3  # Should be low risk

    def test_large_amount_deviation(self):
        """Test that large amount deviations increase score."""
        self.service.user_profiles[self.user_id] = {
            "avg_amount": 500.0,
            "std_amount": 100.0,
            "payees": {"Restaurant A"},
            "categories": {2},
            "recent_txn_count_1hr": 1,
        }

        # Amount 3+ standard deviations away
        score = self.service.score_transaction(
            user_id=self.user_id,
            amount=Decimal('5000.00'),  # Way above average
            payee="Restaurant A",
            category_id=2,
            transacted_at=datetime(2024, 1, 15, 12, 0),
        )

        assert score > 0.3  # Should be elevated

    def test_new_payee_increases_score(self):
        """Test that new payee increases fraud score."""
        self.service.user_profiles[self.user_id] = {
            "avg_amount": 500.0,
            "std_amount": 100.0,
            "payees": {"Restaurant A"},  # Known
            "categories": {2},
            "recent_txn_count_1hr": 1,
        }

        score = self.service.score_transaction(
            user_id=self.user_id,
            amount=Decimal('500.00'),
            payee="Unknown Merchant",  # New payee
            category_id=2,
            transacted_at=datetime(2024, 1, 15, 12, 0),
        )

        # Should have some increase from new payee
        assert score > 0.1

    def test_late_night_transaction(self):
        """Test that late night transactions increase score."""
        self.service.user_profiles[self.user_id] = {
            "avg_amount": 500.0,
            "std_amount": 100.0,
            "payees": {"Restaurant A"},
            "categories": {2},
            "recent_txn_count_1hr": 1,
        }

        # 3 AM transaction
        score = self.service.score_transaction(
            user_id=self.user_id,
            amount=Decimal('500.00'),
            payee="Restaurant A",
            category_id=2,
            transacted_at=datetime(2024, 1, 15, 3, 0),  # 3 AM
        )

        # Should have some increase from late night
        assert score > 0.1

    def test_weekend_transaction(self):
        """Test that weekend transactions slightly increase score."""
        self.service.user_profiles[self.user_id] = {
            "avg_amount": 500.0,
            "std_amount": 100.0,
            "payees": {"Restaurant A"},
            "categories": {2},
            "recent_txn_count_1hr": 1,
        }

        # Saturday transaction
        score = self.service.score_transaction(
            user_id=self.user_id,
            amount=Decimal('500.00'),
            payee="Restaurant A",
            category_id=2,
            transacted_at=datetime(2024, 1, 13, 12, 0),  # Saturday
        )

        # Should have small increase from weekend
        assert score >= 0.05

    def test_high_velocity(self):
        """Test that high transaction velocity increases score."""
        self.service.user_profiles[self.user_id] = {
            "avg_amount": 500.0,
            "std_amount": 100.0,
            "payees": {"Restaurant A"},
            "categories": {2},
            "recent_txn_count_1hr": 10,  # High velocity
        }

        score = self.service.score_transaction(
            user_id=self.user_id,
            amount=Decimal('500.00'),
            payee="Restaurant A",
            category_id=2,
            transacted_at=datetime(2024, 1, 15, 12, 0),
        )

        # Should have increase from velocity
        assert score > 0.15

    def test_combined_anomalies(self):
        """Test that multiple anomalies combine for high score."""
        self.service.user_profiles[self.user_id] = {
            "avg_amount": 500.0,
            "std_amount": 100.0,
            "payees": {"Restaurant A"},
            "categories": {2},
            "recent_txn_count_1hr": 1,
        }

        # Multiple red flags: large amount + new payee + late night + weekend
        score = self.service.score_transaction(
            user_id=self.user_id,
            amount=Decimal('5000.00'),  # Large
            payee="Unknown Merchant",  # New payee
            category_id=5,  # New category
            transacted_at=datetime(2024, 1, 13, 3, 0),  # Saturday 3 AM
        )

        # Should be high risk
        assert score > 0.5

    def test_score_bounds(self):
        """Test that score is always between 0 and 1."""
        self.service.user_profiles[self.user_id] = {
            "avg_amount": 500.0,
            "std_amount": 100.0,
            "payees": set(),
            "categories": set(),
            "recent_txn_count_1hr": 0,
        }

        # Extreme case
        score = self.service.score_transaction(
            user_id=self.user_id,
            amount=Decimal('100000.00'),
            payee="Unknown",
            category_id=99,
            transacted_at=datetime(2024, 1, 13, 3, 0),
        )

        assert 0.0 <= score <= 1.0

    def test_empty_profile_defaults(self):
        """Test scoring with empty user profile."""
        # No profile set up
        score = self.service.score_transaction(
            user_id="new-user",
            amount=Decimal('1000.00'),
            payee="New Payee",
            category_id=2,
            transacted_at=datetime(2024, 1, 15, 12, 0),
        )

        # Should handle gracefully
        assert 0.0 <= score <= 1.0

    def test_update_user_profile(self):
        """Test updating user profile from transactions."""
        transactions = [
            {"amount": 500, "payee": "A", "category_id": 2},
            {"amount": 600, "payee": "B", "category_id": 3},
            {"amount": 400, "payee": "A", "category_id": 2},
        ]

        self.service.update_user_profile("user1", transactions)

        profile = self.service.user_profiles["user1"]
        assert profile["avg_amount"] == 500.0
        assert profile["std_amount"] > 0
        assert "A" in profile["payees"]
        assert "B" in profile["payees"]
        assert 2 in profile["categories"]
        assert 3 in profile["categories"]

    def test_train_model_requires_sklearn(self):
        """Test that training requires scikit-learn."""
        # This test just verifies the method exists and handles missing sklearn
        result = self.service.train_model([])
        # Should not crash, may return False if sklearn not available
        assert result is None or result is False


class TestFraudServiceIntegration:
    """Integration tests with TransactionService."""

    def test_fraud_flag_on_suspicious_transaction(self, db_session, test_user, test_account, test_categories):
        """Test that suspicious transactions get flagged."""
        from backend.app.services.transaction_service import TransactionService

        service = TransactionService(db_session)

        # Create a transaction that will trigger fraud detection
        # (large amount, new payee, late night)
        txn_data = {
            "account_id": test_account.id,
            "category_id": 2,
            "type": "EXPENSE",
            "amount": Decimal('5000.00'),  # Very large
            "payee": "Suspicious Merchant",
            "transacted_at": datetime(2024, 1, 13, 3, 0),  # Saturday 3 AM
        }

        # This should either flag or create transaction depending on balance
        # We're mainly testing it doesn't crash
        try:
            txn = service.create_transaction(txn_data, test_user.id)
            # If it succeeds, check flag status
            assert txn.flag_status in ("NORMAL", "SUSPICIOUS", "REVIEW")
        except ValueError:
            # Expected if insufficient balance
            pass