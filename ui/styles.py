from PyQt5.QtGui import QColor

# Professional trading platform color scheme
COLORS = {
    'background': '#1C1C28',  # Dark theme background
    'card_background': '#282834',  # Slightly lighter for cards
    'text': '#E8E8E8',  # Bright text
    'text_secondary': '#A0A0A8',  # Muted text
    'accent': '#2962FF',  # Vibrant blue
    'accent_hover': '#2979FF',  # Lighter blue for hover
    'positive': '#00C853',  # Bright green
    'negative': '#FF3D00',  # Bright red
    'neutral': '#FFB300',  # Warning/neutral amber
    'chart_grid': '#32323E',  # Subtle grid lines
    'border': '#3E3E4A',  # Refined borders
    'hover': '#303042',  # Hover state
    'active': '#2962FF20',  # Active state with transparency
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