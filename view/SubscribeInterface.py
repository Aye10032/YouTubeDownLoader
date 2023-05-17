from datetime import datetime

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QNetworkProxy
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QLabel
from googleapiclient.discovery import build
from httplib2 import ProxyInfo, socks, Http
from qfluentwidgets import ScrollArea, ExpandLayout

from common.Config import cfg, YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, BASE_DIR
from common.MyWidget import VideoCardView, TextCard


class SubscribeInterface(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.scroll_area = ScrollArea(self)
        self.scroll_widget = QWidget(self)
        self.expand_layout = ExpandLayout(self.scroll_widget)

        self.title_label = QLabel(self.tr("Subscribe List"), self)

        self.setObjectName(text)
        self.init_layout()
        self.init_widget()

    def init_layout(self):
        self.title_label.setAlignment(Qt.AlignCenter)

        if not cfg.get(cfg.api_token) == '':
            channels = cfg.get(cfg.subscribe_channels)
            for channel in channels:
                video_card_view = VideoCardView(channel['name'], self.scroll_widget)
                channel_id = channel['channel_id']

                videos = get_channel_info(channel_id)
                for video in videos:
                    url = 'https://youtu.be/' + video['id']['videoId']
                    title = video['snippet']['title']
                    upload_date = str_local_time(video['snippet']['publishedAt'])
                    video_card = TextCard(title, upload_date, url, video['id']['videoId'], video_card_view)
                    video_card_view.add_video_card(video_card)

                self.expand_layout.addWidget(video_card_view)

        self.expand_layout.setSpacing(28)
        self.expand_layout.setContentsMargins(20, 10, 20, 0)

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

        with open(f'{BASE_DIR}/res/qss/light/scroll_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


def get_channel_info(channel_id: str):
    if cfg.get(cfg.proxy_enable):
        ipaddress = cfg.get(cfg.proxy).split(':')[1][2:]
        ipport = int(cfg.get(cfg.proxy).split(':')[2])
        proxy_info = ProxyInfo(socks.PROXY_TYPE_HTTP, ipaddress, ipport)
        http = Http(timeout=300, proxy_info=proxy_info)
    else:
        http = Http(timeout=300)

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=cfg.get(cfg.api_token), http=http)

    result = youtube.search().list(
        part='snippet,id',
        channelId=channel_id,
        order='date',
        maxResults=8
    ).execute()

    return result['items']


def str_local_time(utc_time_str: str):
    utc_time = datetime.fromisoformat(utc_time_str.replace("Z", "+00:00"))
    local_time = utc_time.astimezone()

    return local_time.strftime('%Y年%m月%d日 %H:%M')


def load_pixmap_from_url(url):
    manager = QNetworkAccessManager()
    print(f'try to download {url}')

    if cfg.get(cfg.proxy_enable):
        proxy = QNetworkProxy()
        proxy.setType(QNetworkProxy.HttpProxy)
        proxy.setHostName(cfg.get(cfg.proxy).split(':')[1][2:])
        proxy.setPort(int(cfg.get(cfg.proxy).split(':')[2]))
        manager.setProxy(proxy)

    request = QNetworkRequest(QUrl(url))

    reply = manager.get(request)

    while not reply.isFinished():
        pass

    if reply.error() != QNetworkReply.NoError:
        print(f"Error loading image {url}")
        return None

    pixmap = QPixmap()
    pixmap.loadFromData(reply.readAll())

    return pixmap
