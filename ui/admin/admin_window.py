from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QFrame, QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .market_control_panel import MarketControlPanel
from .news_event_panel import NewsEventPanel
from .settings_panel import SettingsPanel
from simulation import market_simulation

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.trading_window = None
        self.init_ui()

    def init_ui(self):
        """Initialize the enhanced admin UI"""
        self.setWindowTitle("Trading Simulator - Admin Control")
        self.setMinimumSize(1280, 800)
        
        # Create main container
        main_widget = QWidget()
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create navigation sidebar
        nav_sidebar = self.create_nav_sidebar()
        layout.addWidget(nav_sidebar)
        
        # Create main content area
        main_content = self.create_main_content()
        layout.addWidget(main_content, 1)  # Stretch factor of 1
        
        self.setCentralWidget(main_widget)

    def create_nav_sidebar(self):
        """Create navigation sidebar with modern design"""
        sidebar = QFrame()
        sidebar.setFixedWidth(240)  # Fixed width for consistency
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border-right: 1px solid #3D3D3D;
            }
            QPushButton {
                text-align: left;
                padding: 12px 20px;
                border: none;
                font-size: 14px;
                color: #CCCCCC;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #353535;
                color: white;
            }
            QPushButton:checked {
                background-color: #1E90FF;
                color: white;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Add header
        header = QLabel("Trading Simulator")
        header.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 20px;
            background-color: #1E90FF;
        """)
        layout.addWidget(header)
        
        # Navigation buttons - store them as instance variables
        self.nav_buttons = []
        nav_items = [
            ("🏛️ Market Control", 0),
            ("📰 News & Events", 1),
            ("⚙️ Settings", 2)
        ]
        
        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.clicked.connect(lambda checked, x=index: self.switch_page(x))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)
        
        # Set first button as checked
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
        
        # Add Trading View launcher at bottom
        layout.addStretch()
        self.launch_btn = QPushButton("🚀 Launch Trading View")
        self.launch_btn.setStyleSheet("""
            QPushButton {
                margin: 10px;
                padding: 15px;
                background-color: #1E90FF;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.launch_btn.clicked.connect(self.launch_trading_view)
        layout.addWidget(self.launch_btn)
        
        return sidebar

    def create_main_content(self):
        """Create main content area with stacked layout"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #1F1F1F;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with current section title
        self.page_header = QLabel()
        self.page_header.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
                background-color: #2B2B2B;
                border-bottom: 1px solid #3D3D3D;
            }
        """)
        layout.addWidget(self.page_header)
        
        # Stacked widget for content
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QWidget {
                background-color: #1F1F1F;
            }
        """)
        
        # Initialize panels
        self.market_panel = MarketControlPanel()
        self.news_panel = NewsEventPanel()
        self.settings_panel = SettingsPanel()
        
        # Add panels to stack
        self.content_stack.addWidget(self.market_panel)
        self.content_stack.addWidget(self.news_panel)
        self.content_stack.addWidget(self.settings_panel)
        
        layout.addWidget(self.content_stack)
        
        # Set initial header text
        self.update_header_text(0)
        
        return container

    def switch_page(self, index):
        """Switch between pages and update header"""
        self.content_stack.setCurrentIndex(index)
        self.update_header_text(index)

    def update_header_text(self, index):
        """Update header text based on current page"""
        headers = [
            "Market Control Center",
            "News & Events Management",
            "System Settings"
        ]
        self.page_header.setText(headers[index])

    def launch_trading_view(self):
        """Launch trading view in a separate window"""
        from ..main_window import launch_trading_view
        
        if self.trading_window is not None:
            self.trading_window.close()
            
        self.trading_window = launch_trading_view()
        self.launch_btn.setText("🔄 Trading View Active")
