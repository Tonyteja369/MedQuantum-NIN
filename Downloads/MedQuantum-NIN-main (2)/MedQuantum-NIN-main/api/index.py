from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
import io
from typing import Dict, Any

# Import our services
from app.services.quantum_engine import QuantumProcessor
from app.services.nin_engine import NINEngine

app = FastAPI(
    title="MedQuantum-NIN API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "MedQuantum-NIN ECG Analysis API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/analyze")
async def analyze_ecg(file: UploadFile = File(...)):
    """Analyze uploaded ECG file"""
    try:
        # Read uploaded file
        contents = await file.read()
        
        # Parse CSV
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
            
            # Extract ECG signal from first non-time column
            signal_columns = [col for col in df.columns if col.lower() != 'time']
            if not signal_columns:
                raise HTTPException(status_code=400, detail="No ECG signal columns found")
            
            # Use first available ECG lead
            ecg_column = signal_columns[0]
            signal = df[ecg_column].values
            sampling_rate = 500  # Default sampling rate
            
            # Process with real ECG analysis
            quantum_result = QuantumProcessor.process(signal, sampling_rate)
            analysis_result = await NINEngine().analyze(quantum_result)
            
            return {
                "success": True,
                "analysis": {
                    "heart_rate": analysis_result.features.get("heart_rate", 0),
                    "diagnoses": [
                        {
                            "condition": d.condition,
                            "confidence": d.confidence,
                            "severity": d.severity,
                            "reasoning": [
                                {"step": r.step_number, "description": r.description}
                                for r in (d.reasoning_trace or [])
                            ]
                        }
                        for d in analysis_result.diagnoses
                    ],
                    "signal_quality": {
                        "samples_analyzed": len(signal),
                        "duration_seconds": len(signal) / sampling_rate
                    }
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Only CSV files supported")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Vercel automatically exports this ASGI app for serverless execution
__all__ = ["app"]
