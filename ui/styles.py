from PyQt5.QtGui import QColor

# Update COLORS dictionary with complete color set
COLORS = {
    'background': '#1E1E2E',      # Dark background
    'card': '#262837',            # Slightly lighter for cards
    'primary': '#2D5AF7',         # Bright blue for primary actions
    'primary_light': '#3D66F5',   # Lighter primary
    'primary_dark': '#1D4AE7',    # Darker primary
    'accent': '#00A3FF',          # Vibrant blue for accents
    'accent_hover': '#0091FF',    # Hover state for accent
    'text': '#FFFFFF',            # Pure white for main text
    'text_secondary': '#94A3B8',  # Soft gray for secondary text
    'text_light': '#CBD5E1',      # Light gray text
    'border': '#363853',          # Subtle borders
    'success': '#10B981',         # Green for positive actions
    'error': '#EF4444',           # Red for negative actions
    'warning': '#F59E0B',         # Amber for warnings
    'hover': '#2F3349',           # Hover state color
    'disabled': '#64748B',        # Disabled state
    'white': '#FFFFFF',           # Pure white
    'positive': '#10B981',        # For positive changes (same as success)
    'negative': '#EF4444',        # For negative changes (same as error)
    'neutral': '#94A3B8',         # For neutral states
    'chart_grid': '#363853',      # For chart grid lines
    'active': '#2D5AF720',        # Semi-transparent primary for active states
    'card_background': '#262837'  # Same as card for consistency
}

# Fix the animation style by using double braces to escape them
PRICE_CHANGE_ANIMATION = """
@keyframes flash-positive {{
    0% {{ background-color: {0}20; }}
    100% {{ background-color: transparent; }}
}}

@keyframes flash-negative {{
    0% {{ background-color: {1}20; }}
    100% {{ background-color: transparent; }}
}}
""".format(COLORS['positive'], COLORS['negative'])

# Enhanced main window style
MAIN_WINDOW_STYLE = """
QWidget {
    /* Unify default background color */
    background-color: #282c34;
    color: #EEEEEE;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}
"""

# Enhanced table style
TABLE_STYLE = f"""
QTableWidget {{
    background-color: {COLORS['card_background']};
    color: {COLORS['text']};
    gridline-color: {COLORS['border']};
    border: none;
    border-radius: 8px;
    padding: 5px;
    selection-background-color: {COLORS['accent']};
    selection-color: {COLORS['background']};
}}

QTableWidget::item {{
    padding: 10px;
    border-bottom: 1px solid {COLORS['border']};
}}

QHeaderView::section {{
    background-color: {COLORS['background']};
    color: {COLORS['text_secondary']};
    padding: 10px;
    border: none;
    font-weight: bold;
    text-transform: uppercase;
    font-size: 11px;
}}

QTableCornerButton::section {{
    background-color: {COLORS['background']};
    border: none;
}}
"""

# Enhanced button style
BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLORS['accent']};
    color: {COLORS['background']};
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 13px;
    min-width: 100px;
}}

QPushButton:hover {{
    background-color: {COLORS['accent_hover']};
}}

QPushButton:pressed {{
    background-color: {COLORS['accent']}99;
}}

QPushButton:disabled {{
    background-color: {COLORS['chart_grid']};
    color: {COLORS['text_secondary']};
}}
"""

# Enhanced group box style
GROUP_BOX_STYLE = """
QGroupBox {
    border: 1px solid #555;
    border-radius: 6px;
    margin-top: 10px;
    padding: 10px;
    font-weight: bold;
}
"""

SPIN_BOX_STYLE = f"""
QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['card_background']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['chart_grid']};
    border-radius: 4px;
    padding: 5px;
}}
"""

COMBO_BOX_STYLE = f"""
QComboBox {{
    background-color: {COLORS['card_background']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['chart_grid']};
    border-radius: 4px;
    padding: 5px;
}}

QComboBox::drop-down {{
    border: none;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {COLORS['text']};
}}
"""

# Enhanced price ticker style
PRICE_TICKER_STYLE = """
QFrame {
    background-color: rgba(255,255,255,0.03);
    border: 1px solid #444;
    border-radius: 8px;
}
QLabel#price {
    font-size: 18px;
    font-weight: bold;
}
QLabel#change_up {
    color: #98C379;
}
QLabel#change_down {
    color: #E06C75;
}
"""

# Add chart styles
CHART_STYLE = f"""
QChart {{
    background-color: {COLORS['card_background']};
    border: none;
    border-radius: 12px;
    padding: 10px;
}}

QChartView {{
    background-color: transparent;
}}

QLineSeries {{
    color: {COLORS['accent']};
}}
"""

# Enhanced table style for market data
MARKET_TABLE_STYLE = f"""
QTableWidget {{
    background-color: {COLORS['card_background']};
    color: {COLORS['text']};
    gridline-color: {COLORS['border']};
    border: none;
    border-radius: 12px;
    padding: 8px;
    selection-background-color: {COLORS['active']};
    selection-color: {COLORS['text']};
}}

QTableWidget::item {{
    padding: 12px;
    border-bottom: 1px solid {COLORS['border']};
}}

QTableWidget::item:hover {{
    background-color: {COLORS['hover']};
}}

QHeaderView::section {{
    background-color: {COLORS['background']};
    color: {COLORS['text_secondary']};
    padding: 12px;
    border: none;
    font-weight: bold;
    text-transform: uppercase;
    font-size: 12px;
}}
"""

# Add tooltip style
TOOLTIP_STYLE = f"""
QToolTip {{
    background-color: {COLORS['card_background']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 8px;
    font-size: 12px;
}}
"""

# Enhanced input field styles
INPUT_STYLE = f"""
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {COLORS['background']};
    color: {COLORS['text']};
    border: 2px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 120px;
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border-color: {COLORS['accent']};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {COLORS['text']};
    margin-right: 8px;
}}
"""

# Add APP_STYLE definition
APP_STYLE = f"""
QMainWindow, QDialog {{
    background-color: {COLORS['background']};
    color: {COLORS['text']};
    font-family: 'Segoe UI', Arial, sans-serif;
}}

QWidget {{
    font-size: 12px;
}}

QLabel {{
    color: {COLORS['text']};
}}

QGroupBox {{
    font-weight: bold;
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    margin-top: 12px;
    padding: 10px;
}}

QPushButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_light']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:disabled {{
    background-color: {COLORS['disabled']};
    color: {COLORS['text_light']};
}}

QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['white']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 6px;
}}

QComboBox {{
    background-color: {COLORS['white']};
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 6px;
}}

QStatusBar {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
}}

QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
}}

QTabBar::tab {{
    background-color: {COLORS['background']};
    color: {COLORS['text']};
    padding: 8px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['primary']};
    color: {COLORS['white']};
}}

QScrollBar:vertical {{
    border: none;
    background-color: {COLORS['background']};
    width: 12px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""