import os

def read_text_files(folder_path):
    """Reads the first 3 text files found in a folder."""
    if not os.path.exists(folder_path):
        return "Folder does not exist."
    
    content_summary = ""
    files_read = 0
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt") and files_read < 3:
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content_summary += f"\n--- File: {filename} ---\n"
                    content_summary += f.read()[:500] + "...\n" # Read first 500 chars
                files_read += 1
            except Exception as e:
                pass
                
    if files_read == 0:
        return "No .txt files found in that folder."
    return content_summary