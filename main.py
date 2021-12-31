from PyQt5.QtWidgets import *
import timing
import recorder
import sys

# main file mainly containing the GUI conrols

if __name__ == '__main__':

    # create instance of class Recorder (see recorder.py)
    rec = recorder.recorder()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = QWidget()
    window.setGeometry(300, 300, 600, 600)
    window.setWindowTitle('timalyze')
    timealize_button = QPushButton('timealyze')
    record_button = QPushButton('record')
    stoprec_button = QPushButton("stop recording")
    layout = QVBoxLayout()
    layout.addWidget(timealize_button)
    layout.addWidget(record_button)
    layout.addWidget(stoprec_button)
    window.setLayout(layout)

    def click_timealyze():
        timing.timealyze()
        print("timalize clicked")

    def click_record():
        rec.start()
        print("record clicked")

    def click_stoprec():
        rec.stop()
        print("stopped recording")
        rec.save("output.wav")
        print("saved recording")

    timealize_button.clicked.connect(click_timealyze)
    record_button.clicked.connect(click_record)
    stoprec_button.clicked.connect(click_stoprec)
    window.show()
    sys.exit(app.exec())