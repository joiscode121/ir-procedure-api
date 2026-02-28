#!/usr/bin/env bash
set -e
pip install --upgrade pip
pip install -r requirements.txt
python3 -c "from app.models.database import init_db; init_db(); print('DB initialized')"
python3 data/seed.py
