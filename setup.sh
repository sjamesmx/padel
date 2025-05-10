#!/bin/bash
cd ~/pdzr/backend
source venv/bin/activate
export PATH="/Users/jaime/pdzr/backend/venv/bin:$PATH"
export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"
unset GOOGLE_APPLICATION_CREDENTIALS
export FIRESTORE_EMULATOR_HOST=localhost:8080
pip install -r requirements.txt
killall java
firebase emulators:start --only firestore &
sleep 5
pytest tests/ -v --cov=app --cov-report=html 