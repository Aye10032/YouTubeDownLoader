import logging
from urllib.error import URLError

from PyQt5.QtCore import QThread, pyqtSignal
from yt_dlp import YoutubeDL, DownloadError
from yt_dlp.extractor.youtube import YoutubeIE

from common.Config import cfg
from common.Uploader import BiliBili, Data


class UpdateMessage(QThread):
    log_signal = pyqtSignal(dict)
    result_signal = pyqtSignal(dict)
    finish_signal = pyqtSignal()
    error_signal = pyqtSignal()

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            logger = logging.getLogger()
            handler = logging.StreamHandler()
            logger.addHandler(handler)

            ydl_opts = {
                'logger': logger
            }
            if cfg.get(cfg.proxy_enable):
                ydl_opts['proxy'] = cfg.get(cfg.proxy)
                ydl_opts['socket_timeout'] = 3000

            # print(ydl_opts)
            ydl = YoutubeDL(ydl_opts)
            ie = YoutubeIE
            ydl.add_info_extractor(ie)
            ydl.add_progress_hook(self.my_hook)
            info_dict = ydl.extract_info(self.url, download=False, force_generic_extractor=True)

            self.result_signal.emit(info_dict)
            self.finish_signal.emit()
        except DownloadError as e:
            self.error_signal.emit()
        except ConnectionRefusedError as e:
            self.error_signal.emit()
        except URLError as e:
            self.error_signal.emit()

    def my_hook(self, d):
        self.log_signal.emit(d)


class Download(QThread):
    log_signal = pyqtSignal(dict)
    finish_signal = pyqtSignal()
    error_signal = pyqtSignal()

    def __init__(self, url, ydl_opts):
        super().__init__()
        self.url = url
        self.ydl_opts = ydl_opts
        # print(ydl_opts)

    def run(self):
        try:
            logger = logging.getLogger()
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            self.ydl_opts['logger'] = logger

            ydl = YoutubeDL(self.ydl_opts)
            ydl.add_progress_hook(self.my_hook)
            ydl.download(self.url)

            self.finish_signal.emit()
        except DownloadError as e:
            self.error_signal.emit()
        except ConnectionRefusedError as e:
            self.error_signal.emit()

    def my_hook(self, d):
        self.log_signal.emit(d)


class Upload(QThread):
    finish_signal = pyqtSignal()

    def __init__(self, login_access, info: dict, video_list: list):
        super().__init__()
        self.login_access = login_access
        self.info = info
        self.video_list = video_list

    def run(self):
        video = Data()
        video.title = self.info['title']
        video.desc = self.info['desc']
        video.source = self.info['source']
        video.tid = 17
        video.set_tag(self.info['tag'])
        video.dynamic = self.info['dynamic']
        lines = 'AUTO'
        tasks = 3
        dtime = 0  # 延后时间，单位秒
        with BiliBili(video) as bili:
            bili.login("bili.cookie", self.login_access)

            for part in self.video_list:
                video_part = bili.upload_file(part['path'], part['name'], lines=lines, tasks=tasks)
                video.append(video_part)
            video.delay_time(dtime)
            video.cover = bili.cover_up(self.info['cover_path']).replace('http:', '')
            ret = bili.submit_client()  # 提交视频

        self.finish_signal.emit()
