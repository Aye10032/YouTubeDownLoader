from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QLabel
from qfluentwidgets import ScrollArea, ExpandLayout


class LocalVideoInterface(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.scroll_area = ScrollArea(self)
        self.scroll_widget = QWidget(self)
        self.expand_layout = ExpandLayout(self.scroll_widget)

        self.title_label = QLabel(self.tr("Download List"), self)

        self.setObjectName(text)
        self.init_layout()
        self.init_widget()
        self.connect_signal()

    def init_layout(self):
        self.title_label.setAlignment(Qt.AlignCenter)

        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(20, 10, 20, 0)
        # self.expand_layout.addWidget(self.edit_setting_group)
        # self.expand_layout.addWidget(self.system_setting_group)

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

        with open(f'res/qss/light/local_video_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def connect_signal(self):
        pass


