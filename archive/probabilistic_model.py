import numpy as np

def run_quantum_classification(normalized_features, raw_features):
    """
    Executes a quantum-inspired probabilistic classification model.
    Uses amplitude and phase-like calculations to generate probabilities
    for Normal, Tachycardia, and Bradycardia.
    """
    hr = raw_features["heart_rate"]
    
    # Base classical probabilities derived from HR
    if hr < 60:
        p_brady = 0.8 + 0.01 * (60 - hr)
        p_tachy = 0.05
        p_norm = 1.0 - p_brady - p_tachy
    elif hr > 100:
        p_tachy = 0.8 + 0.01 * (hr - 100)
        p_brady = 0.05
        p_norm = 1.0 - p_tachy - p_brady
    else:
        # Distance from optimal 75 BPM
        dist = abs(hr - 75) / 25.0
        p_norm = 0.9 - 0.2 * dist
        if hr > 75:
            p_tachy = 1.0 - p_norm - 0.05
            p_brady = 0.05
        else:
            p_brady = 1.0 - p_norm - 0.05
            p_tachy = 0.05

    # Clip and normalize
    p_norm = max(min(p_norm, 1.0), 0.0)
    p_tachy = max(min(p_tachy, 1.0), 0.0)
    p_brady = max(min(p_brady, 1.0), 0.0)

    total = p_norm + p_tachy + p_brady
    p_norm /= total
    p_tachy /= total
    p_brady /= total

    # Quantum-inspired interference (amplitude mapping)
    # Mapping probabilities to state amplitudes
    amp_norm = np.sqrt(p_norm)
    amp_tachy = np.sqrt(p_tachy)
    amp_brady = np.sqrt(p_brady)

    # Applying a "phase shift" based on normalized QRS and QT intervals
    # to simulate quantum interference effects on final measurements.
    qrs_shift = normalized_features["qrs_duration"]
    qt_shift = normalized_features["qt_interval"]

    # Interference term affects normal vs abnormal states
    interference = 0.05 * np.cos(qrs_shift * np.pi) * np.sin(qt_shift * np.pi)
    
    amp_norm = max(amp_norm + interference, 0.0)
    amp_tachy = max(amp_tachy - interference / 2, 0.0)
    amp_brady = max(amp_brady - interference / 2, 0.0)

    # Convert back to probabilities (Born's rule)
    final_p_norm = amp_norm ** 2
    final_p_tachy = amp_tachy ** 2
    final_p_brady = amp_brady ** 2

    # Final normalization
    final_total = final_p_norm + final_p_tachy + final_p_brady
    probs = {
        "normal": round(final_p_norm / final_total, 4),
        "tachycardia": round(final_p_tachy / final_total, 4),
        "bradycardia": round(final_p_brady / final_total, 4)
    }

    # Determine diagnosis
    diagnosis = max(probs, key=probs.get).capitalize()

    return diagnosis, probs
