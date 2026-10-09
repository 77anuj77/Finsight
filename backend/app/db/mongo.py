"""
MongoDB Connection for FinSight
Uses pymongo (sync) for simplicity; can be swapped for motor (async) if needed.
"""
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional

from backend.app.config import settings


class MongoDB:
    """MongoDB client wrapper with collection references."""

    client: Optional[MongoClient] = None
    db: Optional[Database] = None

    # Collections
    txn_analytics: Optional[Collection] = None
    user_behaviour: Optional[Collection] = None
    ai_insights: Optional[Collection] = None
    notifications: Optional[Collection] = None


mongo = MongoDB()


def init_mongo() -> None:
    """Initialize MongoDB connection and collections."""
    mongo.client = MongoClient(settings.MONGO_URI)
    mongo.db = mongo.client[settings.MONGO_DB]

    # Collection references
    mongo.txn_analytics = mongo.db["txn_analytics"]
    mongo.user_behaviour = mongo.db["user_behaviour"]
    mongo.ai_insights = mongo.db["ai_insights"]
    mongo.notifications = mongo.db["notifications"]

    # Create indexes
    _create_indexes()


def _create_indexes() -> None:
    """Create necessary indexes for performance."""
    # txn_analytics indexes
    mongo.txn_analytics.create_index([("user_id", 1), ("transacted_at", -1)])
    mongo.txn_analytics.create_index([("month_key", 1)])
    mongo.txn_analytics.create_index([("category", 1)])
    mongo.txn_analytics.create_index([("tx_id", 1)], unique=True)

    # user_behaviour indexes
    mongo.user_behaviour.create_index([("user_id", 1), ("month_key", 1)], unique=True)

    # ai_insights indexes
    mongo.ai_insights.create_index([("user_id", 1), ("month_key", 1)], unique=True)

    # notifications indexes
    mongo.notifications.create_index([("user_id", 1), ("is_read", 1), ("created_at", -1)])


def close_mongo() -> None:
    """Close MongoDB connection."""
    if mongo.client:
        mongo.client.close()
        mongo.client = None
        mongo.db = None


def get_mongo_db() -> Optional[Database]:
    """Get MongoDB database instance, initializing if needed."""
    if mongo.db is None:
        try:
            init_mongo()
        except Exception:
            return None
    return mongo.db