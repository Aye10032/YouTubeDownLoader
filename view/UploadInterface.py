import json
import os
import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QGridLayout, QWidget, QSizePolicy, QHBoxLayout, QFileDialog
from qfluentwidgets import TextEdit, ScrollArea, ExpandLayout, LineEdit, ToolButton, PushButton, PrimaryPushButton
from qfluentwidgets import FluentIcon as FIF

from common.Config import cfg
from common.MyWidget import UploadCard, VideoCardView


class UploadInterface(QFrame):
    _videos = []

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.scroll_area = ScrollArea(self)
        self.scroll_widget = QWidget(self)
        self.expand_layout = ExpandLayout(self.scroll_widget)

        self.title_label = QLabel(self.tr("Upload"), self)

        self.video_title_label = QLabel(self.tr('Video Title'), self.scroll_widget)
        self.video_title_input = LineEdit(self.scroll_widget)

        self.cover_label = QLabel(self.tr('Cover'), self.scroll_widget)
        self.cover_path_input = LineEdit(self.scroll_widget)
        self.cover_path_btn = ToolButton(FIF.FOLDER, self.scroll_widget)

        self.widget_3 = QWidget(self.scroll_widget)
        self.video_label = QLabel(self.tr('Video'), self.scroll_widget)
        self.video_card_view = QWidget(self.scroll_widget)
        self.video_card_layout = QVBoxLayout()
        self.add_video_btn = ToolButton(FIF.FOLDER_ADD, self.scroll_widget)

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
        self.connect_signal()

    def init_widget(self):
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setViewportMargins(0, 10, 0, 20)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        widget_1 = QWidget(self.scroll_widget)
        layout_1 = QHBoxLayout()
        layout_1.setContentsMargins(5, 0, 0, 0)
        self.video_title_label.setFixedWidth(90)
        layout_1.addWidget(self.video_title_label, stretch=1)
        layout_1.addWidget(self.video_title_input, stretch=6)
        widget_1.setLayout(layout_1)
        widget_1.setFixedHeight(35)
        self.expand_layout.addWidget(widget_1)

        widget_2 = QWidget(self.scroll_widget)
        layout_2 = QHBoxLayout()
        layout_2.setContentsMargins(5, 0, 0, 0)
        self.cover_label.setFixedWidth(90)
        layout_2.addWidget(self.cover_label, stretch=1)
        layout_2.addWidget(self.cover_path_input, stretch=5)
        layout_2.addWidget(self.cover_path_btn, stretch=1)
        widget_2.setLayout(layout_2)
        widget_2.setFixedHeight(35)
        self.expand_layout.addWidget(widget_2)

        layout_3 = QHBoxLayout()
        layout_3.setContentsMargins(5, 0, 0, 0)
        self.video_label.setFixedWidth(90)
        layout_3.addWidget(self.video_label, stretch=1, alignment=Qt.AlignTop)
        layout_3.addWidget(self.video_card_view, stretch=6, alignment=Qt.AlignTop)
        self.video_card_layout.addWidget(self.add_video_btn, alignment=Qt.AlignRight)
        self.widget_3.setLayout(layout_3)
        self.widget_3.setFixedHeight(35)
        self.expand_layout.addWidget(self.widget_3)

        widget_4 = QWidget(self.scroll_widget)
        layout_4 = QHBoxLayout()
        layout_4.setContentsMargins(5, 0, 0, 0)
        self.reprint_info_label.setFixedWidth(90)
        layout_4.addWidget(self.reprint_info_label, stretch=1)
        layout_4.addWidget(self.reprint_info_input, stretch=6)
        widget_4.setLayout(layout_4)
        widget_4.setFixedHeight(35)
        self.expand_layout.addWidget(widget_4)

        widget_5 = QWidget(self.scroll_widget)
        layout_5 = QHBoxLayout()
        layout_5.setContentsMargins(5, 0, 0, 0)
        self.tag_label.setFixedWidth(90)
        layout_5.addWidget(self.tag_label, stretch=1)
        layout_5.addWidget(self.tag_input, stretch=6)
        widget_5.setLayout(layout_5)
        widget_5.setFixedHeight(35)
        self.expand_layout.addWidget(widget_5)

        widget_6 = QWidget(self.scroll_widget)
        layout_6 = QHBoxLayout()
        layout_6.setContentsMargins(5, 0, 0, 0)
        self.video_description_label.setFixedWidth(90)
        layout_6.addWidget(self.video_description_label, stretch=1, alignment=Qt.AlignTop)
        layout_6.addWidget(self.video_description_input, stretch=6, alignment=Qt.AlignTop)
        self.video_description_input.setStyleSheet('font-size: 12px;font-family: \'Segoe UI\', \'Microsoft YaHei\';')
        self.video_description_input.setFixedHeight(240)
        widget_6.setLayout(layout_6)
        widget_6.setFixedHeight(250)
        self.expand_layout.addWidget(widget_6)

        widget_7 = QWidget(self.scroll_widget)
        layout_7 = QHBoxLayout()
        layout_7.setContentsMargins(5, 0, 0, 0)
        layout_7.addWidget(self.upload_btn, alignment=Qt.AlignCenter)
        widget_7.setLayout(layout_7)
        widget_7.setFixedHeight(35)
        self.expand_layout.addWidget(widget_7)

        self.log_output.setFixedHeight(100)
        self.log_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.log_output.setStyleSheet('font-size: 12px;font-family: \'Segoe UI\', \'Microsoft YaHei\';')
        self.log_output.setReadOnly(True)

    def init_layout(self):
        self.title_label.setAlignment(Qt.AlignCenter)

        self.video_card_view.setLayout(self.video_card_layout)
        self.video_card_layout.setSpacing(5)
        self.video_card_layout.setContentsMargins(0, 0, 0, 0)

        self.expand_layout.setSpacing(10)
        self.expand_layout.setContentsMargins(15, 0, 30, 0)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.log_output)

        self.set_qss()

    def init_text(self, path: str):
        data_file = os.path.join(path, 'data.json')
        with open(data_file, 'r') as f:
            data_contents = json.loads(f.read())
            self.video_title_input.setText(data_contents['title'])
            self.reprint_info_input.setText(data_contents['reprint'])
            self.video_description_input.setText(data_contents['description'])

        self.cover_path_input.setText(os.path.join(path, 'cover.jpg'))
        for file in os.listdir(path):
            if file.endswith('.mp4') or file.endswith('.mkv'):
                video_path = os.path.join(path, file)
                self.add_video(video_path)

    def add_video(self, path):
        video = {
            'name': os.path.splitext(os.path.split(path)[1])[0],
            'path': path
        }
        if video not in self._videos:
            self._videos.append(video)
            count = len(self._videos)
            if count == 0:
                self.video_card_view.setFixedHeight(35)
                self.widget_3.setFixedHeight(35)
            else:
                self.video_card_view.setFixedHeight(count * 85 + 45)
                self.widget_3.setFixedHeight(count * 85 + 45)

            route_key = re.findall(r'\[(.*?)\]', video['name'])[-1]
            card = UploadCard(video['name'], video['path'], self.scroll_widget)
            card.setObjectName(f"upload_card_{route_key}")
            self.video_card_layout.addWidget(card)

            self.video_card_layout.update()
            self.video_card_view.update()
            self.scroll_widget.update()
            self.update()
        else:
            return

    def set_qss(self):
        self.title_label.setObjectName('Title')
        self.scroll_widget.setObjectName('ScrollWidget')
        self.video_title_label.setObjectName('Text')
        self.cover_label.setObjectName('Text')
        self.video_label.setObjectName('Text')
        self.reprint_info_label.setObjectName('Text')
        self.tag_label.setObjectName('Text')
        self.video_description_label.setObjectName('Text')

        with open(f'res/qss/light/upload_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def connect_signal(self):
        self.cover_path_btn.clicked.connect(self.on_cover_path_btn_clicked)
        self.add_video_btn.clicked.connect(self.on_add_video_btn_clicked)
        self.upload_btn.clicked.connect(self.on_upload_btn_clicked)

    def on_cover_path_btn_clicked(self):
        options = QFileDialog.Options()
        options.filter = "JPEG files (*.jpg)"
        file_name, _ = QFileDialog.getOpenFileName(None, "Choose Image File", cfg.get(cfg.download_folder),
                                                   "Image files (*.jpg *.png *.bmp)", options=options)
        self.cover_path_input.setText(file_name)

    def on_add_video_btn_clicked(self):
        options = QFileDialog.Options()
        options.filter = "MP4 files (*.mp4)"
        file_name, _ = QFileDialog.getOpenFileName(None, "Choose Image File", cfg.get(cfg.download_folder),
                                                   "Video files (*.mp4)", options=options)

        self.add_video(file_name)

    def on_upload_btn_clicked(self):
        for video in self._videos:
            route_key = re.findall(r'\[(.*?)\]', video['name'])[-1]
            card = self.video_card_view.findChild(UploadCard, f"upload_card_{route_key}",
                                                  options=Qt.FindDirectChildrenOnly)
            if card is not None:
                print(card.title_input.text())
