# AI Pipeline

## Implemented Pipeline

`ECG upload -> preprocessing -> feature extraction -> clinical rules -> explainability -> report`

## Stage Details

1. **Preprocessing** (`services/preprocessing.py`)
   - 50/60 Hz notch filtering
   - Bandpass filtering
   - Baseline correction
   - Smoothing
   - Quality scoring

2. **Feature Extraction** (`services/feature_extraction.py`)
   - R-peak detection
   - RR intervals
   - HR, HRV
   - PR/QRS/QT/QTc estimation when available

3. **Clinical Rules** (`services/rule_engine.py`)
   - Sinus tachycardia
   - Sinus bradycardia
   - Possible atrial fibrillation
   - QT prolongation
   - Bundle branch block (possible)
   - First-degree AV block
   - Fallback normal sinus rhythm

4. **Explainability** (`services/explainability.py`)
   - Natural-language reasoning enhancement
   - Diagnosis confidence calibration
   - Feature importance ranking

5. **ML Placeholder** (`services/ml_placeholder.py`)
   - Reserved for future model integration
   - Currently returns no additional diagnoses
