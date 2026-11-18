# AutoBrowse AI Agent

An AI-powered browser automation agent built with Python, Playwright, LLM (GPT-4o), and FastAPI. 

## Setup
1. Create virtual environment: `python -m venv venv`
2. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
3. Install dependencies: `pip install -r requirements.txt`
4. Install Playwright browsers: `playwright install chromium`
5. Add your OpenAI API key to the `.env` file.
6. Run the server: `python main.py`

## Usage
Send a POST request to `http://localhost:8000/api/run-task`:
```json
{
  "task": "Search for the latest news about Playwright on Google.",
  "start_url": "https://www.google.com"
}

#### 5. `main.py`
```python
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="AutoBrowse AI Agent", 
    description="An AI agent that handles repetitive browser tasks automatically.",
    version="1.0.0"
)

# Include the routes
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    # reload=True is for development. Turn it off for production.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)