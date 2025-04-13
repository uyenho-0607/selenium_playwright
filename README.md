# Selenium and Playwright Testing Project

This repository contains automated test suites using both Selenium and Playwright frameworks.

## Project Structure
```
selenium_playwright/
├── selenium_tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── tests/
├── playwright_tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── tests/
├── requirements.txt
└── README.md
```

## Setup Instructions

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

### Selenium Tests
```bash
pytest selenium_tests/
```

### Playwright Tests
```bash
pytest playwright_tests/
```

## Dependencies
- Python 3.8+
- Selenium
- Playwright
- pytest
- pytest-playwright