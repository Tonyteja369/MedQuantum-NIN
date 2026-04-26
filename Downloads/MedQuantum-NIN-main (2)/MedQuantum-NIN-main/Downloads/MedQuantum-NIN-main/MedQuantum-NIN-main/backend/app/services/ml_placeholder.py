import time
import random
from typing import Dict, Any, List
from loguru import logger

from app.models.schemas import DiagnosisResult, ReasoningStep


class MLModelPlaceholder:
    """Placeholder ML model for ECG analysis."""
    
    def __init__(self):
        self.model_name = "ECG-Analysis-Placeholder-v1.0"
        self.is_loaded = True
        
    def predict(self, signal_id: str, features) -> List[DiagnosisResult]:
        """Generate placeholder predictions based on ECG features."""
        time.sleep(0.1)  # Simulate processing time
        
        # Handle ECGFeatures object
        heart_rate = getattr(features, 'heart_rate', 72)
        
        diagnoses = []
        if 60 <= heart_rate <= 100:
            diagnoses.append(DiagnosisResult(
                id=f"ml-{signal_id}-1",
                condition='Normal Sinus Rhythm',
                confidence=0.92,
                severity='normal',
                supporting_features=['heart_rate', 'rr_intervals'],
                reasoning=[
                    ReasoningStep(
                        step=1,
                        description='Heart rate analysis',
                        feature_used='heart_rate',
                        value=heart_rate,
                        threshold='60-100 bpm',
                        conclusion='Heart rate is within normal range'
                    )
                ],
                recommendations=['Routine follow-up']
            ))
        elif heart_rate > 100:
            diagnoses.append(DiagnosisResult(
                id=f"ml-{signal_id}-1",
                condition='Sinus Tachycardia',
                confidence=0.85,
                severity='warning',
                supporting_features=['heart_rate', 'rr_intervals'],
                reasoning=[
                    ReasoningStep(
                        step=1,
                        description='Heart rate analysis',
                        feature_used='heart_rate',
                        value=heart_rate,
                        threshold='>100 bpm',
                        conclusion='Heart rate is elevated'
                    )
                ],
                recommendations=['Monitor heart rate', 'Consider evaluation']
            ))
        elif heart_rate < 60:
            diagnoses.append(DiagnosisResult(
                id=f"ml-{signal_id}-1",
                condition='Sinus Bradycardia',
                confidence=0.88,
                severity='warning',
                supporting_features=['heart_rate', 'rr_intervals'],
                reasoning=[
                    ReasoningStep(
                        step=1,
                        description='Heart rate analysis',
                        feature_used='heart_rate',
                        value=heart_rate,
                        threshold='<60 bpm',
                        conclusion='Heart rate is low'
                    )
                ],
                recommendations=['Monitor heart rate', 'Consider evaluation']
            ))
        
        # Add some random variations for testing
        if random.random() < 0.1:
            diagnoses.append(DiagnosisResult(
                id=f"ml-{signal_id}-2",
                condition='Possible Atrial Fibrillation',
                confidence=0.65,
                severity='moderate',
                supporting_features=['rr_intervals', 'hr_variability'],
                reasoning=[
                    ReasoningStep(
                        step=1,
                        description='Heart rate variability analysis',
                        feature_used='hr_variability',
                        value=getattr(features, 'hr_variability', 0),
                        threshold='irregular',
                        conclusion='Irregular rhythm detected'
                    )
                ],
                recommendations=['Further cardiac evaluation recommended']
            ))
        
        return diagnoses
    
    def _calculate_risk(self, diagnoses) -> str:
        """Calculate overall risk level from diagnoses."""
        if not diagnoses:
            return 'normal'
        
        max_severity = max(d.get('severity', 'normal') for d in diagnoses)
        severity_map = {
            'normal': 'normal',
            'warning': 'low-risk',
            'moderate': 'moderate',
            'critical': 'high-risk'
        }
        return severity_map.get(max_severity, 'normal')
    
    def is_healthy(self) -> bool:
        """Check if model is ready for predictions."""
        return self.is_loaded
