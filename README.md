# MedQuantum-NIN 🫀

## Description
MedQuantum-NIN is an advanced offline ECG intelligent analysis system. It features robust PQRST waveform detection, a quantum-inspired probabilistic diagnostic model, and automated SOAP (Subjective, Objective, Assessment, Plan) report generation. The project comes complete with a FastAPI backend for core signal processing and a Streamlit dashboard for a professional, demo-ready visualization interface.

## Features
* **ECG Signal Processing:** Handles both CSV and NumPy `.npy` formats, utilizing custom IIR notch and Butterworth filters.
* **PQRST Visualization:** Accurately delineates and visually overlays P, Q, R, S, T peaks onto the ECG waveform.
* **Probabilistic Diagnosis:** Evaluates features against normative values to predict Normal, Tachycardia, or Bradycardia with confidence scores.
* **Streamlit UI Dashboard:** A rich, interactive interface that dynamically charts metrics, probabilities, and findings.
* **FastAPI Backend:** A lightweight, highly concurrent, JSON-native API that coordinates the signal processing pipeline.
* **Explainability & Reporting:** Natural language rationale generation along with downloadable clinical SOAP notes.

## Project Structure
```text
medquantum-nin/
├── main.py                    # Main FastAPI application
├── app.py                     # Streamlit frontend dashboard
├── requirements.txt           # Project dependencies
├── README.md                  # This documentation
├── .gitignore                 # Git ignore file
├── src/                       # Core logic modules
│   ├── preprocessing.py
│   ├── pqrst_detection.py
│   ├── feature_engineering.py
│   ├── probabilistic_model.py
│   ├── explainability.py
│   └── soap_generator.py
├── data/                      # Local dataset storage (ignored in git)
└── output/                    # Local output storage (ignored in git)
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Backend
Start the FastAPI REST server:
```bash
uvicorn main:app --reload
```
You can view the interactive API documentation at: `http://localhost:8000/docs`

### 3. Run Frontend
Start the Streamlit Web UI:
```bash
streamlit run app.py
```
Open the dashboard in your browser at: `http://localhost:8501`

## Demo
Launch the app to see an interactive visualization of the sample ECG signal, complete with color-coded probability charts, clinical feature extraction cards, and a fully downloadable SOAP report. Simply choose "Select Sample Dataset" from the sidebar and click **Run Analysis**.
