import sys
from PyQt6.QtWidgets import QApplication
from admin import Admin

def main():
    app = QApplication(sys.argv)
    admin = Admin()  # Singleton instance manages everything
    admin.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
