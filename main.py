from fastapi import FastAPI
from app.database import engine, Base
from app.routes import router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Monitoring Tool", description="Automatically test APIs and track uptime.")

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to the API Monitor. Go to /docs to test the API."}