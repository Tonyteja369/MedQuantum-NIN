"""NIN Engine - Neuro-Intelligent Network for ECG Analysis"""

from __future__ import annotations

import time
import math
from typing import Optional

from loguru import logger

from ..models.schemas import QuantumResult, Diagnosis, NINResult
from .rule_engine import run_rule_engine
from .explainability import apply_explainability


class RuleReasoner:
    """NIN Pass 1: Evaluate clinical rules against QuantumResult."""
    
    def run(
        self,
        quantum_result: QuantumResult,
        sex: Optional[str] = None,
    ) -> list[Diagnosis]:
        """Run rule-based reasoning engine."""
        return run_rule_engine(quantum_result, sex=sex)


class ConfidenceCalibrator:
    """NIN Pass 2: Assign per-diagnosis confidence using sigmoid scaling."""
    
    def run(self, diagnoses: list[Diagnosis]) -> list[Diagnosis]:
        """Calibrate confidence scores for each diagnosis."""
        try:
            logger.info(f"Confidence calibration: {len(diagnoses)} diagnoses")
            
            calibrated = []
            for diagnosis in diagnoses:
                # Apply sigmoid scaling to confidence
                final_confidence = self._sigmoid_scale(diagnosis.confidence)
                
                diagnosis.confidence = final_confidence
                calibrated.append(diagnosis)
            
            logger.info(f"Calibration complete: {len(calibrated)} diagnoses processed")
            return calibrated
            
        except Exception as e:
            logger.error(f"Confidence calibration failed: {str(e)}")
            return diagnoses
    
    @staticmethod
    def _sigmoid_scale(confidence: float) -> float:
        """Apply sigmoid scaling to raw confidence score."""
        try:
            # Clip to reasonable range
            score = max(0.0, min(1.0, confidence))
            
            # Sigmoid scaling: steeper curve near 0.5
            if score < 0.5:
                return 0.5 * math.tanh(2 * (score - 0.5)) + 0.5
            else:
                return 0.5 * math.tanh(2 * (score - 0.5)) + 0.5
        except Exception:
            return confidence


class ExplainabilityBuilder:
    """NIN Pass 3: Build reasoning traces for diagnosis explanations."""
    
    def run(self, diagnoses: list[Diagnosis]) -> list[Diagnosis]:
        """Build explainability traces for diagnoses."""
        try:
            logger.info(f"Building explainability traces for {len(diagnoses)} diagnoses")
            
            explained = []
            for diagnosis in diagnoses:
                explained_diagnosis = apply_explainability(diagnosis)
                explained.append(explained_diagnosis)
            
            logger.info(f"Explainability complete: {len(explained)} diagnoses with reasoning")
            return explained
            
        except Exception as e:
            logger.error(f"Explainability building failed: {str(e)}")
            return diagnoses


class NINEngine:
    """Neuro-Intelligent Network: 3-pass ECG analysis."""
    
    def __init__(self):
        """Initialize NIN engine components."""
        self.rule_reasoner = RuleReasoner()
        self.confidence_calibrator = ConfidenceCalibrator()
        self.explainability_builder = ExplainabilityBuilder()
        logger.info("NIN Engine initialized with 3-pass pipeline")
    
    async def analyze(
        self,
        quantum_result: QuantumResult,
        sex: Optional[str] = None,
    ) -> NINResult:
        """Execute full NIN pipeline on quantum result."""
        try:
            start_time = time.time()
            logger.info("Starting NIN 3-pass analysis pipeline")
            
            # Pass 1: Rule Reasoning
            logger.info("NIN Pass 1: Rule Reasoning")
            diagnoses = self.rule_reasoner.run(quantum_result, sex=sex)
            logger.info(f"  → Generated {len(diagnoses)} diagnoses")
            
            # Pass 2: Confidence Calibration
            logger.info("NIN Pass 2: Confidence Calibration")
            diagnoses = self.confidence_calibrator.run(diagnoses)
            logger.info(f"  → Calibrated {len(diagnoses)} confidence scores")
            
            # Pass 3: Explainability  
            logger.info("NIN Pass 3: Explainability")
            diagnoses = self.explainability_builder.run(diagnoses)
            logger.info(f"  → Generated reasoning traces for {len(diagnoses)} diagnoses")
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            result = NINResult(
                diagnoses=diagnoses,
                primary_diagnosis=diagnoses[0] if diagnoses else None,
                analysis_time_ms=elapsed_ms,
                pipeline_stages_completed=["rule_reasoning", "confidence_calibration", "explainability"],
            )
            
            logger.info(f"NIN analysis complete in {elapsed_ms:.0f}ms")
            return result
            
        except Exception as e:
            logger.error(f"NIN analysis failed: {str(e)}")
            raise


# Module-level convenience function
async def run_nin_analysis(
    quantum_result: QuantumResult,
    sex: Optional[str] = None,
) -> NINResult:
    """Run NIN engine on quantum result."""
    engine = NINEngine()
    return await engine.analyze(quantum_result, sex=sex)
fatal: path 'backend/app/services/nin_engine.py' does not exist in 'origin/copilot/build-medquantum-nin-application'
