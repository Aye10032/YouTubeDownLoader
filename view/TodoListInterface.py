import logging
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QLabel
from qfluentwidgets import ScrollArea, ExpandLayout, isDarkTheme
from requests import request

from Path import BASE_DIR
from common.Config import cfg
from common.MyWidget import VideoCardView, TextCard
from common.Style import StyleSheet


class TodoListInterface(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.scroll_area = ScrollArea(self)
        self.scroll_widget = QWidget(self)
        self.expand_layout = ExpandLayout(self.scroll_widget)
        self.video_card_view = VideoCardView('', self.scroll_widget)

        self.title_label = QLabel(self.tr("TODO List"), self)

        self.setObjectName(text)
        self.init_layout()
        self.init_widget()

    def init_layout(self):
        self.title_label.setAlignment(Qt.AlignCenter)

        if not cfg.get(cfg.api_server) == '':
            url = cfg.get(cfg.api_server)

            try:
                done_response = request("GET", url)

                json_data = done_response.json()

                for item in json_data['data']:
                    todo_id = item['id']
                    description = item['description']
                    url = item['url']
                    time_stamp = item['time']
                    # 将时间戳转换为指定格式
                    time_format = datetime.fromtimestamp(time_stamp / 1000).strftime('%Y年%m月%d日 %H:%M')

                    video_card = TextCard(f'{todo_id} | {description}', time_format, url, f'todo{todo_id}',
                                          self.video_card_view)
                    self.video_card_view.add_video_card(video_card)

            except ConnectionRefusedError:
                logging.warning('获取视频列表错误')

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

        StyleSheet.SCROLL.apply(self)
