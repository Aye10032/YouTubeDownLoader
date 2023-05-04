from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QWidget, QVBoxLayout, QLabel, QFileDialog
from qfluentwidgets import ScrollArea, ExpandLayout, SettingCardGroup, PushSettingCard, SwitchSettingCard, Dialog, \
    ComboBoxSettingCard, InfoBar
from qfluentwidgets import FluentIcon as FIF

from Config import cfg
from view.MyWidget import RangeSettingCard, TextDialog


class SettingWidget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.scroll_area = ScrollArea(self)
        self.scroll_widget = QWidget(self)
        self.expand_layout = ExpandLayout(self.scroll_widget)

        self.title_label = QLabel(self.tr("Settings"), self)

        self.edit_setting_group = SettingCardGroup(
            self.tr('Download Setting'), self.scroll_widget)
        self.reprint_id_card = PushSettingCard(
            self.tr('Edit'),
            FIF.DOWNLOAD,
            self.tr('Reprinter ID'),
            cfg.get(cfg.reprint_id),
            self.edit_setting_group
        )
        self.proxy_enable = SwitchSettingCard(
            FIF.GLOBE,
            self.tr("Enable Proxy"),
            self.tr("Whether to enable web proxy"),
            configItem=cfg.proxy_enable,
            parent=self.edit_setting_group
        )
        self.proxy_card = PushSettingCard(
            self.tr('Edit'),
            FIF.GLOBE,
            self.tr('Proxy Setting'),
            cfg.get(cfg.proxy),
            self.edit_setting_group
        )
        self.thread_card = RangeSettingCard(
            cfg.thread,
            QIcon(f'res/icons/number.svg'),
            self.tr('Number of threads'),
            parent=self.edit_setting_group
        )
        self.download_folder_card = PushSettingCard(
            self.tr('Choose folder'),
            FIF.FOLDER_ADD,
            self.tr("Download directory"),
            cfg.get(cfg.download_folder),
            self.edit_setting_group
        )

        self.system_setting_group = SettingCardGroup(
            self.tr('System Setting'), self.scroll_widget)
        self.language_card = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', 'English', self.tr('Use system setting')],
            parent=self.system_setting_group
        )

        self.setObjectName(text)
        self.init_layout()
        self.init_widget()
        self.connect_signal()

    def init_layout(self):
        self.title_label.setAlignment(Qt.AlignCenter)
        self.edit_setting_group.addSettingCard(self.reprint_id_card)
        self.edit_setting_group.addSettingCard(self.proxy_enable)
        self.edit_setting_group.addSettingCard(self.proxy_card)
        self.edit_setting_group.addSettingCard(self.thread_card)
        self.edit_setting_group.addSettingCard(self.download_folder_card)

        self.system_setting_group.addSettingCard(self.language_card)

        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(20, 10, 20, 0)
        self.expand_layout.addWidget(self.edit_setting_group)
        self.expand_layout.addWidget(self.system_setting_group)

    def init_widget(self):
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setViewportMargins(0, 10, 0, 20)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.scroll_area)

        self.set_qss()

    def set_qss(self):
        self.title_label.setObjectName('Title')
        self.scroll_widget.setObjectName('ScrollWidget')

        with open(f'res/qss/light/setting_widget.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def connect_signal(self):
        cfg.appRestartSig.connect(self.show_restart_tooltip)

        self.reprint_id_card.clicked.connect(
            self.on_reprint_id_card_clicked
        )
        self.download_folder_card.clicked.connect(
            self.on_download_folder_card_clicked
        )
        self.proxy_card.clicked.connect(
            self.on_proxy_card_clicked
        )

    def show_restart_tooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def on_reprint_id_card_clicked(self):
        w = TextDialog(self.tr('Nick Name'), self.tr('please input your nick name:'), cfg.get(cfg.reprint_id), self)
        w.setTitleBarVisible(False)
        if w.exec():
            cfg.set(cfg.reprint_id, w.input_edit.text())
            self.reprint_id_card.setContent(w.input_edit.text())
        else:
            print('Cancel button is pressed')

    def on_proxy_card_clicked(self):
        w = TextDialog(self.tr('Proxy Setting'), self.tr('manual proxy configuration:'), cfg.get(cfg.proxy), self)
        w.setTitleBarVisible(False)
        if w.exec():
            cfg.set(cfg.proxy, w.input_edit.text())
            self.proxy_card.setContent(w.input_edit.text())
        else:
            print('Cancel button is pressed')

    def on_download_folder_card_clicked(self):
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.download_folder) == folder:
            return

        print(folder)
        cfg.set(cfg.download_folder, folder)
        self.download_folder_card.setContent(folder)
