import sys
from PyQt5.QtWidgets import QApplication, QWidget

app = QApplication(sys.argv[:1])
mw = QWidget()
mw.setWindowTitle('test')

minw, minh = int(sys.argv[1]), int(sys.argv[2])
maxw, maxh = int(sys.argv[3]), int(sys.argv[4])

if minw > 0 and minh > 0:
    mw.setMinimumSize(minw, minh)
if maxw > 0 and maxh > 0:
    mw.setMaximumSize(maxw, maxh)

mw.resize(100, 100)
mw.show()
app.exec_()
