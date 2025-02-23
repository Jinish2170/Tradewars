from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from ui.admin.admin_window import AdminWindow
from ui.styles import MAIN_WINDOW_STYLE

class MainWindow(QMainWindow):
    def __init__(self, view_type='admin'):
        super().__init__()
        self.setWindowTitle("Trading War Simulator")
        self.setGeometry(100, 100, 1280, 800)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # Initialize based on view type
        if view_type == 'admin':
            self.init_admin_view()
        else:
            self.init_trading_view()

    def init_admin_view(self):
        """Initialize admin dashboard"""
        self.admin_view = AdminWindow()
        self.setCentralWidget(self.admin_view)

    def init_trading_view(self):
        """Initialize trading view"""
        from ui.participant_view import ParticipantView
        self.trading_view = ParticipantView()
        self.setCentralWidget(self.trading_view)

def launch_trading_view():
    """Creates and shows a new trading view window"""
    trading_window = MainWindow(view_type='trading')
    trading_window.show()
    return trading_window

def main():
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Create admin window
    admin_window = MainWindow(view_type='admin')
    admin_window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
