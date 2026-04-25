import datetime

def generate_soap_note(features, diagnosis, explanation):
    """
    Generates a structured SOAP (Subjective, Objective, Assessment, Plan) report.
    """
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    soap = f"""SOAP Note - Date: {date_str}

**SUBJECTIVE:**
Patient presents for ECG analysis. No acute distress reported at the time of data capture.

**OBJECTIVE:**
ECG findings:
- Heart Rate: {features.get('heart_rate')} BPM
- RR Interval: {features.get('rr_interval')} s
- PR Interval: {features.get('pr_interval')} s
- QRS Duration: {features.get('qrs_duration')} s
- QT Interval: {features.get('qt_interval')} s

**ASSESSMENT:**
Diagnosis: {diagnosis}
Details: {explanation}

**PLAN:**
"""
    if diagnosis == "Normal":
        soap += "Routine follow-up. No immediate clinical intervention required based on ECG."
    elif diagnosis == "Tachycardia":
        soap += "Recommend clinical correlation for tachycardia. Consider holter monitor or echocardiogram if symptomatic."
    elif diagnosis == "Bradycardia":
        soap += "Recommend clinical correlation for bradycardia. Evaluate medication list and patient symptoms (dizziness, fatigue)."
        
    return soap
