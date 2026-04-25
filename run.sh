#!/usr/bin/env bash
set -e
echo "Starting MedQuantum-NIN Backend..."
uvicorn main:app --reload &
sleep 2
echo "Starting Streamlit Frontend..."
streamlit run app.py
