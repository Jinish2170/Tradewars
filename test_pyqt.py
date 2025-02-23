import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

def test_pyqt():
    try:
        app = QApplication(sys.argv)
        window = QMainWindow()
        label = QLabel("PyQt5 is working!")
        window.setCentralWidget(label)
        window.show()
        app.exec_()
        print("PyQt5 test successful!")
        return True
    except Exception as e:
        print(f"PyQt5 test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_pyqt()
