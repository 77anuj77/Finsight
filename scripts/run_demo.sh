#!/bin/bash
# FinSight Demo Runner
# Starts all services and runs the demo

set -e

echo "=" * 60
echo "FinSight Demo Runner"
echo "=" * 60

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose not found. Please install Docker Compose."
    exit 1
fi

# Start services
echo "Starting services..."
docker-compose up -d postgres mongodb redis

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Check postgres
echo "Checking PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U finsight_user -d finsight > /dev/null 2>&1; do
    echo "  Waiting for PostgreSQL..."
    sleep 2
done
echo "  PostgreSQL ready!"

# Check mongodb
echo "Checking MongoDB..."
until docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    echo "  Waiting for MongoDB..."
    sleep 2
done
echo "  MongoDB ready!"

# Initialize database (run migrations)
echo "Initializing database..."
docker-compose exec -T backend python -c "
from backend.app.db.postgres import init_db
init_db()
print('Database initialized')
"

# Seed data
echo "Seeding synthetic data..."
docker-compose exec -T backend python scripts/seed.py

# Run tests
echo "Running tests..."
docker-compose exec -T backend pytest backend/tests/ -v --tb=short || true

# Start backend
echo "Starting backend..."
docker-compose up -d backend

# Wait for backend
sleep 5

# Test API
echo "Testing API..."
curl -s http://localhost:8000/health | jq . || echo "Health check failed"

# Start frontend
echo "Starting frontend..."
docker-compose up -d frontend

echo ""
echo "=" * 60
echo "Demo is running!"
echo "=" * 60
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f"