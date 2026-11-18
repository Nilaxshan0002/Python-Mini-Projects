from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QLineEdit, QPushButton, QLabel, QListWidget, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ai_engine import chat_with_local_ai
from database import init_db

# --- Worker Thread so the UI doesn't freeze while the AI thinks ---
class AIWorker(QThread):
    finished = pyqtSignal(str)
    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt
    def run(self):
        response = chat_with_local_ai(self.prompt)
        self.finished.emit(response)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LocalAI - Your Personal AI Assistant")
        self.resize(1000, 700)
        init_db()
        
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # --- SIDEBAR ---
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #2b2b2b; color: white; border-radius: 5px;")
        sidebar_layout = QVBoxLayout(sidebar)
        
        title = QLabel("🤖 LocalAI")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        sidebar_layout.addWidget(title)
        
        btn_chat = QPushButton("💬 Chat")
        btn_library = QPushButton("📚 Library")
        btn_notes = QPushButton("📝 Notes")
        
        for btn in [btn_chat, btn_library, btn_notes]:
            btn.setStyleSheet("text-align: left; padding: 10px; font-size: 14px; border: none;")
            sidebar_layout.addWidget(btn)
            
        sidebar_layout.addStretch()
        status = QLabel("🟢 Ollama Running Locally")
        status.setStyleSheet("color: #4CAF50; padding: 10px;")
        sidebar_layout.addWidget(status)
        
        main_layout.addWidget(sidebar)
        
        # --- MAIN CHAT AREA ---
        chat_area = QWidget()
        chat_layout = QVBoxLayout(chat_area)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-size: 15px; padding: 10px; border-radius: 5px;")
        chat_layout.addWidget(self.chat_display)
        
        # Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask LocalAI to read a folder or save a note...")
        self.input_field.setStyleSheet("padding: 10px; font-size: 14px; background-color: #333; color: white; border-radius: 5px;")
        self.input_field.returnPressed.connect(self.send_message)
        
        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("padding: 10px 20px; background-color: #0078D7; color: white; font-weight: bold; border-radius: 5px;")
        send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_btn)
        
        chat_layout.addLayout(input_layout)
        main_layout.addWidget(chat_area)
        
        # Welcome Message
        self.chat_display.append("<b>LocalAI:</b> Hello! I am running 100% locally on your machine. How can I help you today?")

    def send_message(self):
        user_text = self.input_field.text().strip()
        if not user_text:
            return
            
        self.chat_display.append(f"<br><b style='color: #569cd6;'>You:</b> {user_text}")
        self.input_field.clear()
        
        self.chat_display.append("<i style='color: gray;'>LocalAI is thinking...</i>")
        
        # Start background thread
        self.worker = AIWorker(user_text)
        self.worker.finished.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, response):
        # Remove the "thinking..." message
        self.chat_display.undo() 
        
        # Add AI response
        formatted_response = response.replace('\n', '<br>')
        self.chat_display.append(f"<b style='color: #4CAF50;'>LocalAI:</b> {formatted_response}")