from PyQt5.QtCore import QThread, pyqtSignal
from yt_dlp import YoutubeDL
from yt_dlp.extractor.youtube import YoutubeIE

from common.Config import cfg
from common.Uploader import Data, BiliBili


class UpdateMessage(QThread):
    log_signal = pyqtSignal(dict)
    result_signal = pyqtSignal(dict)
    finish_signal = pyqtSignal()

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        if cfg.get(cfg.proxy_enable):
            ydl = YoutubeDL({
                'proxy': cfg.get(cfg.proxy),
            })
        else:
            ydl = YoutubeDL()

        ie = YoutubeIE
        ydl.add_info_extractor(ie)
        ydl.add_progress_hook(self.my_hook)
        info_dict = ydl.extract_info(self.url, download=False, force_generic_extractor=True)

        self.result_signal.emit(info_dict)
        self.finish_signal.emit()

    def my_hook(self, d):
        self.log_signal.emit(d)


class Download(QThread):
    log_signal = pyqtSignal(dict)
    finish_signal = pyqtSignal()

    def __init__(self, url, ydl_opts):
        super().__init__()
        self.url = url
        self.ydl_opts = ydl_opts
        print(ydl_opts)

    def run(self):
        ydl = YoutubeDL(self.ydl_opts)
        ydl.add_progress_hook(self.my_hook)
        ydl.download(self.url)

        self.finish_signal.emit()

    def my_hook(self, d):
        self.log_signal.emit(d)


class Upload(QThread):
    finish_signal = pyqtSignal()

    def __init__(self, video: Data, cover_path: str, bili: BiliBili):
        super().__init__()
        self.video = video
        self.cover_path = cover_path
        self.bili = bili

    def run(self):
        self.video.cover = self.bili.cover_up(self.cover_path).replace('http:', '')
        ret = self.bili.submit_client()  # 提交视频

        self.finish_signal.emit()
