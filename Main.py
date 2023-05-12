import sys

from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QLabel, QFrame, QHBoxLayout, QStackedWidget
from qfluentwidgets import (NavigationInterface, NavigationItemPosition, setTheme, Theme, PopUpAniStackedWidget, FluentTranslator)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar

from common.Config import cfg, VERSION
from common.SignalBus import signal_bus
from view.DownloadInterface import DownloadInterface
from view.LocalVideoInterface import LocalVideoInterface
from view.SettingInterface import SettingInterface
from view.SubscribeInterface import SubscribeInterface


class Window(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))

        setTheme(Theme.LIGHT)

        self.h_box_layout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)
        self.navigation_interface = NavigationInterface(self, showMenuButton=True, showReturnButton=False)
        self.stack_widget = QStackedWidget(self)  # 多窗口控件

        self.download_interface = DownloadInterface('edit_interface', self)
        self.local_video_interface = LocalVideoInterface('local_video_interface', self)
        self.subscribe_interface = SubscribeInterface('subscribe_interface', self)
        self.todo_list_interface = Widget('todo_list_interface', self)
        self.info_interface = Widget('info_interface', self)
        self.setting_interface = SettingInterface('setting_interface', self)

        self.stack_widget.addWidget(self.download_interface)
        self.stack_widget.addWidget(self.local_video_interface)
        self.stack_widget.addWidget(self.subscribe_interface)
        self.stack_widget.addWidget(self.todo_list_interface)
        self.stack_widget.addWidget(self.info_interface)
        self.stack_widget.addWidget(self.setting_interface)

        # initialize layout
        self.init_layout()

        # add items to navigation interface
        self.init_navigation()

        self.init_window()
        self.connect_signal()

    def init_layout(self):
        self.h_box_layout.setSpacing(0)
        self.h_box_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.h_box_layout.addWidget(self.navigation_interface)
        self.h_box_layout.addWidget(self.stack_widget)
        self.h_box_layout.setStretchFactor(self.stack_widget, 1)  # 缩放因子

    def init_navigation(self):
        self.navigation_interface.addItem(routeKey=self.download_interface.objectName(), icon=FIF.EDIT,
                                          text=self.tr('Download'),
                                          onClick=lambda: self.switch_to(self.download_interface))
        self.navigation_interface.addItem(routeKey=self.local_video_interface.objectName(), icon=FIF.HISTORY,
                                          text=self.tr('Local Video'),
                                          onClick=lambda: self.switch_to(self.local_video_interface),
                                          position=NavigationItemPosition.SCROLL)
        self.navigation_interface.addItem(routeKey=self.subscribe_interface.objectName(), icon=FIF.RINGER,
                                          text=self.tr('Subscription Information'),
                                          onClick=lambda: self.switch_to(self.subscribe_interface),
                                          position=NavigationItemPosition.SCROLL)
        self.navigation_interface.addItem(routeKey=self.todo_list_interface.objectName(), icon=FIF.FEEDBACK,
                                          text=self.tr('TODO List'),
                                          onClick=lambda: self.switch_to(self.todo_list_interface),
                                          position=NavigationItemPosition.SCROLL)

        self.navigation_interface.addSeparator()

        self.navigation_interface.addItem(routeKey=self.info_interface.objectName(), icon=FIF.INFO,
                                          text=self.tr('Info'),
                                          onClick=lambda: self.switch_to(self.info_interface),
                                          position=NavigationItemPosition.BOTTOM)
        self.navigation_interface.addItem(routeKey=self.setting_interface.objectName(), icon=FIF.SETTING,
                                          text=self.tr('Setting'),
                                          onClick=lambda: self.switch_to(self.setting_interface),
                                          position=NavigationItemPosition.BOTTOM)

        self.navigation_interface.setExpandWidth(200)

        self.stack_widget.currentChanged.connect(self.on_current_interface_changed)
        self.stack_widget.setCurrentIndex(0)

    def init_window(self):
        self.resize(650, 750)
        self.setWindowIcon(QIcon('res/icons/logo.ico'))
        self.setWindowTitle('YoutubeDownloader V' + VERSION)
        self.titleBar.setAttribute(Qt.WA_StyledBackground)  # 允许使用样式表定义背景

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.set_qss()

    def connect_signal(self):
        signal_bus.path2_download_signal.connect(self.local2_download)
        signal_bus.url2_download_signal.connect(self.url2_download)

    def set_qss(self):
        with open(f'res/qss/light/main.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def local2_download(self, path):
        self.download_interface.update_ui(path)
        self.switch_to(self.download_interface)

    def url2_download(self, url):
        self.download_interface.set_url(url)
        self.switch_to(self.download_interface)

    def switch_to(self, widget):
        self.stack_widget.setCurrentWidget(widget)

    def on_current_interface_changed(self, index):
        widget = self.stack_widget.widget(index)
        self.navigation_interface.setCurrentItem(widget.objectName())


class Widget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    # internationalization
    locale = cfg.get(cfg.language).value
    fluentTranslator = FluentTranslator(locale)
    settingTranslator = QTranslator()
    settingTranslator.load(locale, '', '', 'res/lang')

    app.installTranslator(fluentTranslator)
    app.installTranslator(settingTranslator)

    w = Window()
    w.show()
    app.exec_()
