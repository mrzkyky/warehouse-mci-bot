# Makefile for Warehouse Bot

.PHONY: help install dev test clean docker-build docker-up docker-down lint format

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Run in development mode"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean temporary files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start with Docker Compose"
	@echo "  make docker-down  - Stop Docker Compose"
	@echo "  make lint         - Run linter"
	@echo "  make format       - Format code"
	@echo "  make stats        - Show database stats"
	@echo "  make report       - Generate today's report"

install:
	pip install -r requirements.txt

dev:
	python bot.py

test:
	python test_parser.py

stats:
	python admin.py stats

report:
	python admin.py report

clean:
	rm -rf __pycache__
	rm -rf *.pyc
	rm -rf temp/*
	rm -rf .pytest_cache
	rm -rf .mypy_cache

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f bot

lint:
	flake8 . --max-line-length=120 --exclude=venv,__pycache__

format:
	black . --line-length=120 --exclude=venv

check: lint test
