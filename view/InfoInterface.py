from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QLabel, QSizePolicy
from qfluentwidgets import ScrollArea, ExpandLayout, TextEdit

from common.Config import LICENCE_PATH


class InfoInterface(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.scroll_area = ScrollArea(self)
        self.scroll_widget = QWidget(self)
        self.expand_layout = ExpandLayout(self.scroll_widget)

        self.title_label = QLabel(self.tr("About"), self)
        self.about_text = QLabel('', self.scroll_widget)

        self.setObjectName(text)
        self.init_layout()
        self.init_widget()

    def init_layout(self):
        self.title_label.setAlignment(Qt.AlignCenter)

        self.about_text.setFixedHeight(500)

        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(20, 10, 20, 0)
        self.expand_layout.addWidget(self.about_text)

    def init_widget(self):
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setViewportMargins(0, 10, 0, 20)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        f = open(LICENCE_PATH, mode='r', encoding='utf8')
        text = f.read()
        self.about_text.setText(text)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.scroll_area)

        self.set_qss()

    def set_qss(self):
        self.title_label.setObjectName('Title')
        self.scroll_widget.setObjectName('ScrollWidget')

        with open(f'res/qss/light/scroll_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())