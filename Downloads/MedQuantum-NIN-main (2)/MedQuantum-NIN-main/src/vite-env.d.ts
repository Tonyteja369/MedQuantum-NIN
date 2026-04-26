/// <reference types="vite/client" />

interface ImportMetaEnv {
	readonly VITE_API_URL?: string
	readonly VITE_BACKEND_SERVICE_URL?: string
	readonly VITE_BACKEND_UPLOAD_PATH?: string
	readonly VITE_BACKEND_LOAD_SAMPLE_PATH?: string
	readonly VITE_BACKEND_ANALYZE_PATH?: string
	readonly VITE_BACKEND_ANALYSIS_RESULT_PATH?: string
	readonly VITE_BACKEND_REPORT_PATH?: string
	readonly VITE_BACKEND_SIGNAL_ID_FIELD?: string
	readonly VITE_BACKEND_PATIENT_CONTEXT_FIELD?: string
}

interface ImportMeta {
	readonly env: ImportMetaEnv
}
