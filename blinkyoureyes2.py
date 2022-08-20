# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPainter, QPixmap
import platform
from ewmh import EWMH

class BlinkYourEyesWidget(QtWidgets.QWidget):

    def __init__(self, availablegeom, parent = None, widget = None):
        super(BlinkYourEyesWidget, self).__init__()
        # Avoid this window appearing from alt-tab window selection
        # see the followings:
        # https://stackoverflow.com/questions/3553428/how-can-i-prevent-gnome-from-showing-two-windows-when-doing-alt-tab-c-qt-app
        # https://doc.qt.io/qt-5/qt.html#WindowType-enum
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint|QtCore.Qt.Tool)

        # self.setStyleSheet('QMainWindow{background-color: darkgray;border: 5px solid black;}')
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput | Qt.WindowDoesNotAcceptFocus)
        self.setGeometry(availablegeom)
        # cprint(self.geometry())
        self.geom = availablegeom
        # print(availablegeom)
        # self.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        # self.showFullScreen()
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        # self.setWindowOpacity(1.0)
        # self.setStyleSheet("QWidget{background: #000000}")
        # self.setStyleSheet("background: transparent;")

        #self.setFocusPolicy(QtCore.Qt.NoFocus)
        #self.setStyleSheet("background-color:transparent;")

        self.clearpaint = False
        self.timer_count = 0
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)  # [milliseconds]
        self.timer.timeout.connect(self.timer_callback)
        self.pencolor = QtCore.Qt.darkGreen

        self.show()

        if platform.system() == 'Linux':
            self.ewmh = EWMH()
            all_wins = self.ewmh.getClientList()
            wins = filter(lambda w: 'blinkyoureyes' in w.get_wm_class()[1], all_wins)
            for w in wins:
                self.ewmh.setWmDesktop(w, 0xffffffff)
            self.ewmh.display.flush()

        self.timer.start()

    def timer_callback(self, ):
        # https://github.com/fullermd/ctwm-mirror-old/blob/3e524368e11553c1a25389f33a667620c3b1bf43/ewmh.h#L37
        if platform.system() == 'Linux':
            all_wins = self.ewmh.getClientList()
            import Xlib.error
            try:
                winstates = [w.get_wm_state()['state'] for w in all_wins]
                if 4 in winstates:
                    # there is a fullscreen window
                    print('there is a fullscreen window')
                    self.hide()
                else:
                    self.show()
            except Xlib.error.BadWindow:
                pass
        self.timer_count = (self.timer_count + 1)%30 #1 seconds
        if self.timer_count == 0:
            self.pencolor = QtCore.Qt.green
            # self.pencolor = QtCore.Qt.darkGreen
            self.clearpaint = False
            self.repaint()
        elif self.timer_count == 3:
            #self.pencolor = QtCore.Qt.darkGreen
            self.clearpaint = True
            self.update()
            self.repaint()
        elif self.timer_count == 6:
            self.pencolor = QtCore.Qt.green
            # self.pencolor = QtCore.Qt.darkGreen
            self.clearpaint = False
            self.repaint()
        elif self.timer_count == 9:
            #self.pencolor = QtCore.Qt.darkGreen
            self.clearpaint = True
            self.update()
            self.repaint()

    def paintEvent(self, e):
        if self.clearpaint:
            return
        painter = QPainter(self)
        pen = painter.pen()
        penwidth = 12
        pen.setWidth(penwidth)
        pen.setColor(self.pencolor)
        painter.setPen(pen)
        # painter.setFont(QFont("Arial", 30))
        # painter.drawText(rect(), Qt.AlignCenter, "Qt")
        geom = self.geometry()
        # rect = QtCore.QRect(0, 0, self.width(), self.height())
        rect = QtCore.QRect(0, 0, geom.width() - geom.x(), geom.height() - geom.y())
        painter.drawRect(rect)
        print(self.geometry())
        print(rect)
        painter.end()

def main():
    app = QtWidgets.QApplication(sys.argv)
    dw = app.desktop()
    # ex = BlinkYourEyesWidget(dw.availableGeometry())
    # ex = BlinkYourEyesWidget(dw.geometry())
    ex = BlinkYourEyesWidget(dw.availableGeometry(dw.screen(dw.primaryScreen())))
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     w = QWidget()
#     dw = app.desktop()
# 
#     w.setGeometry(dw.availableGeometry())
#     # w.setAttribute(Qt.WA_ShowWithoutActivating, True)
#     # w.setWindowFlags(Qt.WindowTransparentForInput|Qt.FramelessWindowHint)
#     # w.setAttribute(Qt.WA_NoSystemBackground, True)
#     # w.setAttribute(Qt.WA_TranslucentBackground, True)
# 
#     # w.setAttribute(Qt.WA_ShowWithoutActivating, True)
#     # w.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowSystemMenuHint)
#     
#     # https://stackoverflow.com/questions/7667552/qt-widget-with-transparent-background
#     w.setAttribute(Qt.WA_TranslucentBackground, True)
#     w.setAttribute(Qt.WA_ShowWithoutActivating, True)
#     w.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput | Qt.WindowDoesNotAcceptFocus)
# 
#     #w.showFullScreen()
#     sys.exit(app.exec_())
