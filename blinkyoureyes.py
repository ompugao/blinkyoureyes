#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "ompugao"

import sys
from PyQt5 import QtCore, QtWidgets, QtGui

from enum import Enum

class DragMode(Enum):
    MOVE = 1
    RESIZEX = 2
    RESIZEY = 3
    RESIZEDIAG = 4

class BlinkYourEyesWidget(QtWidgets.QWidget):

    def __init__(self, parent = None, widget = None):
        super(BlinkYourEyesWidget, self).__init__()
        # Avoid this window appearing from alt-tab window selection
        # see the followings:
        # https://stackoverflow.com/questions/3553428/how-can-i-prevent-gnome-from-showing-two-windows-when-doing-alt-tab-c-qt-app
        # https://doc.qt.io/qt-5/qt.html#WindowType-enum
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint
                |QtCore.Qt.Tool)
        #self.setAttribute(Qt.Qt.WA_NoSystemBackground)
        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.8)

        #self.setFocusPolicy(QtCore.Qt.NoFocus)
        #self.setStyleSheet("background-color:transparent;")

        self.background_color = QtCore.Qt.black
        self.timer_count = 0
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)  # [milliseconds]
        self.timer.timeout.connect(self.timer_callback)

        self.initUI()
        self.timer.start()

        self.dragmode = None
        self.dragstartpos = None
        self.dragstartgeom = None

    def initUI(self):
        screenrect = QtWidgets.QDesktopWidget().screenGeometry().getRect()
        width = int(screenrect[2] / 8)  # 170
        height = int(screenrect[3] / 8)  # 80
        self.setGeometry(screenrect[2] - width, screenrect[3] - height, width, height)  # screenrect[3] - height or 0
        self.setWindowTitle('Blink Your Eyes')
        self.show()

    def mousePressEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            geom = self.geometry()
            self.dragstartpos = event.pos()  # in window
            self.dragstartgeom = self.geometry()

            on_edge_x = geom.width()*3/4 < event.x() < geom.width()
            on_edge_y = geom.height()*3/4 < event.y() < geom.height()
            if on_edge_x and on_edge_y:
                self.dragmode = DragMode.RESIZEDIAG
                self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
            elif on_edge_x and not on_edge_y:
                self.dragmode = DragMode.RESIZEX
                self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            elif not on_edge_x and on_edge_y:
                self.dragmode = DragMode.RESIZEY
                self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
            else:
                self.dragmode = DragMode.MOVE
                self.setCursor(QtGui.QCursor(QtCore.Qt.SizeAllCursor))

    def mouseMoveEvent(self, event):
        if (self.dragstartpos is not None\
                and event.buttons() & QtCore.Qt.LeftButton):
                #and (event.pos() - self.dragstartpos).manhattanLength() > QtWidgets.qApp.startDragDistance()):

            geom = self.dragstartgeom
            pointerpos = QtCore.QPoint(event.globalPos())
            neworiginpos = pointerpos - self.dragstartpos
            diff = event.pos() - self.dragstartpos
            minsize = 100
            newwidth = max(minsize, geom.width() + diff.x())
            newheight = max(minsize, geom.height() + diff.y())
            # print('----')
            # print(self.dragstartpos)
            # print(diff)
            # print(neworiginpos.x(), neworiginpos.y())
            if self.dragmode is DragMode.RESIZEDIAG:
                self.setGeometry(geom.x(), geom.y(), newwidth, newheight)
            elif self.dragmode is DragMode.RESIZEX:
                self.setGeometry(geom.x(), geom.y(), newwidth, geom.height())
            elif self.dragmode is DragMode.RESIZEY:
                self.setGeometry(geom.x(), geom.y(), geom.width(), newheight)
            else:
                # self.dragmode = DragMode.MOVE
                self.window().move(neworiginpos)
            #self.dragstart = None
            #drag = QtGui.QDrag(self)
            #drag.setMimeData(QtCore.QMimeData())
            #drag.exec_(QtCore.Qt.LinkAction)

    def mouseReleaseEvent(self, event):
        self.dragstartpos = None
        self.dragmode = None
        self.dragstartgeom = None
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
