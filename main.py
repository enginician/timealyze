
from PyQt5.QtWidgets import *
import timing
import sys

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = QWidget()
    window.setGeometry(300, 300, 600, 600)
    window.setWindowTitle('The Timealyzer')
    button = QPushButton('Timealyze!')
    layout = QVBoxLayout()
    layout.addWidget(button)
    layout.addWidget(QPushButton('Bottom'))
    window.setLayout(layout)

    def on_button_click():
        timing.timealyze()
        print("clicked")

    button.clicked.connect(on_button_click)
    window.show()
    sys.exit(app.exec())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
