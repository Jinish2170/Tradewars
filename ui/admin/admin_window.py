from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QTabWidget
# Use relative imports for files in same directory
from .market_control_panel import MarketControlPanel
from .news_event_panel import NewsEventPanel
from .settings_panel import SettingsPanel
# Use absolute import for simulation module
from simulation import market_simulation

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        menu_bar = self.menuBar()
        tabs = QTabWidget()
        
        # Market Control Panel
        market_panel = MarketControlPanel()
        tabs.addTab(market_panel, "Market Control")
        
        # News/Event Panel
        news_panel = NewsEventPanel()
        tabs.addTab(news_panel, "News & Events")
        
        # Settings Panel
        settings_panel = SettingsPanel()
        tabs.addTab(settings_panel, "Settings")
        
        # Remove Team Management Panel as it's moved to main view
        
        self.setCentralWidget(tabs)
        self.statusBar().showMessage("Ready")

    # Remove old panel creation methods as they're no longer needed

    def launch_ipo(self):
        ipo_data = {
            'stock': self.ipo_stock_name.text(),
            'initial_price': self.ipo_price.value(),
            'available_quantity': self.ipo_quantity.value()
        }
        market_simulation.inject_IPO(ipo_data)

    def publish_news(self):
        event_data = {
            'content': self.news_text.toPlainText(),
            'impact': self.impact_spin.value() / 100.0
        }
        market_simulation.inject_news_event(event_data)
