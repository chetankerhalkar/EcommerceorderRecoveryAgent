#!/bin/bash
set -e

# Backend deps
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Frontend deps
cd frontend
npm install
