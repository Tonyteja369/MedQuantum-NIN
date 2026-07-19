# Architecture

This document describes the implemented architecture in the current repository.

## System Architecture

```mermaid
flowchart LR
  UI[React UI
src/] --> API[FastAPI
backend/app/main.py]
  API --> ECG[ECG Router
/api/ecg]
  API --> ANALYSIS[Analysis Router
/api/analysis]
  API --> REPORT[Report Router
/api/report]

  ECG --> PRE[ECGPreprocessor]
  ANALYSIS --> FEAT[ECGFeatureExtractor]
  ANALYSIS --> RULE[ClinicalRuleEngine]
  ANALYSIS --> EXPL[ExplainabilityEngine]
  ANALYSIS --> ML[MLModelPlaceholder]
  REPORT --> SOAP[SOAP + summaries]

  ECG --> TEMP[(data/temp
.npz/.json signal cache)]
  ANALYSIS --> TEMP
  REPORT --> TEMP
```

## Frontend Architecture

```mermaid
flowchart TD
  App[App.tsx] --> Router[React Router]
  Router --> Landing[LandingPage]
  Router --> Upload[UploadDashboard]
  Router --> Analysis[AnalysisDashboard]
  Router --> Report[ReportPage]

  Upload --> FileHook[useFileUpload]
  Upload --> Store[useECGStore]
  Analysis --> AnalysisHook[useECGAnalysis]
  Report --> Store

  FileHook --> APIClient[src/api/ecgApi.ts]
  AnalysisHook --> APIClient
```

## Backend Architecture

```mermaid
flowchart TD
  Main[app.main] --> ECGRouter[routers/ecg.py]
  Main --> AnalysisRouter[routers/analysis.py]
  Main --> ReportRouter[routers/report.py]

  ECGRouter --> SignalIO[utils/signal_io.py]
  ECGRouter --> Preprocessing[services/preprocessing.py]

  AnalysisRouter --> Preprocessing
  AnalysisRouter --> FeatureExtraction[services/feature_extraction.py]
  AnalysisRouter --> RuleEngine[services/rule_engine.py]
  AnalysisRouter --> Explainability[services/explainability.py]
  AnalysisRouter --> MLPlaceholder[services/ml_placeholder.py]

  ReportRouter --> AnalysisRouter
```

## Deployment Architecture

```mermaid
flowchart LR
  Browser --> FrontendContainer[Frontend Container]
  FrontendContainer --> BackendContainer[Backend Container]
  BackendContainer --> DataVolume[(ecg-data volume)]
```
