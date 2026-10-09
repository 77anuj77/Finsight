#!/usr/bin/env python3
"""
FinSight Seed Script
Loads synthetic data into PostgreSQL and MongoDB.
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.ml.synthetic_data import main

if __name__ == "__main__":
    print("Starting FinSight data seeding...")
    main()
    print("Seeding complete!")