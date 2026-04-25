def generate_explanation(diagnosis, features):
    """
    Generates explainable outputs for the diagnosis based on the clinical features.
    """
    hr = features.get("heart_rate")
    rr = features.get("rr_interval")
    
    explanation = f"The model diagnosed the ECG as {diagnosis}. "
    
    if diagnosis == "Normal":
        explanation += f"This is supported by a resting heart rate of {hr} BPM, which falls within the normal range of 60-100 BPM. "
        explanation += f"The RR interval is stable at {rr} seconds."
    elif diagnosis == "Tachycardia":
        explanation += f"This is primarily driven by an elevated heart rate of {hr} BPM, which exceeds the normal threshold of 100 BPM. "
        explanation += f"The corresponding RR interval is shortened to {rr} seconds."
    elif diagnosis == "Bradycardia":
        explanation += f"This is primarily driven by a depressed heart rate of {hr} BPM, which is below the normal threshold of 60 BPM. "
        explanation += f"The corresponding RR interval is prolonged to {rr} seconds."
        
    return explanation

def generate_patient_message(diagnosis):
    """
    Generates a patient-friendly interpretation.
    """
    if diagnosis == "Normal":
        return "Your heart rhythm looks normal! Keep up your healthy habits."
    elif diagnosis == "Tachycardia":
        return "Your heart rate is faster than usual. While this can happen due to exercise or stress, you should consult with your doctor if you feel unwell."
    elif diagnosis == "Bradycardia":
        return "Your heart rate is slower than usual. This is often normal for athletes, but if you feel dizzy or tired, please reach out to your doctor."
    return "Your ECG results are ready for review with your doctor."
