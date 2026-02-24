from fastapi import FastAPI
from .database import engine
from .models import Base
from .routers import auth

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LeaseLensAI API", version="0.1.0")

app.include_router(auth.router)

@app.get("/healthz")
def health_check():
    return {"status": "healthy", "service": "LeaseLensAI API"}

@app.get("/")
def root():
    return {"message": "Welcome to LeaseLensAI API"}