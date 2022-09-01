# -*- coding: utf-8 -*-
import sys
import os
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QPainter, QPixmap, QIcon
import platform
import functools
import weakref
from ewmh import EWMH


def retrieve_asset(name, dir='assets'):
    if getattr(sys, 'frozen', False):
        # print('sys.frozen:', sys.frozen)
        # print('sys.executable:', sys.executable)
        # print('sys._MEIPASS:', sys._MEIPASS)

        folder_of_executable = os.path.dirname(sys.executable)
        if os.path.samefile(folder_of_executable, sys._MEIPASS):
            base_path = os.path.dirname(folder_of_executable)
        else:
            base_path = folder_of_executable

        assets_path = os.path.join(sys._MEIPASS, dir)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(base_path, dir)
    return os.path.join(assets_path, name)

class BlinkYourEyesWidget(QtWidgets.QWidget):

    def __init__(self, availablegeom, timer_count_ref, name = '', parent = None, widget = None):
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
        self.geom = availablegeom
        self.name = name
        # print(availablegeom)
        # self.setGeometry(QtCore.QRect(0, 0, 1920, 1080))
        # self.showFullScreen()
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        # self.setWindowOpacity(1.0)
        # self.setStyleSheet("QWidget{background: #000000}")
        # self.setStyleSheet("background: transparent;")

        #self.setFocusPolicy(QtCore.Qt.NoFocus)
        #self.setStyleSheet("background-color:transparent;")
        self.timer_count = timer_count_ref
        self.clearpaint = False
        self.pencolor = QtCore.Qt.darkGreen

        # self.show()
        self.show()

        if platform.system() == 'Linux':
            self.ewmh = EWMH()
            while True:
                import Xlib.error
                try:
                    all_wins = self.ewmh.getClientList()
                    wins = filter(lambda w: 'blinkyoureyes' in w.get_wm_class()[1], all_wins)
                    for w in wins:
                        self.ewmh.setWmDesktop(w, 0xffffffff)
                    self.ewmh.display.flush()
                    break
                except Xlib.error.BadWindow as e:
                    time.sleep(0.1)


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
        if self.timer_count.count == 0:
            self.pencolor = QtCore.Qt.green
            # self.pencolor = QtCore.Qt.darkGreen
            self.clearpaint = False
            self.repaint()
        elif self.timer_count.count == 3:
            #self.pencolor = QtCore.Qt.darkGreen
            self.clearpaint = True
            self.update()
            self.repaint()
        elif self.timer_count.count == 6:
            self.pencolor = QtCore.Qt.green
            # self.pencolor = QtCore.Qt.darkGreen
            self.clearpaint = False
            self.repaint()
        elif self.timer_count.count == 9:
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
        if geom.y() < 100:  # TODO: heuristic to handle the height of gnome3 system tray bar
            rect = QtCore.QRect(0, 0, geom.width(), geom.height() - geom.y())
        else:
            rect = QtCore.QRect(0, 0, geom.width(), geom.height())
        painter.drawRect(rect)
        print(self.name, self.frameGeometry(), self.geometry(), rect)
        painter.end()

def main():
    app = QtWidgets.QApplication(sys.argv)
    dw = app.desktop()

    # ex = BlinkYourEyesWidget(dw.availableGeometry())
    # ex = BlinkYourEyesWidget(dw.geometry())
    # w = BlinkYourEyesWidget(dw.availableGeometry(dw.primaryScreen()))
    widgets = {}

    timer = QtCore.QTimer()
    class TimerCount(object):
        def __init__(self, ):
            self.count = 0
        def _update(self,):
            self.count = (self.count + 1)%30  # 1 seconds

    timer_count = TimerCount()
    timer.setInterval(100)  # [milliseconds]
    # def _update_count():
        # timer_count = (timer_count + 1)%30 #1 seconds
    timer.timeout.connect(timer_count._update)

    for i in range(dw.screenCount()):
        w = BlinkYourEyesWidget(dw.availableGeometry(dw.screen(i)),
                                weakref.proxy(timer_count),
                                'ex%s'%dw.screen(i).screen().serialNumber())
        timer.timeout.connect(w.timer_callback)
        widgets[dw.screen(i).screen()] = w

    # def create(screen):
    #     widgets[screen] = BlinkYourEyesWidget(screen.availableGeometry(),
    #                           weakref.proxy(timer_count),
    #                           'ex%s'%screen.serialNumber())
    #     for w in widgets.values():
    #         w.timer.stop()
    #     for w in widgets.values():
    #         w.timer.start()  # restart
    # def delete(screen):
    #     widgets.pop(screen, None)
    # app.screenAdded.connect(create)
    # app.screenRemoved.connect(delete)

    timer.start()

    # systray
    icon = QIcon(retrieve_asset("icon.png"))
    # Adding item on the menu bar
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)
    # Creating the options
    menu = QMenu()
    quit = QAction("Quit")
    quit.triggered.connect(app.quit)
    menu.addAction(quit)
    # Adding options to the System Tray
    tray.setContextMenu(menu)

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
