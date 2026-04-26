from fastapi import FastAPI

app = FastAPI(
    title="MedQuantum-NIN API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
