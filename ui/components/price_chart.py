from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QPainter, QColor
from ..styles import COLORS, CHART_STYLE

class PriceChart(QWidget):
    def __init__(self, stock_symbol):
        super().__init__()
        self.stock_symbol = stock_symbol
        self.price_history = []
        self.setup_chart()
        
    def setup_chart(self):
        layout = QVBoxLayout(self)
        
        # Create chart
        self.chart = QChart()
        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.setBackgroundVisible(False)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create series
        self.price_series = QLineSeries()
        self.price_series.setName(f"{self.stock_symbol} Price")
        
        # Fix: Create QPen with proper QColor object
        try:
            color = QColor(COLORS['accent'])
            pen = QPen()
            pen.setColor(color)
            pen.setWidth(2)
            self.price_series.setPen(pen)
        except Exception as e:
            print(f"Error setting pen: {e}")
            # Fallback to default pen if there's an error
            self.price_series.setPen(QPen())
        
        # Add series to chart
        self.chart.addSeries(self.price_series)
        
        # Create axes
        self.time_axis = QValueAxis()
        self.price_axis = QValueAxis()
        self.time_axis.setRange(0, 100)  # Set initial range
        self.price_axis.setRange(0, 100)  # Set initial range
        
        self.chart.addAxis(self.time_axis, Qt.AlignBottom)
        self.chart.addAxis(self.price_axis, Qt.AlignLeft)
        
        self.price_series.attachAxis(self.time_axis)
        self.price_series.attachAxis(self.price_axis)
        
        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setStyleSheet(CHART_STYLE)
        
        layout.addWidget(self.chart_view)
        
    def update_price(self, price):
        try:
            self.price_history.append(float(price))
            if len(self.price_history) > 100:
                self.price_history.pop(0)
                
            points = []
            for i, p in enumerate(self.price_history):
                points.append(QPointF(float(i), float(p)))
            
            self.price_series.replace(points)
            
            if self.price_history:
                min_price = min(self.price_history)
                max_price = max(self.price_history)
                if min_price != max_price:
                    margin = (max_price - min_price) * 0.1
                    self.price_axis.setRange(min_price - margin, max_price + margin)
                else:
                    self.price_axis.setRange(min_price * 0.9, min_price * 1.1)
                    
        except Exception as e:
            print(f"Error updating price chart: {e}")
