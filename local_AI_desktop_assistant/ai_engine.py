import ollama
from database import save_note
from tools import read_text_files

def chat_with_local_ai(user_message):
    # System prompt to teach the AI its job
    system_prompt = """
    You are LocalAI, a helpful desktop assistant. 
    If the user asks you to read a folder, output a JSON block like this: 
    {"action": "read_folder", "path": "C:/Users/Name/Documents"}
    If the user asks you to save a note, output a JSON block like this:
    {"action": "save_note", "title": "Title Here", "content": "Content Here"}
    Otherwise, just answer normally.
    """
    
    # Send to Ollama
    try:
        response = ollama.chat(model='llama3', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message},
        ])
        ai_reply = response['message']['content']
        
        # --- Agent Logic (Check if AI wants to use a tool) ---
        if '"action": "read_folder"' in ai_reply:
            # Extract the path (simplified for this demo)
            import json, re
            json_match = re.search(r'\{.*\}', ai_reply)
            if json_match:
                data = json.loads(json_match.group())
                folder_content = read_text_files(data.get("path", ""))
                
                # Send the folder content back to the AI to summarize
                final_response = ollama.chat(model='llama3', messages=[
                    {'role': 'user', 'content': f"Here is the folder content: {folder_content}. Please summarize it."}
                ])
                return final_response['message']['content']
                
        elif '"action": "save_note"' in ai_reply:
            import json, re
            json_match = re.search(r'\{.*\}', ai_reply)
            if json_match:
                data = json.loads(json_match.group())
                save_note(data.get("title"), data.get("content"))
                return f"✅ I have saved the note '{data.get('title')}' to your database."
                
        return ai_reply
        
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}\n\nDid you run 'ollama run llama3' in your terminal?"