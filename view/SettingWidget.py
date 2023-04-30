from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy, QLabel
from qfluentwidgets import ScrollArea, ExpandLayout, SettingCardGroup, PushSettingCard, SwitchSettingCard
from qfluentwidgets import FluentIcon as FIF

from Config import cfg
from view.MySettingCard import RangeSettingCard


class SettingWidget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.scroll_area = ScrollArea(self)
        self.scroll_widget = QWidget(self)
        self.expand_layout = ExpandLayout(self.scroll_widget)

        self.title_label = QLabel(self.tr("Settings"), self)

        self.edit_setting_group = SettingCardGroup(
            self.tr('Edit Setting'), self.scroll_widget)
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

        self.setObjectName(text)
        self.init_layout()
        self.init_widget()

    def init_layout(self):
        self.title_label.setAlignment(Qt.AlignCenter)
        self.edit_setting_group.addSettingCard(self.reprint_id_card)
        self.edit_setting_group.addSettingCard(self.proxy_enable)
        self.edit_setting_group.addSettingCard(self.proxy_card)
        self.edit_setting_group.addSettingCard(self.thread_card)
        self.edit_setting_group.addSettingCard(self.download_folder_card)

        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(20, 10, 20, 0)
        self.expand_layout.addWidget(self.edit_setting_group)

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
