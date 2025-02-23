from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QApplication
from ui.participant_view import ParticipantView
from ui.admin.admin_window import AdminWindow
from ui.styles import MAIN_WINDOW_STYLE, COLORS

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trading War Simulator")
        self.setGeometry(100, 100, 1280, 800)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['chart_grid']};
                background: {COLORS['background']};
            }}
            QTabBar::tab {{
                background: {COLORS['card_background']};
                color: {COLORS['text']};
                padding: 8px 16px;
                border: 1px solid {COLORS['chart_grid']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['background']};
                margin-bottom: -1px;
            }}
        """)
        
        self.setCentralWidget(self.tabs)
        
        # Create participant view tab
        self.participant_view = ParticipantView()
        self.tabs.addTab(self.participant_view, "Trading View")
        
        # Create admin view tab
        self.admin_view = AdminWindow()
        self.tabs.addTab(self.admin_view, "Admin Dashboard")

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
