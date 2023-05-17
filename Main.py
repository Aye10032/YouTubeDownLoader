import os
import sys

from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QLabel, QFrame, QHBoxLayout, QStackedWidget
from qfluentwidgets import (NavigationInterface, NavigationItemPosition, setTheme, Theme, PopUpAniStackedWidget,
                            FluentTranslator, Dialog, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar

from Path import BASE_DIR
from common.Config import cfg, VERSION, LOG_PATH, LOG_NAME
from common.SignalBus import signal_bus
from common.Style import StyleSheet
from view.DownloadInterface import DownloadInterface
from view.InfoInterface import InfoInterface
from view.LocalVideoInterface import LocalVideoInterface
from view.SettingInterface import SettingInterface
from view.SubscribeInterface import SubscribeInterface
from view.TodoListInterface import TodoListInterface
from view.UploadInterface import UploadInterface


class Window(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))

        setTheme(Theme.LIGHT)

        self.h_box_layout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)
        self.navigation_interface = NavigationInterface(self, showMenuButton=True, showReturnButton=False)
        self.stack_widget = QStackedWidget(self)

        self.download_interface = DownloadInterface('edit_interface', self)
        self.upload_interface = UploadInterface('upload_interface', self)
        self.local_video_interface = LocalVideoInterface('local_video_interface', self)
        self.subscribe_interface = SubscribeInterface('subscribe_interface', self)
        self.todo_list_interface = TodoListInterface('todo_list_interface', self)
        self.info_interface = InfoInterface('info_interface', self)
        self.setting_interface = SettingInterface('setting_interface', self)

        self.stack_widget.addWidget(self.download_interface)
        self.stack_widget.addWidget(self.upload_interface)
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
        self.navigation_interface.addItem(routeKey=self.upload_interface.objectName(), icon=FIF.SEND,
                                          text=self.tr('Upload'),
                                          onClick=lambda: self.switch_to(self.upload_interface))
        self.navigation_interface.addItem(routeKey=self.local_video_interface.objectName(), icon=FIF.HISTORY,
                                          text=self.tr('Local Video'),
                                          onClick=lambda: self.switch_to(self.local_video_interface),
                                          position=NavigationItemPosition.SCROLL)
        self.navigation_interface.addItem(routeKey=self.subscribe_interface.objectName(), icon=FIF.RINGER,
                                          text=self.tr('Subscription Information'),
                                          onClick=self.switch_to_subscribe,
                                          position=NavigationItemPosition.SCROLL)
        self.navigation_interface.addItem(routeKey=self.todo_list_interface.objectName(), icon=FIF.FEEDBACK,
                                          text=self.tr('TODO List'),
                                          onClick=self.switch_to_todo,
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
        self.setWindowIcon(QIcon(f'{BASE_DIR}/res/icons/logo.ico'))
        self.setWindowTitle('YoutubeDownloader V' + VERSION)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.navigation_interface.displayModeChanged.connect(
            self.titleBar.raise_)
        self.titleBar.raise_()

        self.set_qss()

    def connect_signal(self):
        signal_bus.path2_download_signal.connect(self.local2_download)
        signal_bus.url2_download_signal.connect(self.url2_download)
        signal_bus.path2_upload_signal.connect(self.path2_upload)

    def set_qss(self):
        StyleSheet.MAIN_WINDOW.apply(self)

    def local2_download(self, path):
        self.download_interface.update_ui(path)
        self.switch_to(self.download_interface)

    def url2_download(self, url):
        self.download_interface.set_url(url)
        self.switch_to(self.download_interface)

    def path2_upload(self, path):
        self.upload_interface.init_text(path)
        self.switch_to(self.upload_interface)

    def switch_to(self, widget):
        self.stack_widget.setCurrentWidget(widget)

    def switch_to_subscribe(self):
        if cfg.get(cfg.api_token) == '':
            dialog = Dialog(
                self.tr('No API Token!'),
                self.tr('You haven\'t set your token yet, please go to the settings screen to set it first'),
                self.window())
            dialog.setTitleBarVisible(False)
            if dialog.exec():
                self.switch_to(self.setting_interface)
        else:
            self.switch_to(self.subscribe_interface)

    def switch_to_todo(self):
        if cfg.get(cfg.api_server) == '':
            dialog = Dialog(
                self.tr('No API Server!'),
                self.tr('You haven\'t set api server yet, please go to the settings screen to set it first'),
                self.window())
            dialog.setTitleBarVisible(False)
            if dialog.exec():
                self.switch_to(self.setting_interface)
        else:
            self.switch_to(self.todo_list_interface)

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


class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'a', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.terminal.flush()
        self.log.write(message)
        self.log.flush()

    def debug(self, message):
        self.terminal.write('[debug]' + message + '\n')
        self.terminal.flush()
        self.log.write('[debug]' + message + '\n')
        self.log.flush()

    def warning(self, message):
        self.terminal.write('[warning]' + message + '\n')
        self.terminal.flush()
        self.log.write('[warning]' + message + '\n')
        self.log.flush()

    def error(self, message):
        self.terminal.write('[error]' + message + '\n')
        self.terminal.flush()
        self.log.write('[error]' + message + '\n')
        self.log.flush()

    def isatty(self):
        return False

    def flush(self):
        pass


if __name__ == '__main__':
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

    sys.stdout = Logger(LOG_PATH + '/' + LOG_NAME + '.log', sys.stdout)
    sys.stderr = Logger(LOG_PATH + '/' + LOG_NAME + '.log', sys.stderr)

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    # internationalization
    locale = cfg.get(cfg.language).value
    fluentTranslator = FluentTranslator(locale)
    settingTranslator = QTranslator()
    settingTranslator.load(locale, '', '', f'{BASE_DIR}/res/lang')

    app.installTranslator(fluentTranslator)
    app.installTranslator(settingTranslator)

    w = Window()
    w.show()
    app.exec_()
