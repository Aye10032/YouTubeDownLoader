import json
import os
import subprocess
import webbrowser

from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QWidget, QSizePolicy, QHBoxLayout
from qfluentwidgets import LineEdit, PushButton, ToolButton, SwitchButton, TextEdit, InfoBar, ToolTipFilter, \
    ToolTipPosition
from qfluentwidgets import FluentIcon as FIF
from yt_dlp import YoutubeDL

from common.Config import cfg, SUCCESS, WARNING
from common.MyThread import UpdateMessage, Download
from common.MyWidget import TableDialog
from common.SignalBus import signal_bus
from common.Style import StyleSheet, MyIcon


class DownloadInterface(QFrame):
    _uploader = ''
    _title = ''
    _description = ''
    _upload_date = ''
    _format_code, _extension, _resolution, _format_note, _file_size = [], [], [], [], []
    _path = ''
    _download = False

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.update_message_thread = None
        self.download_thread = None

        self.main_layout = QGridLayout(self)
        self.title_label = QLabel(self.tr('Video Download'), self)

        self.origin_link_label = QLabel(self.tr('Origin Link'), self)
        self.origin_link_input = LineEdit(self)

        self.auto_quality_label = QLabel(self.tr('Auto Quality'), self)
        self.auto_quality_btn = SwitchButton()
        self.quality_label = QLabel(self.tr('Quality'), self)
        self.quality_input = LineEdit(self)
        self.get_quality_btn = ToolButton(FIF.SEARCH, self)

        self.get_info_btn = PushButton(self.tr('Get Info'), self, FIF.MESSAGE)
        self.download_btn = PushButton(self.tr('Download Video'), self, FIF.DOWNLOAD)

        self.video_title_label = QLabel(self.tr('Video Title'), self)
        self.video_title_input = LineEdit(self)
        self.copy_title_btn = ToolButton(FIF.COPY, self)

        self.reprint_info_label = QLabel(self.tr('Reprinter Info'), self)
        self.reprint_info_input = LineEdit(self)
        self.copy_reprint_btn = ToolButton(FIF.COPY, self)

        self.video_description_input = TextEdit(self)

        self.save_btn = ToolButton(FIF.SAVE, self)
        self.play_btn = ToolButton(MyIcon.PLAY, self)
        self.copy_btn = ToolButton(FIF.COPY, self)
        self.link_btn = ToolButton(MyIcon.LINK, self)
        self.folder_btn = ToolButton(FIF.FOLDER, self)
        self.upload_btn = ToolButton(FIF.SEND, self)

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

        widget_1 = QWidget()
        layout_1 = QHBoxLayout()
        layout_1.setContentsMargins(0, 5, 0, 5)
        self.origin_link_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout_1.addWidget(self.origin_link_label, stretch=1)
        layout_1.addWidget(self.origin_link_input, stretch=6)
        widget_1.setLayout(layout_1)
        self.main_layout.addWidget(widget_1, 1, 0, 1, 9)

        widget_2 = QWidget()
        layout_2 = QGridLayout()
        layout_2.setContentsMargins(0, 0, 0, 5)
        self.quality_input.setText('')
        self.quality_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout_2.addWidget(self.auto_quality_label, 0, 0, Qt.AlignLeft)
        layout_2.addWidget(self.auto_quality_btn, 0, 1, Qt.AlignLeft)
        layout_2.addWidget(self.quality_label, 0, 3, Qt.AlignCenter)
        layout_2.addWidget(self.quality_input, 0, 4, 1, 2)
        layout_2.addWidget(self.get_quality_btn, 0, 6)
        widget_2.setLayout(layout_2)
        self.main_layout.addWidget(widget_2, 2, 0, 1, 9)
        self.auto_quality_btn.setChecked(cfg.get(cfg.auto_quality))
        self.auto_quality_btn.setText(
            self.tr('On') if self.auto_quality_btn.isChecked() else self.tr('Off'))
        self.quality_input.setReadOnly(cfg.get(cfg.auto_quality))

        self.main_layout.addWidget(self.get_info_btn, 3, 2, 1, 2, Qt.AlignHCenter)
        self.main_layout.addWidget(self.download_btn, 3, 5, 1, 2, Qt.AlignHCenter)

        widget_3 = QWidget()
        layout_3 = QHBoxLayout()
        layout_3.setContentsMargins(0, 15, 0, 5)
        layout_3.addWidget(self.video_title_label, stretch=1)
        layout_3.addWidget(self.video_title_input, stretch=6)
        layout_3.addWidget(self.copy_title_btn, stretch=1)
        widget_3.setLayout(layout_3)
        self.main_layout.addWidget(widget_3, 4, 0, 1, 9)

        widget_4 = QWidget()
        layout_4 = QHBoxLayout()
        layout_4.setContentsMargins(0, 0, 0, 5)
        layout_4.addWidget(self.reprint_info_label, stretch=1)
        layout_4.addWidget(self.reprint_info_input, stretch=6)
        layout_4.addWidget(self.copy_reprint_btn, stretch=1)
        widget_4.setLayout(layout_4)
        self.main_layout.addWidget(widget_4, 5, 0, 1, 9)

        self.video_description_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.video_description_input, 6, 0, 3, 9)
        self.video_description_input.setStyleSheet('font-size: 12px;font-family: \'Segoe UI\', \'Microsoft YaHei\';')

        widget_5 = QWidget()
        layout_5 = QHBoxLayout()
        layout_5.setContentsMargins(0, 5, 0, 15)
        layout_5.addWidget(self.save_btn, stretch=1)
        layout_5.addWidget(self.folder_btn, stretch=1)
        layout_5.addWidget(self.play_btn, stretch=1)
        layout_5.addWidget(self.link_btn, stretch=1)
        layout_5.addWidget(self.copy_btn, stretch=1)
        layout_5.addWidget(self.upload_btn, stretch=1)
        widget_5.setLayout(layout_5)
        self.main_layout.addWidget(widget_5, 9, 0, 1, 9)
        self.save_btn.setToolTip(self.tr('save download information'))
        self.folder_btn.setToolTip(self.tr('open download folder'))
        self.play_btn.setToolTip(self.tr('play download video'))
        self.link_btn.setToolTip(self.tr('open youtube link'))
        self.copy_btn.setToolTip(self.tr('copy description'))
        self.upload_btn.setToolTip(self.tr('turn to upload page'))
        self.save_btn.installEventFilter(ToolTipFilter(self.save_btn, 300, ToolTipPosition.TOP))
        self.folder_btn.installEventFilter(ToolTipFilter(self.folder_btn, 300, ToolTipPosition.TOP))
        self.play_btn.installEventFilter(ToolTipFilter(self.play_btn, 300, ToolTipPosition.TOP))
        self.link_btn.installEventFilter(ToolTipFilter(self.link_btn, 300, ToolTipPosition.TOP))
        self.copy_btn.installEventFilter(ToolTipFilter(self.copy_btn, 300, ToolTipPosition.TOP))
        self.upload_btn.installEventFilter(ToolTipFilter(self.upload_btn, 300, ToolTipPosition.TOP))

        self.log_output.setFixedHeight(100)
        self.log_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.main_layout.addWidget(self.log_output, 10, 0, 2, 9)
        self.log_output.setStyleSheet('font-size: 12px;font-family: \'Segoe UI\', \'Microsoft YaHei\';')
        self.log_output.setReadOnly(True)

        self.setLayout(self.main_layout)

        self.init_text()
        self.set_qss()
        self.connect_signal()

    def init_text(self):
        self.origin_link_input.setText('')
        self.video_title_input.setText('【MC】【】')
        self.reprint_info_input.setText('转自 有能力请支持原作者')
        self.video_description_input.setText(
            f'作者：\r\n'
            f'发布时间：\r\n'
            f'搬运：{cfg.get(cfg.reprint_id)}\r\n'
            f'视频摘要：\r\n'
            f'原简介翻译：\r\n'
            f'存档：\r\n'
            f'其他外链：')

    def update_ui(self, path):
        self._path = path
        data_file = os.path.join(path, 'data.json')
        with open(data_file, 'r') as f:
            data_contents = json.loads(f.read())
            self.origin_link_input.setText(data_contents['link'])
            self.video_title_input.setText(data_contents['title'])
            self.reprint_info_input.setText(data_contents['reprint'])
            self.video_description_input.setText(data_contents['description'])
            self._uploader = data_contents['uploader']

    def set_url(self, url):
        self.init_text()
        self.origin_link_input.setText(url)

    def set_qss(self):
        self.title_label.setObjectName('Title')
        self.origin_link_label.setObjectName('Text')
        self.auto_quality_label.setObjectName('Text')
        self.quality_label.setObjectName('Text')
        self.video_title_label.setObjectName('Text')
        self.reprint_info_label.setObjectName('Text')

        StyleSheet.DOWNLOAD.apply(self)

    def connect_signal(self):
        self.auto_quality_btn.checkedChanged.connect(self.auto_quality_btn_changed)
        self.get_quality_btn.clicked.connect(self.on_get_quality_btn_clicked)

        self.get_info_btn.clicked.connect(self.start_get_info)
        self.download_btn.clicked.connect(self.on_download_btn_clicked)

        self.copy_title_btn.clicked.connect(self.copy_title)
        self.copy_reprint_btn.clicked.connect(self.copy_reprint)

        self.save_btn.clicked.connect(self.on_save_btn_clicked)
        self.folder_btn.clicked.connect(self.on_folder_btn_clicked)
        self.play_btn.clicked.connect(self.on_play_btn_clicked)
        self.link_btn.clicked.connect(self.on_link_btn_clicked)
        self.copy_btn.clicked.connect(self.on_copy_btn_clicked)
        self.upload_btn.clicked.connect(self.on_upload_btn_clicked)

    def auto_quality_btn_changed(self, is_checked: bool):
        if is_checked:
            self.auto_quality_btn.setText(self.tr('On'))
        else:
            self.auto_quality_btn.setText(self.tr('Off'))

        cfg.set(cfg.auto_quality, is_checked)

        self.quality_input.setReadOnly(is_checked)

    def on_get_quality_btn_clicked(self):
        if self.auto_quality_btn.isChecked():
            self.show_finish_tooltip(
                self.tr('auto quality is enabled, you can start downloading the video directly'), WARNING)
            return

        if self.update_message_thread and self.update_message_thread.isRunning():
            return

        self.update_message_thread = UpdateMessage(self.origin_link_input.text())
        self.update_message_thread.log_signal.connect(self.update_log)
        self.update_message_thread.result_signal.connect(self.update_message)
        self.update_message_thread.finish_signal.connect(self.get_quality_done)
        self.update_message_thread.start()

    def start_get_info(self):
        if self.update_message_thread and self.update_message_thread.isRunning():
            return

        self.update_message_thread = UpdateMessage(self.origin_link_input.text())
        self.update_message_thread.log_signal.connect(self.update_log)
        self.update_message_thread.result_signal.connect(self.update_message)
        self.update_message_thread.finish_signal.connect(self.get_info_done)
        self.update_message_thread.start()

    def on_download_btn_clicked(self):
        if not self.auto_quality_btn.isChecked() and self.quality_input.text() == '':
            self.show_finish_tooltip(self.tr('you should choose quality first'), WARNING)
            return

        if self.video_title_input.text() == '【MC】【】':
            if self.update_message_thread and self.update_message_thread.isRunning():
                return

            self.update_message_thread = UpdateMessage(self.origin_link_input.text())
            self.update_message_thread.log_signal.connect(self.update_log)
            self.update_message_thread.result_signal.connect(self.update_message)
            self.update_message_thread.finish_signal.connect(self.start_download)
            self.update_message_thread.start()
        else:
            self.start_download()

    def start_download(self):
        self._path = cfg.get(cfg.download_folder) + '/' + self.video_title_input.text(). \
            replace(':', '').replace('.', '').replace('|', '').replace('\\', '').replace('/', '') \
            .replace('?', '').replace('\"', '')

        quality = self.quality_input.text()

        ydl_opts = {
            "writethumbnail": True,
            'concurrent-fragments': cfg.get(cfg.thread),
            'paths': {'home': self._path},
            'output': {'default': '%(title)s.%(ext)s'},
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitlesformat': 'vtt',
            'subtitleslangs': ['zh-Hans', 'en'],
        }

        if cfg.get(cfg.proxy_enable):
            ydl_opts['proxy'] = cfg.get(cfg.proxy)
            ydl_opts['socket_timeout'] = 3000

        if cfg.get(cfg.auto_quality):
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'
        else:
            ydl_opts['format'] = quality

        if self.download_thread and self.download_thread.isRunning():
            return

        self.download_thread = Download(self.origin_link_input.text(), ydl_opts)
        self.download_thread.log_signal.connect(self.update_log)
        self.download_thread.finish_signal.connect(self.download_done)
        self.download_thread.start()

    def update_message(self, info_dict):
        self._uploader = info_dict.get('uploader')
        self._title = info_dict.get('title')
        self._description = info_dict.get('description')

        if not (info_dict.get("upload_date") is None):
            self._upload_date = info_dict.get("upload_date", None)
        else:
            self._upload_date = '00000000'

        if self._upload_date[4] == '0' and self._upload_date[6] == '0':
            date = self._upload_date[0:4] + '年' + self._upload_date[5] + '月' + self._upload_date[7:8] + '日'
        elif self._upload_date[4] == '0' and not self._upload_date[6] == 0:
            date = self._upload_date[0:4] + '年' + self._upload_date[5] + '月' + self._upload_date[6:8] + '日'
        elif not self._upload_date[4] == '0' and self._upload_date[6] == '0':
            date = self._upload_date[0:4] + '年' + self._upload_date[4:6] + '月' + self._upload_date[7:8] + '日'
        else:
            date = self._upload_date[0:4] + '年' + self._upload_date[4:6] + '月' + self._upload_date[6:8] + '日'

        self.video_title_input.setText(f'【MC】{self._title}【{self._uploader}】')
        self.reprint_info_input.setText(f'转自{self.origin_link_input.text()} 有能力请支持原作者')
        self.video_description_input.setText(
            f'作者：{self._uploader}\r\n'
            f'发布时间：{date}\r\n'
            f'搬运：{cfg.get(cfg.reprint_id)}\r\n'
            f'视频摘要：\r\n'
            f'原简介翻译：{self._description}\r\n'
            f'存档：\r\n'
            f'其他外链：')

        formats = info_dict.get('formats')
        for f in formats:
            self._format_code.append(f.get('format_id'))
            self._extension.append(f.get('ext'))
            self._resolution.append(YoutubeDL.format_resolution(f))
            self._format_note.append(f.get('format_note'))
            self._file_size.append(f.get('filesize'))

    def get_info_done(self):
        self.show_finish_tooltip(self.tr('description download complete'), SUCCESS)

    def download_done(self):
        files = os.listdir(self._path)

        for file in files:
            if file.endswith('.jpg'):
                old_path = os.path.join(self._path, file)
                new_path = os.path.join(self._path, 'cover{}'.format(os.path.splitext(file)[1]))
                os.rename(old_path, new_path)
            elif file.endswith('.webp'):
                old_path = os.path.join(self._path, file)
                new_path = os.path.join(self._path, 'cover.jpg')
                with Image.open(old_path) as im:
                    im.convert('RGB').save(new_path, 'JPEG')

        info = {
            'link': self.origin_link_input.text(),
            'title': self.video_title_input.text(),
            'reprint': self.reprint_info_input.text(),
            'description': self.video_description_input.toPlainText(),
            'uploader': self._uploader
        }

        with open(f'{self._path}/data.json', 'w') as f:
            json.dump(info, f)

        self.show_finish_tooltip(self.tr('download complete'), SUCCESS)
        self._download = True

    def get_quality_done(self):
        format_info = [self._format_code, self._extension, self._resolution, self._format_note, self._file_size]
        w = TableDialog(len(self._format_code), 5, format_info, self)
        w.setTitleBarVisible(False)
        if w.exec():
            if w.audio_code != '':
                self.quality_input.setText(f'{w.audio_code}+{w.video_code}')
            else:
                self.quality_input.setText(w.video_code)

            self.show_finish_tooltip(self.tr('quality configure complete, now you can start download'), SUCCESS)
        else:
            print('Cancel button is pressed')

    def show_finish_tooltip(self, text, tool_type: int):
        """ show restart tooltip """
        if tool_type == SUCCESS:
            InfoBar.success('', text, parent=self.window(), duration=5000)
        elif tool_type == WARNING:
            InfoBar.warning('', text, parent=self.window(), duration=5000)

    def copy_title(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.video_title_input.text())
        self.show_finish_tooltip(self.tr('the content of the title has been copied'), SUCCESS)

    def copy_reprint(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.reprint_info_input.text())
        self.show_finish_tooltip(self.tr('the content of the reprint has been copied'), SUCCESS)

    def on_save_btn_clicked(self):
        if self._path == '':
            self.show_finish_tooltip(self.tr('you haven\'t downloaded any videos yet'), WARNING)
            return

        info = {
            'link': self.origin_link_input.text(),
            'title': self.video_title_input.text(),
            'reprint': self.reprint_info_input.text(),
            'description': self.video_description_input.toPlainText(),
            'uploader': self._uploader
        }

        with open(f'{self._path}/data.json', 'w') as f:
            json.dump(info, f)

        self.show_finish_tooltip(self.tr('video information is saved'), SUCCESS)

    def on_folder_btn_clicked(self):
        if self._path == '':
            self.show_finish_tooltip(self.tr('you haven\'t downloaded any videos yet'), WARNING)
            return

        if os.name == 'nt':
            os.startfile(self._path)
        elif os.name == 'darwin':
            subprocess.Popen(['open', self._path])
        else:
            subprocess.Popen(['xdg-open', self._path])

    def on_play_btn_clicked(self):
        if not self._download:
            self.show_finish_tooltip(self.tr('you haven\'t downloaded any videos yet'), WARNING)
            return

        files = os.listdir(self._path)

        for file in files:
            if file.endswith('.mp4'):
                video_path = os.path.join(self._path, file)
                if os.name == 'nt':
                    os.startfile(video_path)
                elif os.name == 'darwin':
                    subprocess.Popen(['open', video_path])
                else:
                    subprocess.Popen(['xdg-open', video_path])

    def on_link_btn_clicked(self):
        if self.origin_link_input.text() == '':
            self.show_finish_tooltip(self.tr('you haven\'t entered a video link yet'), WARNING)
            return

        webbrowser.open(self.origin_link_input.text())

    def on_copy_btn_clicked(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.video_description_input.toPlainText())
        self.show_finish_tooltip(self.tr('the content of the description has been copied'), SUCCESS)

    def on_upload_btn_clicked(self):
        if self._path == '':
            self.show_finish_tooltip(self.tr('you haven\'t downloaded any videos yet'), WARNING)
            return

        signal_bus.path2_upload_signal.emit(self._path)

    def update_log(self, log):
        self.log_output.append('[' + log.get('status') + '] ' + log.get('_default_template'))
