import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QLabel, QFrame, QHBoxLayout, QStackedWidget
from qfluentwidgets import (NavigationInterface, NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar


class Widget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class Window(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))

        setTheme(Theme.LIGHT)

        self.h_box_layout = QHBoxLayout(self)
        self.navigation_interface = NavigationInterface(self, showMenuButton=True, showReturnButton=False)
        self.stack_widget = QStackedWidget(self)  # 多窗口控件

        self.search_interface = Widget('search_interface', self)
        self.music_interface = Widget('music_interface', self)
        self.video_interface = Widget('video_interface', self)
        self.setting_interface = Widget('setting_interface', self)

        self.stack_widget.addWidget(self.search_interface)
        self.stack_widget.addWidget(self.music_interface)
        self.stack_widget.addWidget(self.video_interface)
        self.stack_widget.addWidget(self.setting_interface)

        # initialize layout
        self.init_layout()

        # add items to navigation interface
        self.init_navigation()

        self.init_window()

    def init_layout(self):
        self.h_box_layout.setSpacing(0)
        self.h_box_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.h_box_layout.addWidget(self.navigation_interface)
        self.h_box_layout.addWidget(self.stack_widget)
        self.h_box_layout.setStretchFactor(self.stack_widget, 1)  # 缩放因子

    def init_navigation(self):
        self.navigation_interface.addItem(routeKey=self.search_interface.objectName(), icon=FIF.SEARCH, text='Search',
                                          onClick=lambda: self.switch_to(self.search_interface))
        self.navigation_interface.addItem(routeKey=self.music_interface.objectName(), icon=FIF.MUSIC, text='Music',
                                          onClick=lambda: self.switch_to(self.music_interface))
        self.navigation_interface.addItem(routeKey=self.video_interface.objectName(), icon=FIF.VIDEO, text='Video',
                                          onClick=lambda: self.switch_to(self.video_interface))

        self.navigation_interface.addSeparator()

        self.navigation_interface.addItem(routeKey=self.setting_interface.objectName(), icon=FIF.SETTING,
                                          text='Setting',
                                          onClick=lambda: self.switch_to(self.setting_interface),
                                          position=NavigationItemPosition.BOTTOM)

        self.stack_widget.currentChanged.connect(self.on_current_interface_changed)
        self.stack_widget.setCurrentIndex(1)

    def init_window(self):
        self.resize(1008, 700)
        self.setWindowIcon(QIcon('res/logo.ico'))
        self.setWindowTitle('YoutubeDownloader')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)  # 允许使用样式表定义背景

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.set_qss()

    def set_qss(self):
        pass

    def switch_to(self, widget):
        self.stack_widget.setCurrentWidget(widget)

    def on_current_interface_changed(self, index):
        widget = self.stack_widget.widget(index)
        self.navigation_interface.setCurrentItem(widget.objectName())


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
