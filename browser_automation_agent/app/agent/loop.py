from openai import OpenAI
import json
import os
import logging
from dotenv import load_dotenv
from app.browser.controller import BrowserController
from app.agent.prompts import SYSTEM_PROMPT

load_dotenv()
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def run_agent_task(task: str, start_url: str, max_steps: int = 15):
    browser = BrowserController(headless=False) # Set True for background execution
    history = []
    
    try:
        # Step 1: Navigate to start URL
        nav_result = browser.navigate(start_url)
        logger.info(nav_result)
        
        for step in range(max_steps):
            logger.info(f"--- Step {step + 1} ---")
            
            # 1. Observe
            screenshot_base64 = browser.get_screenshot()
            
            # 2. Think
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": f"TASK: {task}\n\nHISTORY: {json.dumps(history)}\n\nWhat is the next action?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}}
                ]}
            ]
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.1 # Low temperature for more deterministic actions
                )
                action_json = json.loads(response.choices[0].message.content)
            except Exception as e:
                # --- CHANGED THIS SECTION TO SHOW THE REAL ERROR ---
                logger.error(f"🚨 REAL LLM ERROR: {e}")
                return f"Agent failed. Reason: {str(e)}", step
                # ---------------------------------------------------

            action_type = action_json.get("action")
            logger.info(f"Agent decided: {action_json}")
            
            # 3. Act
            if action_type == "click":
                result = browser.click(action_json["x"], action_json["y"])
            elif action_type == "type":
                result = browser.type_text(action_json["text"])
            elif action_type == "scroll":
                result = browser.scroll(action_json["direction"])
            elif action_type == "press_key":
                result = browser.press_key(action_json["key"])
            elif action_type == "done":
                return action_json.get("result", "Task completed."), step + 1
            else:
                result = f"Error: Unknown action '{action_type}'"
                
            logger.info(result)
            history.append({"step": step + 1, "action": action_json, "result": result})
            
        return "Task timed out (reached max steps).", max_steps
        
    finally:
        # Ensure browser always closes, even if it crashes
        browser.close()