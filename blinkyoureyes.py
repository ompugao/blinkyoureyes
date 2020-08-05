#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "ompugao"

import sys
from PyQt5 import QtCore, QtWidgets, QtGui

class BlinkYourEyesWidget(QtWidgets.QWidget):

    def __init__(self, parent = None, widget = None):
        super(BlinkYourEyesWidget, self).__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)
        #self.setAttribute(Qt.Qt.WA_NoSystemBackground)
        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.8)

        #self.setFocusPolicy(QtCore.Qt.NoFocus)
        #self.setStyleSheet("background-color:transparent;")

        self.background_color = QtCore.Qt.black
        self.timer_count = 0
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100) #[milliseconds]
        self.timer.timeout.connect(self.timer_callback)

        self.initUI()
        self.timer.start()
        self.dragstartpos = None

    def initUI(self):
        screenrect = QtWidgets.QDesktopWidget().screenGeometry().getRect()
        width = screenrect[2] / 8 #170
        height = screenrect[3] / 8 #80
        self.setGeometry(screenrect[2] - width, 0, width, height) #screenrect[3] - height
        self.setWindowTitle('Blink Your Eyes')
        self.show()

    def mousePressEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.dragstartpos = event.pos()
            self.xy = [event.x, event.y]
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeAllCursor))

    def mouseMoveEvent(self, event):
        #self.move(event.x - self.xy[0], event.y - self.xy[1])
        if (self.dragstartpos is not None\
                and event.buttons() & QtCore.Qt.LeftButton):
                #and (event.pos() - self.dragstartpos).manhattanLength() > QtWidgets.qApp.startDragDistance()):
            event.pos() - self.dragstartpos
            pos = QtCore.QPoint(event.globalPos())
            self.window().move(pos - self.dragstartpos)
            #self.dragstart = None
            #drag = QtGui.QDrag(self)
            #drag.setMimeData(QtCore.QMimeData())
            #drag.exec_(QtCore.Qt.LinkAction)


    def mouseReleaseEvent(self, event):
        self.dragstartpos = None
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def timer_callback(self, ):
        self.timer_count = (self.timer_count + 1)%30 #3 seconds
        if self.timer_count == 0:
            self.background_color = QtCore.Qt.gray
            self.repaint()
        elif self.timer_count == 3:
            self.background_color = QtCore.Qt.black
            self.repaint()
        elif self.timer_count == 6:
            self.background_color = QtCore.Qt.gray
            self.repaint()
        elif self.timer_count == 9:
            self.background_color = QtCore.Qt.black
            self.repaint()

    def paintEvent(self, e):
        self.drawBackground()

    def drawBackground(self,):
        p = self.palette()
        p.setColor(self.backgroundRole(), self.background_color)
        self.setPalette(p)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = BlinkYourEyesWidget()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
