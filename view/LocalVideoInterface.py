import json
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QLabel
from qfluentwidgets import ScrollArea, ExpandLayout

from common.Config import cfg
from common.MyWidget import VideoCard, VideoCardView


class LocalVideoInterface(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.scroll_area = ScrollArea(self)
        self.scroll_widget = QWidget(self)
        self.expand_layout = ExpandLayout(self.scroll_widget)
        self.video_card_view = VideoCardView('', self.scroll_widget)

        self.title_label = QLabel(self.tr("Download List"), self)

        self.setObjectName(text)
        self.init_layout()
        self.init_widget()
        self.connect_signal()

    def init_layout(self):
        self.title_label.setAlignment(Qt.AlignCenter)

        downloads = os.listdir(cfg.get(cfg.download_folder))

        index = 0
        for video_folder in downloads:
            video_path = os.path.join(cfg.get(cfg.download_folder), video_folder)
            if os.path.isdir(video_path):
                data_file = os.path.join(video_path, 'data.json')
                if os.path.exists(data_file) and os.path.isfile(data_file):
                    with open(data_file, 'r') as f:
                        data_contents = json.loads(f.read())
                    cover_files = [os.path.join(video_path, 'cover' + ext) for ext in ['.jpg', '.webp']]
                    for cover_file in cover_files:
                        if os.path.exists(cover_file) and os.path.isfile(cover_file):
                            image = QPixmap(cover_file)
                            index += 1
                            video_card = VideoCard(image, data_contents['title'], os.path.abspath(video_path),
                                                   f'video_card{index}', index)
                            self.video_card_view.add_video_card(video_card)
                            break
                else:
                    continue

        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(20, 10, 20, 0)
        self.expand_layout.addWidget(self.video_card_view)

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

        with open(f'res/qss/light/scroll_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def connect_signal(self):
        pass
