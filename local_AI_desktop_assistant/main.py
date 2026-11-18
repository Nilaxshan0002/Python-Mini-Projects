import sys
from PyQt6.QtWidgets import QApplication
from ui.window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Optional: Set a global dark theme for the app
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())