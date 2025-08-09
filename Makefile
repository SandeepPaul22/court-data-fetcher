.PHONY: install run test docker-build docker-run clean

# Install dependencies
install:
	python -m venv venv
	venv/Scripts/activate && pip install -r requirements.txt

# Run the application
run:
	venv/Scripts/activate && python app.py

# Run tests (when you add them later)
test:
	venv/Scripts/activate && python -m pytest

# Build Docker image
docker-build:
	docker build -t court-data-fetcher .

# Run with Docker
docker-run:
	docker-compose up -d

# Stop Docker
docker-stop:
	docker-compose down

# Clean up
clean:
	rm -rf venv/
	rm -rf __pycache__/
	rm -rf court_scraper/__pycache__/
	rm -f data/*.db
	rm -f logs/*.log

# Development setup
dev-setup: install
	copy .env.example .env
	venv/Scripts/activate && python -c "from court_scraper.database import init_db; init_db()"

# Help
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  run          - Run the application"
	@echo "  test         - Run tests"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker containers"
	@echo "  clean        - Clean up generated files"
	@echo "  dev-setup    - Complete development setup"
