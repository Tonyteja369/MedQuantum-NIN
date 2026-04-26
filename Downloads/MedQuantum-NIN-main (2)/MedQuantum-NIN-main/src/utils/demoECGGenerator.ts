/**
 * High-Fidelity ECG Demo Generator
 * 
 * Generates clinically accurate ECG waveforms with consistent parameters
 * Waveform ↔ Parameters ↔ Diagnosis must match
 */

import type { AnalysisResult, SignalQuality } from '@/types/ecg.types';

interface DemoCase {
  id: string;
  name: string;
  description: string;
  heartRate: number;
  samplingRate: number;
  duration: number;
  signal: number[];
  quality: SignalQuality;
  analysis: AnalysisResult;
}

/**
 * Generate realistic ECG waveform using P-QRS-T components
 */
function generateECGWaveform(
  heartRate: number,
  samplingRate: number,
  duration: number,
  noiseLevel: number = 0.02,
  irregularity: number = 0
): number[] {
  const samples = samplingRate * duration;
  const signal: number[] = new Array(samples).fill(0);
  
  // RR interval in samples based on heart rate
  const rrInterval = (60 / heartRate) * samplingRate;
  
  // Generate beats
  let currentSample = 0;
  while (currentSample < samples - 200) {
    // Add irregularity for arrhythmia
    const actualRR = rrInterval + (irregularity > 0 ? (Math.random() - 0.5) * irregularity * rrInterval : 0);
    
    const beatStart = currentSample;
    const beatEnd = Math.min(beatStart + actualRR, samples);
    
    // P-wave (small positive deflection before QRS)
    const pStart = beatStart + actualRR * 0.1;
    const pPeak = pStart + actualRR * 0.05;
    const pEnd = pStart + actualRR * 0.1;
    
    for (let i = Math.floor(pStart); i < Math.min(Math.floor(pEnd), samples); i++) {
      const progress = (i - pStart) / (pEnd - pStart);
      signal[i] += 0.15 * Math.sin(progress * Math.PI);
    }
    
    // QRS complex (sharp spike)
    const qStart = beatStart + actualRR * 0.2;
    const qPeak = qStart + actualRR * 0.02;
    const rPeak = qStart + actualRR * 0.05;
    const sPeak = qStart + actualRR * 0.08;
    const qrsEnd = beatStart + actualRR * 0.12;
    
    for (let i = Math.floor(qStart); i < Math.min(Math.floor(qrsEnd), samples); i++) {
      if (i < rPeak) {
        // Q and R
        signal[i] -= 0.1; // Q
        if (i >= rPeak - actualRR * 0.02) {
          signal[i] += 1.2; // R
        }
      } else {
        // S
        signal[i] -= 0.2; // S
      }
    }
    
    // ST segment (flat)
    const stStart = qrsEnd;
    const stEnd = beatStart + actualRR * 0.2;
    
    // T-wave (broader positive deflection)
    const tStart = stEnd;
    const tPeak = tStart + actualRR * 0.08;
    const tEnd = beatStart + actualRR * 0.4;
    
    for (let i = Math.floor(tStart); i < Math.min(Math.floor(tEnd), samples); i++) {
      const progress = (i - tStart) / (tEnd - tStart);
      signal[i] += 0.25 * Math.sin(progress * Math.PI);
    }
    
    currentSample = beatEnd;
  }
  
  // Add baseline drift
  for (let i = 0; i < samples; i++) {
    signal[i] += 0.05 * Math.sin(2 * Math.PI * i / (samplingRate * 2));
  }
  
  // Add noise
  for (let i = 0; i < samples; i++) {
    signal[i] += (Math.random() - 0.5) * noiseLevel;
  }
  
  return signal;
}

/**
 * Generate PVC (Premature Ventricular Contraction) waveform
 */
function generatePVCWaveform(
  heartRate: number,
  samplingRate: number,
  duration: number
): number[] {
  const samples = samplingRate * duration;
  const signal: number[] = new Array(samples).fill(0);
  
  const rrInterval = (60 / heartRate) * samplingRate;
  let currentSample = 0;
  let beatCount = 0;
  
  while (currentSample < samples - 200) {
    const beatStart = currentSample;
    const isPVC = beatCount > 0 && beatCount % 4 === 0; // Every 4th beat is PVC
    
    const actualRR = isPVC ? rrInterval * 0.6 : rrInterval; // PVC comes early
    
    if (isPVC) {
      // PVC: Wide QRS, no P-wave, large amplitude
      const qrsStart = beatStart;
      const qrsEnd = beatStart + actualRR * 0.2; // Wider QRS
      
      for (let i = Math.floor(qrsStart); i < Math.min(Math.floor(qrsEnd), samples); i++) {
        const progress = (i - qrsStart) / (qrsEnd - qrsStart);
        signal[i] += 1.5 * Math.sin(progress * Math.PI); // Large amplitude
      }
    } else {
      // Normal beat
      const pStart = beatStart + actualRR * 0.1;
      const pEnd = beatStart + actualRR * 0.15;
      for (let i = Math.floor(pStart); i < Math.min(Math.floor(pEnd), samples); i++) {
        signal[i] += 0.15 * Math.sin(((i - pStart) / (pEnd - pStart)) * Math.PI);
      }
      
      const qrsStart = beatStart + actualRR * 0.2;
      const qrsEnd = beatStart + actualRR * 0.3;
      for (let i = Math.floor(qrsStart); i < Math.min(Math.floor(qrsEnd), samples); i++) {
        if (i < qrsStart + actualRR * 0.05) {
          signal[i] += 1.2;
        } else {
          signal[i] -= 0.2;
        }
      }
      
      const tStart = beatStart + actualRR * 0.4;
      const tEnd = beatStart + actualRR * 0.6;
      for (let i = Math.floor(tStart); i < Math.min(Math.floor(tEnd), samples); i++) {
        signal[i] += 0.25 * Math.sin(((i - tStart) / (tEnd - tStart)) * Math.PI);
      }
    }
    
    currentSample = beatStart + actualRR;
    beatCount++;
  }
  
  // Add noise
  for (let i = 0; i < samples; i++) {
    signal[i] += (Math.random() - 0.5) * 0.03;
  }
  
  return signal;
}

/**
 * Demo Case 1: Normal Sinus Rhythm
 */
export function createNormalSinusRhythm(): DemoCase {
  const heartRate = 72;
  const samplingRate = 500;
  const duration = 10;
  
  const signal = generateECGWaveform(heartRate, samplingRate, duration, 0.02, 0);
  
  const quality: SignalQuality = {
    overall: 92,
    noiseLevel: 28,
    baselineWander: false,
    artifactRatio: 0.03,
    leadQualities: { II: 0.95, V1: 0.88, V5: 0.91 },
  };
  
  const analysis: AnalysisResult = {
    id: `demo-normal-${Date.now()}`,
    timestamp: new Date().toISOString(),
    processingTimeMs: 1234,
    signals: [
      { lead: 'II', data: signal, samplingRate, duration, units: 'mV' },
      { lead: 'V1', data: generateECGWaveform(heartRate, samplingRate, duration, 0.025, 0), samplingRate, duration, units: 'mV' },
      { lead: 'V5', data: generateECGWaveform(heartRate, samplingRate, duration, 0.022, 0), samplingRate, duration, units: 'mV' },
    ],
    quality,
    metrics: {
      heartRate,
      heartRateVariability: 45.2,
      intervals: { pr: 156, qrs: 92, qt: 400, qtc: 418, rr: 833 },
      axis: 45,
      qrsAmplitude: 1.2,
      stDeviation: 0.05,
      tWaveAmplitude: 0.4,
    },
    diagnoses: [
      { code: 'I49.9', label: 'Normal Sinus Rhythm', confidence: 0.94, category: 'Normal', icdVersion: '10' },
    ],
    primaryDiagnosis: { code: 'I49.9', label: 'Normal Sinus Rhythm', confidence: 0.94, category: 'Normal', icdVersion: '10' },
    riskLevel: 'normal',
    riskScore: 12,
    confidence: 0.94,
    explainability: [
      {
        id: '1', feature: 'QRS Morphology', contribution: 0.72, importance: 0.85,
        description: 'Normal QRS complex shape',
        children: [
          { id: '1a', feature: 'QRS Duration (92ms)', contribution: 0.38, importance: 0.7 },
          { id: '1b', feature: 'R-wave Amplitude', contribution: 0.34, importance: 0.65 },
        ],
      },
      { id: '2', feature: 'P-wave Presence', contribution: 0.55, importance: 0.75, description: 'Regular P waves preceding each QRS' },
      { id: '3', feature: 'RR Regularity', contribution: 0.48, importance: 0.68, description: 'Regular RR intervals' },
    ],
    recommendations: [
      { priority: 'low', category: 'follow-up', text: 'Routine follow-up in 12 months', rationale: 'Normal ECG findings' },
    ],
    modelVersion: 'v2.1-demo',
    quantumEnhanced: true,
  };
  
  return {
    id: 'normal-sinus-rhythm',
    name: 'Normal Sinus Rhythm',
    description: 'Healthy heart rhythm with regular P-QRS-T pattern',
    heartRate,
    samplingRate,
    duration,
    signal,
    quality,
    analysis,
  };
}

/**
 * Demo Case 2: Sinus Tachycardia
 */
export function createSinusTachycardia(): DemoCase {
  const heartRate = 120;
  const samplingRate = 500;
  const duration = 10;
  
  const signal = generateECGWaveform(heartRate, samplingRate, duration, 0.02, 0);
  
  const quality: SignalQuality = {
    overall: 88,
    noiseLevel: 32,
    baselineWander: false,
    artifactRatio: 0.04,
    leadQualities: { II: 0.90, V1: 0.85, V5: 0.88 },
  };
  
  const analysis: AnalysisResult = {
    id: `demo-tachy-${Date.now()}`,
    timestamp: new Date().toISOString(),
    processingTimeMs: 1156,
    signals: [
      { lead: 'II', data: signal, samplingRate, duration, units: 'mV' },
      { lead: 'V1', data: generateECGWaveform(heartRate, samplingRate, duration, 0.025, 0), samplingRate, duration, units: 'mV' },
      { lead: 'V5', data: generateECGWaveform(heartRate, samplingRate, duration, 0.022, 0), samplingRate, duration, units: 'mV' },
    ],
    quality,
    metrics: {
      heartRate,
      heartRateVariability: 35.8,
      intervals: { pr: 140, qrs: 88, qt: 320, qtc: 445, rr: 500 },
      axis: 42,
      qrsAmplitude: 1.1,
      stDeviation: 0.03,
      tWaveAmplitude: 0.35,
    },
    diagnoses: [
      { code: 'R00.0', label: 'Sinus Tachycardia', confidence: 0.89, category: 'Abnormal', icdVersion: '10' },
    ],
    primaryDiagnosis: { code: 'R00.0', label: 'Sinus Tachycardia', confidence: 0.89, category: 'Abnormal', icdVersion: '10' },
    riskLevel: 'elevated',
    riskScore: 45,
    confidence: 0.89,
    explainability: [
      {
        id: '1', feature: 'Heart Rate', contribution: 0.85, importance: 0.92,
        description: 'Elevated heart rate (120 BPM)',
        children: [
          { id: '1a', feature: 'RR Interval (500ms)', contribution: 0.45, importance: 0.88 },
        ],
      },
      { id: '2', feature: 'QRS Morphology', contribution: 0.42, importance: 0.75, description: 'Normal QRS despite elevated rate' },
      { id: '3', feature: 'P-wave Regularity', contribution: 0.38, importance: 0.70, description: 'P waves present and regular' },
    ],
    recommendations: [
      { priority: 'medium', category: 'monitoring', text: 'Monitor for underlying causes', rationale: 'Tachycardia may indicate stress, exercise, or pathology' },
      { priority: 'low', category: 'lifestyle', text: 'Review caffeine intake', rationale: 'Common trigger for elevated heart rate' },
    ],
    modelVersion: 'v2.1-demo',
    quantumEnhanced: true,
  };
  
  return {
    id: 'sinus-tachycardia',
    name: 'Sinus Tachycardia',
    description: 'Elevated heart rate with normal QRS morphology',
    heartRate,
    samplingRate,
    duration,
    signal,
    quality,
    analysis,
  };
}

/**
 * Demo Case 3: Sinus Bradycardia
 */
export function createSinusBradycardia(): DemoCase {
  const heartRate = 48;
  const samplingRate = 500;
  const duration = 10;
  
  const signal = generateECGWaveform(heartRate, samplingRate, duration, 0.02, 0);
  
  const quality: SignalQuality = {
    overall: 90,
    noiseLevel: 30,
    baselineWander: false,
    artifactRatio: 0.03,
    leadQualities: { II: 0.92, V1: 0.87, V5: 0.89 },
  };
  
  const analysis: AnalysisResult = {
    id: `demo-brady-${Date.now()}`,
    timestamp: new Date().toISOString(),
    processingTimeMs: 1342,
    signals: [
      { lead: 'II', data: signal, samplingRate, duration, units: 'mV' },
      { lead: 'V1', data: generateECGWaveform(heartRate, samplingRate, duration, 0.025, 0), samplingRate, duration, units: 'mV' },
      { lead: 'V5', data: generateECGWaveform(heartRate, samplingRate, duration, 0.022, 0), samplingRate, duration, units: 'mV' },
    ],
    quality,
    metrics: {
      heartRate,
      heartRateVariability: 52.4,
      intervals: { pr: 180, qrs: 95, qt: 480, qtc: 425, rr: 1250 },
      axis: 48,
      qrsAmplitude: 1.25,
      stDeviation: 0.04,
      tWaveAmplitude: 0.42,
    },
    diagnoses: [
      { code: 'R00.1', label: 'Sinus Bradycardia', confidence: 0.87, category: 'Abnormal', icdVersion: '10' },
    ],
    primaryDiagnosis: { code: 'R00.1', label: 'Sinus Bradycardia', confidence: 0.87, category: 'Abnormal', icdVersion: '10' },
    riskLevel: 'borderline',
    riskScore: 32,
    confidence: 0.87,
    explainability: [
      {
        id: '1', feature: 'Heart Rate', contribution: 0.82, importance: 0.90,
        description: 'Reduced heart rate (48 BPM)',
        children: [
          { id: '1a', feature: 'RR Interval (1250ms)', contribution: 0.48, importance: 0.85 },
        ],
      },
      { id: '2', feature: 'QRS Morphology', contribution: 0.45, importance: 0.78, description: 'Normal QRS despite slow rate' },
      { id: '3', feature: 'P-wave Regularity', contribution: 0.40, importance: 0.72, description: 'P waves present and regular' },
    ],
    recommendations: [
      { priority: 'medium', category: 'monitoring', text: 'Evaluate for athletic conditioning or pathology', rationale: 'Bradycardia may be normal in athletes or indicate conduction issues' },
      { priority: 'low', category: 'follow-up', text: 'Monitor for symptoms', rationale: 'Dizziness or syncope may require intervention' },
    ],
    modelVersion: 'v2.1-demo',
    quantumEnhanced: true,
  };
  
  return {
    id: 'sinus-bradycardia',
    name: 'Sinus Bradycardia',
    description: 'Reduced heart rate with normal QRS morphology',
    heartRate,
    samplingRate,
    duration,
    signal,
    quality,
    analysis,
  };
}

/**
 * Demo Case 4: PVC / Arrhythmia
 */
export function createPVCArrhythmia(): DemoCase {
  const heartRate = 75;
  const samplingRate = 500;
  const duration = 10;
  
  const signal = generatePVCWaveform(heartRate, samplingRate, duration);
  
  const quality: SignalQuality = {
    overall: 78,
    noiseLevel: 38,
    baselineWander: true,
    artifactRatio: 0.08,
    leadQualities: { II: 0.82, V1: 0.75, V5: 0.80 },
  };
  
  const analysis: AnalysisResult = {
    id: `demo-pvc-${Date.now()}`,
    timestamp: new Date().toISOString(),
    processingTimeMs: 1456,
    signals: [
      { lead: 'II', data: signal, samplingRate, duration, units: 'mV' },
      { lead: 'V1', data: generatePVCWaveform(heartRate, samplingRate, duration), samplingRate, duration, units: 'mV' },
      { lead: 'V5', data: generatePVCWaveform(heartRate, samplingRate, duration), samplingRate, duration, units: 'mV' },
    ],
    quality,
    metrics: {
      heartRate,
      heartRateVariability: 85.2,
      intervals: { pr: 155, qrs: 140, qt: 420, qtc: 435, rr: 800 },
      axis: 38,
      qrsAmplitude: 1.5,
      stDeviation: 0.12,
      tWaveAmplitude: 0.38,
    },
    diagnoses: [
      { code: 'I49.4', label: 'Premature Ventricular Contraction', confidence: 0.82, category: 'Abnormal', icdVersion: '10' },
      { code: 'I49.9', label: 'Arrhythmia', confidence: 0.65, category: 'Abnormal', icdVersion: '10' },
    ],
    primaryDiagnosis: { code: 'I49.4', label: 'Premature Ventricular Contraction', confidence: 0.82, category: 'Abnormal', icdVersion: '10' },
    riskLevel: 'elevated',
    riskScore: 58,
    confidence: 0.82,
    explainability: [
      {
        id: '1', feature: 'RR Irregularity', contribution: 0.78, importance: 0.88,
        description: 'Irregular RR intervals with premature beats',
        children: [
          { id: '1a', feature: 'RR Variability (85ms)', contribution: 0.52, importance: 0.82 },
        ],
      },
      { id: '2', feature: 'QRS Morphology', contribution: -0.65, importance: 0.85, description: 'Wide QRS complexes in PVCs' },
      { id: '3', feature: 'P-wave Absence', contribution: -0.45, importance: 0.75, description: 'Missing P-waves in premature beats' },
    ],
    recommendations: [
      { priority: 'high', category: 'monitoring', text: 'Holter monitoring recommended', rationale: 'Quantify PVC burden and assess for underlying heart disease' },
      { priority: 'medium', category: 'follow-up', text: 'Evaluate electrolyte status', rationale: 'Electrolyte imbalances can trigger PVCs' },
    ],
    modelVersion: 'v2.1-demo',
    quantumEnhanced: true,
  };
  
  return {
    id: 'pvc-arrhythmia',
    name: 'PVC / Arrhythmia',
    description: 'Irregular rhythm with premature ventricular contractions',
    heartRate,
    samplingRate,
    duration,
    signal,
    quality,
    analysis,
  };
}

/**
 * Demo Case 5: Noisy Signal (Optional)
 */
export function createNoisySignal(): DemoCase {
  const heartRate = 72;
  const samplingRate = 500;
  const duration = 10;
  
  const signal = generateECGWaveform(heartRate, samplingRate, duration, 0.15, 0);
  
  const quality: SignalQuality = {
    overall: 45,
    noiseLevel: 72,
    baselineWander: true,
    artifactRatio: 0.18,
    leadQualities: { II: 0.52, V1: 0.42, V5: 0.48 },
  };
  
  const analysis: AnalysisResult = {
    id: `demo-noisy-${Date.now()}`,
    timestamp: new Date().toISOString(),
    processingTimeMs: 1890,
    signals: [
      { lead: 'II', data: signal, samplingRate, duration, units: 'mV' },
      { lead: 'V1', data: generateECGWaveform(heartRate, samplingRate, duration, 0.18, 0), samplingRate, duration, units: 'mV' },
      { lead: 'V5', data: generateECGWaveform(heartRate, samplingRate, duration, 0.16, 0), samplingRate, duration, units: 'mV' },
    ],
    quality,
    metrics: {
      heartRate: 0, // Cannot determine reliably
      heartRateVariability: 0,
      intervals: { pr: null, qrs: null, qt: null, qtc: null, rr: null },
      axis: null,
      qrsAmplitude: null,
      stDeviation: null,
      tWaveAmplitude: null,
    },
    diagnoses: [
      { code: 'Z71.1', label: 'Poor Signal Quality', confidence: 0.95, category: 'Normal', icdVersion: '10' },
    ],
    primaryDiagnosis: { code: 'Z71.1', label: 'Poor Signal Quality', confidence: 0.95, category: 'Normal', icdVersion: '10' },
    riskLevel: 'normal',
    riskScore: 0,
    confidence: 0.95,
    explainability: [
      {
        id: '1', feature: 'Signal Quality', contribution: 0.92, importance: 0.95,
        description: 'High noise level prevents reliable analysis',
        children: [
          { id: '1a', feature: 'Noise Level (72%)', contribution: 0.68, importance: 0.90 },
          { id: '1b', feature: 'Baseline Wander', contribution: 0.55, importance: 0.82 },
        ],
      },
    ],
    recommendations: [
      { priority: 'high', category: 'follow-up', text: 'Repeat ECG with proper electrode placement', rationale: 'Poor signal quality due to electrode issues or patient movement' },
    ],
    modelVersion: 'v2.1-demo',
    quantumEnhanced: true,
  };
  
  return {
    id: 'noisy-signal',
    name: 'Noisy Signal',
    description: 'Poor quality signal with high noise and baseline drift',
    heartRate,
    samplingRate,
    duration,
    signal,
    quality,
    analysis,
  };
}

/**
 * Get all demo cases
 */
export function getAllDemoCases(): DemoCase[] {
  return [
    createNormalSinusRhythm(),
    createSinusTachycardia(),
    createSinusBradycardia(),
    createPVCArrhythmia(),
    createNoisySignal(),
  ];
}

/**
 * Get demo case by ID
 */
export function getDemoCaseById(id: string): DemoCase | undefined {
  return getAllDemoCases().find((c) => c.id === id);
}
