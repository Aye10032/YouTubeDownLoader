from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel
from qfluentwidgets import TextEdit


class UploadInterface(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.main_layout = QGridLayout(self)
        self.title_label = QLabel(self.tr('Video Upload'), self)

        self.log_output = TextEdit(self)

        self.init_ui()
        self.setObjectName(text)

    def init_ui(self):
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(20, 5, 20, 5)
        for i in range(9):
            self.main_layout.setColumnStretch(i, 1)
            self.main_layout.setRowStretch(i, 0)
        self.main_layout.setRowStretch(6, 1)
        self.main_layout.setRowStretch(7, 1)
        self.main_layout.setRowStretch(8, 1)

        self.title_label.setMargin(10)
        self.main_layout.addWidget(self.title_label, 0, 0, 1, 9, Qt.AlignCenter)

        self.setLayout(self.main_layout)

        # self.init_text()
        self.set_qss()
        # self.connect_signal()

    def set_qss(self):
        self.title_label.setObjectName('Title')
        # self.origin_link_label.setObjectName('Text')
        # self.auto_quality_label.setObjectName('Text')
        # self.quality_label.setObjectName('Text')
        # self.video_title_label.setObjectName('Text')
        # self.reprint_info_label.setObjectName('Text')

        with open(f'res/qss/light/download_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
