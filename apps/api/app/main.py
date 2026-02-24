from fastapi import FastAPI

app = FastAPI(title="LeaseLensAI API", version="0.1.0")

@app.get("/healthz")
def health_check():
    return {"status": "healthy", "service": "LeaseLensAI API"}

@app.get("/")
def root():
    return {"message": "Welcome to LeaseLensAI API"}