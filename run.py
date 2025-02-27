import sys
import os
from pathlib import Path
import logging
import site

# Get the site-packages directory
site_packages = site.getsitepackages()[0]
qt_plugin_path = str(Path(site_packages) / "PyQt5" / "Qt5" / "plugins")

# Remove debug output
os.environ['QT_DEBUG_PLUGINS'] = '0'  # Change from '1' to '0'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugin_path

# Add Qt logging filter
from PyQt5.QtCore import QtMsgType, qInstallMessageHandler
def qt_message_handler(mode, context, message):
    if mode == QtMsgType.QtWarningMsg:
        # Suppress Qt warnings
        return
    print(f"{message}")

qInstallMessageHandler(qt_message_handler)

# Add the project root to Python path
root_dir = str(Path(__file__).parent)
sys.path.insert(0, root_dir)

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer
    from simulation.market_simulation import market_session
    from ui.main_window import MainWindow
    from utils.logger import logger
except ImportError as e:
    print(f"Error importing PyQt5: {e}")
    print("Try: pip install PyQt5==5.15.9 PyQtChart==5.15.6 PyQt5-sip==12.12.1")
    print(f"Qt plugin path: {qt_plugin_path}")
    sys.exit(1)

# Configuration
MARKET_UPDATE_INTERVAL = 1000  # milliseconds

# Initialize market state before creating UI
def main():
    try:
        # Create the application
        app = QApplication(sys.argv)
        
        # Initialize market before creating UI
        from simulation import market_state
        market_state.initialize_market()
        logger.info("Market initialized with stocks: " + ", ".join(market_state.stock_prices.keys()))
        
        # Create and show the main window
        window = MainWindow()
        window.show()
        
        # Setup market update timer
        market_timer = QTimer()
        market_timer.timeout.connect(market_session.update)
        market_timer.start(MARKET_UPDATE_INTERVAL)
        
        # Start the market session
        if market_session.start_session():
            logger.info("Market session started successfully")
        else:
            logger.error("Failed to start market session")
            return 1
        
        # Start the event loop
        return app.exec_()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        return 1
    
if __name__ == "__main__":
    sys.exit(main())
