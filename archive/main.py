from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
import os
import io
import math
import numpy as np

from src.preprocessing import load_ecg_file, preprocess_ecg
from src.pqrst_detection import detect_pqrst
from src.feature_engineering import extract_features, normalize_features
from src.probabilistic_model import run_quantum_classification
from src.explainability import generate_explanation, generate_patient_message
from src.soap_generator import generate_soap_note

app = FastAPI(title="MedQuantum-NIN ECG Analysis Server")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.get("/")
def read_root():
    return {"status": "MedQuantum-NIN server running"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "MedQuantum-NIN", "version": "1.0.0"}

@app.get("/samples")
def list_samples():
    """List available ECG sample files from /data/."""
    try:
        files = os.listdir(DATA_DIR)
        return {"samples": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_ecg(file: UploadFile = File(...)):
    """
    Accepts an ECG file (CSV or NumPy), processes it, and returns the analysis.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    is_csv = file.filename.endswith(".csv")
    is_npy = file.filename.endswith(".npy")
    
    if not (is_csv or is_npy):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload .csv or .npy")
    
    try:
        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty signal file.")
        
        # 1. Load ECG signal
        file_bytes = io.BytesIO(content)
        ecg_signal = load_ecg_file(file_bytes, is_csv=is_csv)
        
        if len(ecg_signal) == 0:
             raise HTTPException(status_code=400, detail="Empty signal parsed.")
             
        # 2. Preprocess signal
        ecg_cleaned = preprocess_ecg(ecg_signal, sampling_rate=500)
        
        # 3. Detect PQRST features
        pqrst_info = detect_pqrst(ecg_cleaned, sampling_rate=500)
        
        # 4. Extract features
        features = extract_features(pqrst_info, sampling_rate=500)
        
        # 5. Normalize features
        normalized_features = normalize_features(features)
        
        # 6 & 7. Run probabilistic model & determine diagnosis
        diagnosis, probabilities = run_quantum_classification(normalized_features, features)
        
        # 8. Generate explanation
        explanation = generate_explanation(diagnosis, features)
        
        # 9. Generate patient-friendly output
        patient_message = generate_patient_message(diagnosis)
        
        # 10. Generate SOAP note
        soap_note = generate_soap_note(features, diagnosis, explanation)
        
        # Extract peaks, ignoring NaNs
        def clean_peaks(peaks):
            if peaks is None: return []
            return [int(x) for x in peaks if not math.isnan(x)]

        return {
            "signal": ecg_cleaned.tolist() if isinstance(ecg_cleaned, np.ndarray) else list(ecg_cleaned),
            "time": [i / 500.0 for i in range(len(ecg_cleaned))],
            "r_peaks": clean_peaks(pqrst_info.get("ECG_R_Peaks", [])),
            "p_peaks": clean_peaks(pqrst_info.get("ECG_P_Peaks", [])),
            "q_peaks": clean_peaks(pqrst_info.get("ECG_Q_Peaks", [])),
            "s_peaks": clean_peaks(pqrst_info.get("ECG_S_Peaks", [])),
            "t_peaks": clean_peaks(pqrst_info.get("ECG_T_Peaks", [])),
            "heart_rate": features.get("heart_rate"),
            "features": {
                "rr_interval": features.get("rr_interval"),
                "pr_interval": features.get("pr_interval"),
                "qrs_duration": features.get("qrs_duration"),
                "qt_interval": features.get("qt_interval")
            },
            "diagnosis": diagnosis,
            "probabilities": probabilities,
            "explanation": explanation,
            "patient_message": patient_message,
            "soap_note": soap_note
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failure: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
