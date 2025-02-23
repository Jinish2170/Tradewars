import sys
from PyQt5.QtWidgets import QApplication
from ui.components.price_chart import PriceChart

def test_chart():
    app = QApplication(sys.argv)
    chart = PriceChart("TEST")
    chart.show()
    chart.update_price(100)
    return app.exec_()

if __name__ == "__main__":
    sys.exit(test_chart())
