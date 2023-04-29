from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from qfluentwidgets import ScrollArea, ExpandLayout, SettingCardGroup, PushSettingCard
from qfluentwidgets import FluentIcon as FIF

from Config import cfg


class SettingWidget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.scroll_area = ScrollArea(self)
        self.scroll_widget = QWidget(self)
        self.expand_layout = ExpandLayout(self.scroll_widget)

        self.edit_setting_group = SettingCardGroup(
            self.tr("Music on this PC"), self.scroll_widget)
        self.reprint_id_card = PushSettingCard(
            self.tr('Choose folder'),
            FIF.DOWNLOAD,
            self.tr("Download directory"),
            cfg.get(cfg.reprint_id),
            self.edit_setting_group
        )

        self.setObjectName(text)
        self.init_layout()
        self.init_widget()

    def init_layout(self):
        self.edit_setting_group.addSettingCard(self.reprint_id_card)

        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(60, 10, 60, 0)
        self.expand_layout.addWidget(self.edit_setting_group)

    def init_widget(self):
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setViewportMargins(0, 120, 0, 20)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        self.layout.addWidget(self.scroll_area)

    def set_qss(self):
        self.scroll_widget.setObjectName('scroll_widget')

        with open(f'res/qss/light/setting_widget.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
