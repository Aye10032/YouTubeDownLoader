from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QWidget, QSizePolicy, QHBoxLayout, QApplication
from qfluentwidgets import LineEdit, PushButton, ToolButton, SwitchButton, TextEdit, InfoBar, Dialog
from qfluentwidgets import FluentIcon as FIF
from yt_dlp import YoutubeDL
from yt_dlp.extractor.youtube import YoutubeIE

from Config import cfg, INFO, SUCCESS, WARNING, ARIA2C
from MyThread import UpdateMessage
from view.MyWidget import TableDialog


class EditWidget(QFrame):
    _uploader = ''
    _title = ''
    _description = ''
    _upload_date = ''
    _format_code, _extension, _resolution, _format_note, _file_size = [], [], [], [], []

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.update_message_thread = None

        self.main_layout = QGridLayout(self)
        self.title_label = QLabel(self.tr('Download Video'), self)

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

        self.play_btn = ToolButton(FIF.VIDEO, self)
        self.copy_btn = ToolButton(FIF.COPY, self)
        self.link_btn = ToolButton(FIF.GLOBE, self)
        self.folder_btn = ToolButton(FIF.FOLDER, self)

        self.log_output = TextEdit(self)

        self.init_ui()
        self.setObjectName(text)

    def init_ui(self):
        self.origin_link_input.setText('https://www.youtube.com/watch?v=dQw4w9WgXcQ')

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
        self.video_title_input.setText('【MC】【】')

        widget_4 = QWidget()
        layout_4 = QHBoxLayout()
        layout_4.setContentsMargins(0, 0, 0, 5)
        layout_4.addWidget(self.reprint_info_label, stretch=1)
        layout_4.addWidget(self.reprint_info_input, stretch=6)
        layout_4.addWidget(self.copy_reprint_btn, stretch=1)
        widget_4.setLayout(layout_4)
        self.main_layout.addWidget(widget_4, 5, 0, 1, 9)
        self.reprint_info_input.setText('转自 有能力请支持原作者')

        self.video_description_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.video_description_input, 6, 0, 3, 9)
        self.video_description_input.setStyleSheet('font-size: 12px;font-family: \'Segoe UI\', \'Microsoft YaHei\';')
        self.video_description_input.setText(
            f'作者：\r\n'
            f'发布时间：\r\n'
            f'搬运：{cfg.get(cfg.reprint_id)}\r\n'
            f'视频摘要：\r\n'
            f'原简介翻译：\r\n'
            f'存档：\r\n'
            f'其他外链：')

        widget_5 = QWidget()
        layout_5 = QHBoxLayout()
        layout_5.setContentsMargins(0, 5, 0, 15)
        layout_5.addWidget(self.play_btn, stretch=1)
        layout_5.addWidget(self.copy_btn, stretch=1)
        layout_5.addWidget(self.link_btn, stretch=1)
        layout_5.addWidget(self.folder_btn, stretch=1)
        widget_5.setLayout(layout_5)
        self.main_layout.addWidget(widget_5, 9, 0, 1, 9)

        self.log_output.setFixedHeight(100)
        self.log_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.main_layout.addWidget(self.log_output, 10, 0, 2, 9)
        self.log_output.setStyleSheet('font-size: 12px;font-family: \'Segoe UI\', \'Microsoft YaHei\';')
        self.log_output.setReadOnly(True)

        self.setLayout(self.main_layout)

        self.set_qss()
        self.connect_signal()

    def set_qss(self):
        self.title_label.setObjectName('Title')
        self.origin_link_label.setObjectName('Text')
        self.auto_quality_label.setObjectName('Text')
        self.quality_label.setObjectName('Text')
        self.video_title_label.setObjectName('Text')
        self.reprint_info_label.setObjectName('Text')

        with open(f'res/qss/light/edit_widget.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def connect_signal(self):
        self.auto_quality_btn.checkedChanged.connect(self.auto_quality_btn_changed)
        self.get_quality_btn.clicked.connect(self.on_get_quality_btn_clicked)
        self.get_info_btn.clicked.connect(self.start_get_info)
        self.download_btn.clicked.connect(self.start_download)

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

        self.update_message()

        format_info = [self._format_code, self._extension, self._resolution, self._format_note, self._file_size]
        w = TableDialog(len(self._format_code), 5, format_info, self)
        w.setTitleBarVisible(False)
        if w.exec():
            if w.audio_code != '':
                self.quality_input.setText(f'{w.audio_code}+{w.video_code}')
            else:
                self.quality_input.setText(w.video_code)
        else:
            print('Cancel button is pressed')

        self.show_finish_tooltip(self.tr('quality configure complete, now you can start download'), SUCCESS)

    def start_get_info(self):
        if self.update_message_thread and self.update_message_thread.isRunning():
            return

        print('start')
        self.update_message_thread = UpdateMessage(self.origin_link_input.text())
        self.update_message_thread.log_signal.connect(self.update_log)
        self.update_message_thread.result_signal.connect(self.update_message)
        self.update_message_thread.finish_signal.connect(self.get_info_done)
        self.update_message_thread.start()

    def start_download(self):
        if not self.auto_quality_btn.isChecked() and self.quality_input.text() == '':
            self.show_finish_tooltip(self.tr('you should choose quality first'), WARNING)
            return

        path = cfg.get(cfg.download_folder)
        quality = self.quality_input.text()

        ydl_opts = {
            "writethumbnail": True,
            "external_downloader_args": ['--max-connection-per-server', cfg.get(cfg.thread), '--min-split-size', '1M'],
            "external_downloader": ARIA2C,
            'paths': {'home': path},
            'outtmpl': {'default': '%(title)s.%(ext)s'},
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitlesformat': 'vtt',
            'subtitleslangs': ['zh-Hans', 'en'],
            'progress_hooks': [my_hook],
        }

        if cfg.get(cfg.proxy_enable):
            ydl_opts['proxy'] = cfg.get(cfg.proxy)
            ydl_opts['socket_timeout'] = 3000

        if cfg.get(cfg.auto_quality):
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            ydl_opts['format'] = quality

        print(ydl_opts)

        ydl = YoutubeDL(ydl_opts)
        ydl.download(self.origin_link_input.text())

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

    def show_finish_tooltip(self, text, tool_type: int):
        """ show restart tooltip """
        if tool_type == SUCCESS:
            InfoBar.success('', text, parent=self.window(), duration=5000)
        elif tool_type == WARNING:
            InfoBar.warning('', text, parent=self.window(), duration=5000)

    def update_log(self, log):
        print(f'log: {log}')


def my_hook(d):
    print(d)