import sys
from PyQt5.QtWidgets import QApplication, QWidget

app = QApplication(sys.argv[:1])
mw = QWidget()
mw.setWindowTitle('test')
mw.setMinimumSize(int(sys.argv[1]), int(sys.argv[2]))
mw.setMaximumSize(int(sys.argv[3]), int(sys.argv[4]))
mw.resize(100, 100)
mw.show()
app.exec_()
