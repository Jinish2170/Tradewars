from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis
from PyQt5.QtCore import Qt
from ..styles import COLORS, CHART_STYLE

class VolumeChart(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout(self)
        
        # Create chart
        self.chart = QChart()
        self.chart.setTheme(QChart.ChartThemeDark)
        self.chart.setBackgroundVisible(False)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create series
        self.volume_series = QBarSeries()
        self.volume_set = QBarSet("Volume")
        self.volume_series.append(self.volume_set)
        
        # Add series to chart
        self.chart.addSeries(self.volume_series)
        
        # Create axes
        self.time_axis = QBarCategoryAxis()
        self.volume_axis = QValueAxis()
        self.chart.addAxis(self.time_axis, Qt.AlignBottom)
        self.chart.addAxis(self.volume_axis, Qt.AlignLeft)
        self.volume_series.attachAxis(self.time_axis)
        self.volume_series.attachAxis(self.volume_axis)
        
        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setStyleSheet(CHART_STYLE)
        
        layout.addWidget(self.chart_view)
        
    def update_volume(self, volumes):
        self.volume_set.remove(0, self.volume_set.count())
        for volume in volumes:
            self.volume_set.append(float(volume))
