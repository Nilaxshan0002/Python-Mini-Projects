from fastapi import FastAPI
from app.api.routes import router

# Create the FastAPI application instance
app = FastAPI(
    title="AutoBrowse AI Agent", 
    description="An AI agent that handles repetitive browser tasks automatically.",
    version="1.0.0"
)

# Attach all our API routes to the app
app.include_router(router, prefix="/api")

# A simple check to make sure the server starts correctly
@app.get("/")
def read_root():
    return {"message": "Welcome to the AutoBrowse AI Agent API. Go to /docs to test it!"}

if __name__ == "__main__":
    import uvicorn
    # Run the server
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)