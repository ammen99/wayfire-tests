# Author: Marcus Britanicus

import sys
from PyQt5.QtWidgets import QApplication, QWidget

app = QApplication(sys.argv)
mw = QWidget()
mw.resize(300, 200)
mw.setWindowTitle('test')
mw.showMaximized()
app.exec_()
