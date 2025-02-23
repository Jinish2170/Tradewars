
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QPushButton, QLabel, QDoubleSpinBox)
import config

class SettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Market Parameters
        param_group = QGroupBox("Market Parameters")
        param_layout = QVBoxLayout()

        # Demand Coefficient
        demand_layout = QHBoxLayout()
        self.demand_spin = QDoubleSpinBox()
        self.demand_spin.setRange(0.01, 1.0)
        self.demand_spin.setSingleStep(0.01)
        self.demand_spin.setValue(config.DEMAND_COEFFICIENT)
        demand_layout.addWidget(QLabel("Demand Coefficient:"))
        demand_layout.addWidget(self.demand_spin)
        param_layout.addLayout(demand_layout)

        # Event Coefficient
        event_layout = QHBoxLayout()
        self.event_spin = QDoubleSpinBox()
        self.event_spin.setRange(0.01, 1.0)
        self.event_spin.setSingleStep(0.01)
        self.event_spin.setValue(config.EVENT_COEFFICIENT)
        event_layout.addWidget(QLabel("Event Coefficient:"))
        event_layout.addWidget(self.event_spin)
        param_layout.addLayout(event_layout)

        # Random Noise
        noise_layout = QHBoxLayout()
        self.noise_spin = QDoubleSpinBox()
        self.noise_spin.setRange(0.0, 0.5)
        self.noise_spin.setSingleStep(0.01)
        self.noise_spin.setValue(config.RANDOM_NOISE)
        noise_layout.addWidget(QLabel("Random Noise:"))
        noise_layout.addWidget(self.noise_spin)
        param_layout.addLayout(noise_layout)

        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        # Save Button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_settings(self):
        """Save settings back to config"""
        config.DEMAND_COEFFICIENT = self.demand_spin.value()
        config.EVENT_COEFFICIENT = self.event_spin.value()
        config.RANDOM_NOISE = self.noise_spin.value()
        
        # Update the CONFIG dictionary
        config.CONFIG.update({
            'DEMAND_COEFFICIENT': config.DEMAND_COEFFICIENT,
            'EVENT_COEFFICIENT': config.EVENT_COEFFICIENT,
            'RANDOM_NOISE': config.RANDOM_NOISE
        })
