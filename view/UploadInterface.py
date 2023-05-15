from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QGridLayout, QWidget, QSizePolicy, QHBoxLayout
from qfluentwidgets import TextEdit, ScrollArea, ExpandLayout, LineEdit, ToolButton, PushButton, PrimaryPushButton
from qfluentwidgets import FluentIcon as FIF

from common.MyWidget import UploadCard, VideoCardView


class UploadInterface(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.scroll_area = ScrollArea(self)
        self.scroll_widget = QWidget(self)
        self.expand_layout = ExpandLayout(self.scroll_widget)

        self.title_label = QLabel(self.tr("Settings"), self)

        self.video_title_label = QLabel(self.tr('Video Title'), self.scroll_widget)
        self.video_title_input = LineEdit(self.scroll_widget)

        self.cover_label = QLabel(self.tr('Cover'), self.scroll_widget)
        self.cover_path_label = QLabel('cover path', self.scroll_widget)
        self.cover_path_btn = ToolButton(FIF.FOLDER, self.scroll_widget)

        self.video_list_widget = QWidget(self.scroll_widget)
        self.h_video_layout = QHBoxLayout()
        self.video_label = QLabel(self.tr('Video'), self.scroll_widget)
        self.video_card_view = VideoCardView('', self.scroll_widget)
        self.add_video_btn = ToolButton(FIF.FOLDER_ADD, self.scroll_widget)
        self.video_list_widget.setLayout(self.h_video_layout)

        self.reprint_info_label = QLabel(self.tr('Reprint Info'), self.scroll_widget)
        self.reprint_info_input = LineEdit(self.scroll_widget)

        self.tag_label = QLabel(self.tr('Tag'), self.scroll_widget)
        self.tag_input = LineEdit(self.scroll_widget)

        self.video_description_label = QLabel(self.tr('Description'), self.scroll_widget)
        self.video_description_input = TextEdit(self.scroll_widget)

        self.upload_btn = PrimaryPushButton(self.tr('Upload'), self.scroll_widget, FIF.SEND)

        self.log_output = TextEdit(self)

        self.setObjectName(text)
        self.init_layout()
        self.init_widget()
        # self.connect_signal()

    def init_widget(self):
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setViewportMargins(0, 10, 0, 20)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        widget_1 = QWidget(self.scroll_widget)
        layout_1 = QHBoxLayout()
        layout_1.setContentsMargins(5, 0, 5, 0)
        layout_1.addWidget(self.video_title_label, stretch=1)
        layout_1.addWidget(self.video_title_input, stretch=6)
        widget_1.setLayout(layout_1)
        widget_1.setFixedHeight(35)
        self.expand_layout.addWidget(widget_1)

        widget_2 = QWidget(self.scroll_widget)
        layout_2 = QHBoxLayout()
        layout_2.setContentsMargins(5, 0, 5, 0)
        layout_2.addWidget(self.cover_label, stretch=1)
        layout_2.addWidget(self.cover_path_label, stretch=5)
        layout_2.addWidget(self.cover_path_btn, stretch=1)
        widget_2.setLayout(layout_2)
        widget_2.setFixedHeight(35)
        self.expand_layout.addWidget(widget_2)

        self.video_list_widget.setFixedHeight(35)
        self.expand_layout.addWidget(self.video_list_widget)

        # card = UploadCard('test', 'test', 'test', self.scroll_widget)
        # self.video_card_view.add_video_card(card)

        widget_3 = QWidget(self.scroll_widget)
        layout_3 = QHBoxLayout()
        layout_3.setContentsMargins(5, 0, 5, 0)
        layout_3.addWidget(self.reprint_info_label, stretch=1)
        layout_3.addWidget(self.reprint_info_input, stretch=6)
        widget_3.setLayout(layout_3)
        widget_3.setFixedHeight(35)
        self.expand_layout.addWidget(widget_3)

        widget_4 = QWidget(self.scroll_widget)
        layout_4 = QHBoxLayout()
        layout_4.setContentsMargins(5, 0, 5, 0)
        layout_4.addWidget(self.tag_label, stretch=1)
        layout_4.addWidget(self.tag_input, stretch=6)
        widget_4.setLayout(layout_4)
        widget_4.setFixedHeight(35)
        self.expand_layout.addWidget(widget_4)

        widget_5 = QWidget(self.scroll_widget)
        layout_5 = QHBoxLayout()
        layout_5.setContentsMargins(5, 0, 5, 0)
        layout_5.addWidget(self.video_description_label, stretch=1, alignment=Qt.AlignTop)
        layout_5.addWidget(self.video_description_input, stretch=6, alignment=Qt.AlignTop)
        self.video_description_input.setFixedHeight(240)
        widget_5.setLayout(layout_5)
        widget_5.setFixedHeight(250)
        self.expand_layout.addWidget(widget_5)

        widget_6 = QWidget(self.scroll_widget)
        layout_6 = QHBoxLayout()
        layout_6.setContentsMargins(5, 0, 5, 0)
        layout_6.addWidget(self.upload_btn, alignment=Qt.AlignRight)
        widget_6.setLayout(layout_6)
        widget_6.setFixedHeight(35)
        self.expand_layout.addWidget(widget_6)

        self.log_output.setFixedHeight(100)
        self.log_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.log_output.setStyleSheet('font-size: 12px;font-family: \'Segoe UI\', \'Microsoft YaHei\';')
        self.log_output.setReadOnly(True)

    def init_layout(self):
        self.title_label.setAlignment(Qt.AlignCenter)

        self.expand_layout.setSpacing(15)
        self.expand_layout.setContentsMargins(20, 0, 35, 0)

        self.h_video_layout.setContentsMargins(5, 0, 5, 0)
        self.h_video_layout.addWidget(self.video_label, stretch=1, alignment=Qt.AlignTop)
        self.h_video_layout.addWidget(self.video_card_view, stretch=6, alignment=Qt.AlignTop)
        self.h_video_layout.addWidget(self.add_video_btn, stretch=1, alignment=Qt.AlignTop)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.log_output)

        self.set_qss()

    def set_qss(self):
        self.title_label.setObjectName('Title')
        self.scroll_widget.setObjectName('ScrollWidget')
        self.video_title_label.setObjectName('Text')
        self.cover_label.setObjectName('Text')
        self.cover_path_label.setObjectName('content')
        self.video_label.setObjectName('Text')
        self.reprint_info_label.setObjectName('Text')
        self.tag_label.setObjectName('Text')
        self.video_description_label.setObjectName('Text')

        with open(f'res/qss/light/upload_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
