# SAM RAG API Load Testing

This repository contains Locust load testing scripts for the SAM RAG API.

## Project Structure

```
├── config.py            # Configuration settings
├── locust.py           # Main Locust file
└── tasks/              # Task modules
    ├── instance_tasks.py  # Instance management tasks
    ├── file_tasks.py     # File operations tasks
    └── query_tasks.py    # Query and job tasks
```

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
```

2. Install dependencies:
```bash
pip install locust
```

## Running the Tests

1. Start Locust:
```bash
locust -f locust.py --host https://api-rag.dev.stagwellmarketingcloud.io
```

2. Open http://localhost:8089 in your browser

3. Configure test parameters:
   - Number of users
   - Spawn rate (users per second)
   - Host (if not specified in command line)

## Configuration

Edit `config.py` to modify:
- API host
- Test parameters
- File upload settings
- User IDs
