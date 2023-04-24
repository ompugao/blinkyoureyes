# -*- coding: utf-8 -*-
import sys
import os
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu, QColorDialog, QWidgetAction, QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QSlider, QCheckBox
from PyQt6.QtGui import QAction, QPainter, QPixmap, QIcon, QColor

from pyqt_colorpicker_widget.PyQt6.colorpicker import ColorPicker

import platform
import functools
import weakref
from ewmh import EWMH
import time


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

def _convert_blink_speed(v):
    # TODO do not linearly interpolate
    return int(600 - (v - 1) * 300.0 / 9)

class BlinkYourEyesWidget(QtWidgets.QWidget):

    def __init__(self, availablegeom, timer_count_ref, name = '', parent = None, widget = None,
                 pencolor = 'green', penwidth = 6, bdrawcross = False, isprimaryscreen = False):
        super(BlinkYourEyesWidget, self).__init__()
        # Avoid this window appearing from alt-tab window selection
        # see the followings:
        # https://stackoverflow.com/questions/3553428/how-can-i-prevent-gnome-from-showing-two-windows-when-doing-alt-tab-c-qt-app
        # https://doc.qt.io/qt-5/qt.html#WindowType-enum
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint|QtCore.Qt.Tool)

        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        # self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput | Qt.WindowDoesNotAcceptFocus)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint  | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowTransparentForInput | Qt.WindowType.WindowDoesNotAcceptFocus)
        if isprimaryscreen and platform.system() == 'Linux':
            # TODO available screen is wrong in gnome
            h = availablegeom.height() - 30
            self.geom = QtCore.QRect(availablegeom.x(), availablegeom.y(), availablegeom.width(), h)
            self.setGeometry(self.geom)
        else:
            self.setGeometry(availablegeom)
            self.geom = availablegeom
        print(self.geom)
        self.name = name
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.timer_count = timer_count_ref
        self.clearpaint = False
        self.pencolor = pencolor
        self.penwidth = penwidth
        self.bdrawcross = bdrawcross

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
                except Exception as e:
                    break



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
            self.clearpaint = False
            self.repaint()
        elif self.timer_count.count == 1:
            self.clearpaint = True
            self.update()
            self.repaint()
        elif self.timer_count.count == 2:
            self.clearpaint = False
            self.repaint()
        elif self.timer_count.count == 3:
            self.clearpaint = True
            self.update()
            self.repaint()

    def set_pencolor(self, color):
        self.pencolor = color

    def set_penwidth(self, width):
        self.penwidth = width

    def set_drawcross(self, bdrawcross: bool):
        self.bdrawcross = bdrawcross


    def paintEvent(self, e):
        if self.clearpaint:
            return
        painter = QPainter(self)
        pen = painter.pen()
        pen.setWidth(self.penwidth)
        pen.setColor(self.pencolor)
        painter.setPen(pen)
        # painter.setFont(QFont("Arial", 30))
        # painter.drawText(rect(), Qt.AlignCenter, "Qt")
        geom = self.geometry()
        # TODO: heuristic to handle the height of gnome3 system tray bar
        # if 1 < geom.y() < 100:
        #     rect = QtCore.QRect(0, 0, geom.width(), geom.height() - geom.y())
        # else:
        #    rect = QtCore.QRect(0, 0, geom.width(), geom.height())
        rect = QtCore.QRect(0, 0, geom.width(), geom.height())
        painter.drawRect(rect)
        # print(self.name, self.frameGeometry(), self.geometry(), rect)


        if self.bdrawcross:
            pen.setWidth(max(int(self.penwidth/4), 1))
            pen.setColor(self.pencolor)
            painter.setPen(pen)
            halfcrosssize = max(int(geom.height() / 80), 1)
            painter.drawLine(QtCore.QPoint(int(geom.width()/2) - halfcrosssize, int(geom.height()/2)),
                             QtCore.QPoint(int(geom.width()/2) + halfcrosssize, int(geom.height()/2)))
            painter.drawLine(QtCore.QPoint(int(geom.width()/2), int(geom.height()/2) - halfcrosssize),
                             QtCore.QPoint(int(geom.width()/2), int(geom.height()/2) + halfcrosssize))
        painter.end()

def load_settings():
    settings = QSettings('blinkyoureyes', 'configs')
    pencolor = settings.value('pencolor', defaultValue=QColor('green'), type=QColor)
    penwidth = settings.value('penwidth', defaultValue=6, type=int)
    blinkspeed = settings.value('blinkspeed', defaultValue=1, type=int)
    drawcross = settings.value('drawcross', defaultValue=False, type=bool)
    return dict(pencolor=pencolor, penwidth=penwidth, blinkspeed=blinkspeed, drawcross=drawcross)

def save_settings(color, width, blinkspeed, drawcross):
    settings = QSettings('blinkyoureyes', 'configs')
    settings.setValue('pencolor', color)
    settings.setValue('penwidth', width)
    settings.setValue('blinkspeed', blinkspeed)
    settings.setValue('drawcross', drawcross)
    del settings

class SettingsDialog(QDialog):
    def __init__(self, widgets, timer):
        super().__init__()

        self.setWindowTitle("BlinkYourEyes Settings")

        QBtn = QDialogButtonBox.StandardButton.Save  | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.save)
        self.buttonBox.rejected.connect(self.cancel)

        self.layout = QVBoxLayout()

        current_settings = load_settings()

        self.colorpicker = ColorPicker(self, rgb=(
            current_settings['pencolor'].red(),
            current_settings['pencolor'].green(),
            current_settings['pencolor'].blue()))

        self.slider = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setTickInterval(1)
        self.slider.setMinimum(1)
        self.slider.setMaximum(64)
        self.slider.setSingleStep(1)
        self.slider.setSliderPosition(current_settings['penwidth'])
        self.widthlabel = QLabel(str(current_settings['penwidth']))
        self.slider.valueChanged.connect(lambda value: self.widthlabel.setText(str(value)))

        self.blinkslider = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.blinkslider.setTickInterval(1)
        self.blinkslider.setMinimum(1)
        self.blinkslider.setMaximum(10)
        self.blinkslider.setSingleStep(1)
        self.blinkslider.setSliderPosition(current_settings['blinkspeed'])
        self.blinkspeedlabel = QLabel(str(current_settings['blinkspeed']))
        def _cb(value):
            self.blinkspeedlabel.setText(str(value))
            timer.setInterval(_convert_blink_speed(value))
        self.blinkslider.valueChanged.connect(_cb)
        self.blinkslider.valueChanged.connect(_cb)

        self.checkbox_drawcross = QCheckBox("draw center crosses?")
        self.checkbox_drawcross.setChecked(current_settings['drawcross'])

        for k, w in widgets.items():
            self.slider.valueChanged.connect(w.set_penwidth)
            self.colorpicker.colorChanged.connect(lambda:
                                                  w.set_pencolor(QColor.fromRgb(*map(int, self.colorpicker.getRGB()))))
            self.checkbox_drawcross.stateChanged.connect(lambda:
                                                         w.set_drawcross(self.checkbox_drawcross.isChecked()))

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.slider)
        hlayout.addWidget(self.widthlabel)

        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self.blinkslider)
        hlayout2.addWidget(self.blinkspeedlabel)

        self.layout.addWidget(QLabel("Select Width"))
        self.layout.addLayout(hlayout)
        self.layout.addWidget(QLabel("Select Color"))
        self.layout.addWidget(self.colorpicker)
        self.layout.addWidget(QLabel("Select Blinking Speed"))
        self.layout.addLayout(hlayout2)
        self.layout.addWidget(self.checkbox_drawcross)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def save(self,):
        color = QColor.fromRgb(*map(int, self.colorpicker.getRGB()))
        width = self.slider.value()
        blinkspeed = self.blinkslider.value()
        drawcross = self.checkbox_drawcross.isChecked()
        save_settings(color, width, blinkspeed, drawcross)
        self.close()

    def cancel(self,):
        self.close()

def open_settings_dialog(s, widgets, timer):
    dlg = SettingsDialog(widgets, timer)
    dlg.exec()

def main():
    configs = load_settings()
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # dw = app.desktop()
    # QtGui.QGuiApplication.primaryScreen().availableGeometry()
    screens = QtGui.QGuiApplication.screens()


    # ex = BlinkYourEyesWidget(dw.availableGeometry())
    # ex = BlinkYourEyesWidget(dw.geometry())
    # w = BlinkYourEyesWidget(dw.availableGeometry(dw.primaryScreen()))
    widgets = {}

    timer = QtCore.QTimer()
    class TimerCount(object):
        def __init__(self, ):
            self.count = 0
        def _update(self,):
            self.count = (self.count + 1)%10  # 1 seconds

    timer_count = TimerCount()
    timer.setInterval(_convert_blink_speed(configs['blinkspeed']))  # [milliseconds]
    timer.timeout.connect(timer_count._update)

    for i, screen in enumerate(screens):
        w = BlinkYourEyesWidget(screen.availableGeometry(),
                                weakref.proxy(timer_count),
                                'ex%s'%screen.serialNumber(),
                                pencolor=configs['pencolor'],
                                penwidth=configs['penwidth'],
                                bdrawcross=configs['drawcross'],
                                isprimaryscreen=(QtGui.QGuiApplication.primaryScreen() == screen))
        timer.timeout.connect(w.timer_callback)
        widgets[screen] = w

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
    tray = QSystemTrayIcon()
    tray.setIcon(QIcon(retrieve_asset("icon.png")))
    tray.setVisible(True)
    # Creating the options
    menu = QMenu()
    settingsaction = QAction('Settings')
    settingsaction.triggered.connect(lambda s: open_settings_dialog(s, widgets, weakref.proxy(timer)))
    menu.addAction(settingsaction)
    quit = QAction("Quit")
    quit.triggered.connect(app.quit)
    menu.addAction(quit)
    # Adding options to the System Tray
    tray.setContextMenu(menu)

    sys.exit(app.exec())

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
#     sys.exit(app.exec())

