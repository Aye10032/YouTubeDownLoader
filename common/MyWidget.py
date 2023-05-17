from typing import Union

import qfluentwidgets
from PyQt5.QtCore import pyqtSignal, Qt, QRectF
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QGridLayout, QTableWidgetItem, QFrame, \
    QHBoxLayout, QToolButton
from qfluentwidgets import SettingCard, FluentIconBase, Slider, qconfig, LineEdit, TableWidget, \
    TextWrap, PixmapLabel, ExpandLayout, ExpandSettingCard, ConfigItem, PushButton, drawIcon
from qfluentwidgets.components.dialog_box.dialog import Dialog
from qfluentwidgets import FluentIcon as FIF

from common.Config import BASE_DIR
from common.SignalBus import signal_bus


class RangeSettingCard(SettingCard):
    """ Setting card with a slider """

    valueChanged = pyqtSignal(int)

    def __init__(self, configItem, icon: Union[str, QIcon, FluentIconBase], title, content=None, parent=None):
        """
        Parameters
        ----------
        configItem: RangeConfigItem
            configuration item operated by the card

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of card

        content: str
            the content of card

        parent: QWidget
            parent widget
        """
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.slider = Slider(Qt.Horizontal, self)
        self.valueLabel = QLabel(self)
        self.slider.setMinimumWidth(180)

        self.slider.setSingleStep(1)
        self.slider.setRange(*configItem.range)
        self.slider.setValue(configItem.value)
        self.valueLabel.setNum(configItem.value)

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.valueLabel, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(6)
        self.hBoxLayout.addWidget(self.slider, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.valueLabel.setObjectName('valueLabel')
        configItem.valueChanged.connect(self.setValue)
        self.slider.valueChanged.connect(self.__onValueChanged)

    def __onValueChanged(self, value: int):
        """ slider value changed slot """
        self.setValue(value)
        self.valueChanged.emit(value)

    def setValue(self, value):
        qconfig.set(self.configItem, value)
        self.valueLabel.setNum(value)
        self.valueLabel.adjustSize()


class TextDialog(Dialog):
    """ Dialog box """

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, title: str, content: str, default: str, parent=None):
        super().__init__(title, content, parent=parent)
        self.vBoxLayout.removeWidget(self.windowTitleLabel)
        self.input_edit = LineEdit(self)
        self.input_edit.setText(default)
        self.main_widget = QWidget()
        self.main_layout = QGridLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.addWidget(self.titleLabel, 0, 0)
        self.main_layout.addWidget(self.contentLabel, 1, 0)
        self.main_layout.addWidget(self.input_edit, 2, 0)
        self.titleLabel.setContentsMargins(10, 10, 5, 0)
        self.contentLabel.setContentsMargins(10, 10, 5, 0)
        self.input_edit.setContentsMargins(10, 0, 10, 0)
        self.main_widget.setLayout(self.main_layout)
        self.vBoxLayout.insertWidget(0, self.main_widget)


class TableDialog(Dialog):
    """ Dialog box """

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()
    audio_code = ''
    video_code = ''

    def __init__(self, row: int, col: int, content: [], parent=None):
        super().__init__('', '', parent=parent)
        self.tableView = TableWidget(self)

        self.tableView.setRowCount(row)
        self.tableView.setColumnCount(col)

        for i in range(row):
            self.tableView.setItem(i, 0, QTableWidgetItem(content[0][i]))
            self.tableView.setItem(i, 1, QTableWidgetItem(content[1][i]))
            self.tableView.setItem(i, 2, QTableWidgetItem(content[2][i]))
            self.tableView.setItem(i, 3, QTableWidgetItem(content[3][i]))
            self.tableView.setItem(i, 4, QTableWidgetItem('None' if content[4][i] is None else str(content[4][i])))

        self.init_ui()

    def init_ui(self):
        self.vBoxLayout.removeWidget(self.contentLabel)
        self.vBoxLayout.removeItem(self.textLayout)

        self.tableView.setWordWrap(False)
        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(['代号', '格式', '描述', '编码信息', '文件大小'])
        self.tableView.resizeColumnsToContents()

        self.vBoxLayout.insertWidget(0, self.tableView)

        self.setFixedSize(450, 400)

        self.tableView.itemClicked.connect(self.on_item_clicked)

    def on_item_clicked(self, item: QTableWidgetItem):
        row = item.row()
        if self.tableView.item(row, 2).text() == 'audio only':
            self.audio_code = self.tableView.item(row, 0).text()
        else:
            self.video_code = self.tableView.item(row, 0).text()


class VideoCard(QFrame):
    def __init__(self, image: QPixmap, title, content, route_key, index, parent=None):
        super().__init__(parent=parent)
        self.index = index
        self.route_key = route_key
        self.path = content

        self.image_widget = PixmapLabel(self)
        self.image_widget.setPixmap(image.scaled(
            128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        self.title_label = QLabel(title, self)
        self.content_label = QLabel(TextWrap.wrap(content, 45, False)[0], self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(90)
        self.hBoxLayout.setSpacing(28)
        self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addWidget(self.image_widget)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.title_label)
        self.vBoxLayout.addWidget(self.content_label)
        self.vBoxLayout.addStretch(1)

        self.set_qss()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        signal_bus.path2_download_signal.emit(self.path)

    def set_qss(self):
        self.title_label.setObjectName('titleLabel')
        self.content_label.setObjectName('contentLabel')

        with open(f'{BASE_DIR}/res/qss/light/video_card.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


class TextCard(QFrame):
    def __init__(self, title: str, upload_date: str, url: str, route_key, parent=None):
        super().__init__(parent=parent)
        self.route_key = route_key
        self.title = title
        self.upload_date = upload_date
        self.url = url

        # self.title_label = QLabel(TextWrap.wrap(self.title, 70, False)[0], self)
        self.title_label = QLabel(self.title, self)
        self.upload_date_label = QLabel(self.upload_date, self)
        self.url_label = QLabel(self.url, self)

        self.vBoxLayout = QVBoxLayout(self)

        self.setFixedHeight(75)
        # self.setFixedWidth(500)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(10, 0, 10, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.title_label)
        self.vBoxLayout.addWidget(self.url_label)
        self.vBoxLayout.addWidget(self.upload_date_label)
        self.upload_date_label.setAlignment(Qt.AlignRight)
        self.upload_date_label.setContentsMargins(10, 0, 30, 0)
        self.vBoxLayout.addStretch(1)

        self.set_qss()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        signal_bus.url2_download_signal.emit(self.url)

    def set_qss(self):
        self.title_label.setObjectName('titleLabel')
        self.url_label.setObjectName('contentLabel')
        self.upload_date_label.setObjectName('contentLabel')

        with open(f'{BASE_DIR}/res/qss/light/video_card.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


class VideoCardView(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.titleLabel = QLabel(title, self)
        self.vBoxLayout = QVBoxLayout(self)
        self.cardLayout = ExpandLayout()

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setSpacing(0)
        self.cardLayout.setContentsMargins(0, 0, 0, 0)
        self.cardLayout.setSpacing(5)

        if not title == '':
            self.vBoxLayout.addWidget(self.titleLabel)
            self.vBoxLayout.addSpacing(12)
        self.vBoxLayout.addLayout(self.cardLayout, 1)

        self.titleLabel.adjustSize()
        self.set_qss()

    def add_video_card(self, card: QWidget):
        card.setParent(self)
        self.cardLayout.addWidget(card)
        self.adjustSize()

    def adjustSize(self):
        h = self.cardLayout.heightForWidth(self.width()) + 46
        return self.resize(self.width(), h)

    def set_qss(self):
        self.titleLabel.setObjectName('viewTitleLabel')

        with open(f'{BASE_DIR}/res/qss/light/video_card.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


class ChannelDialog(Dialog):
    """ Dialog box """

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__('', '', parent=parent)
        self.channel_name_label = QLabel(self.tr('Channel Name:'), self)
        self.channel_name_input = LineEdit(self)
        self.channel_id_label = QLabel(self.tr('Channel ID:'), self)
        self.channel_id_input = LineEdit(self)

        self.init_ui()
        self.set_qss()

    def init_ui(self):
        self.vBoxLayout.removeWidget(self.contentLabel)
        self.vBoxLayout.removeItem(self.textLayout)

        self.channel_name_label.setContentsMargins(10, 10, 10, 0)
        self.channel_name_input.setContentsMargins(10, 0, 10, 0)
        self.channel_id_label.setContentsMargins(10, 10, 10, 0)
        self.channel_id_input.setContentsMargins(10, 0, 10, 0)

        self.vBoxLayout.insertSpacing(0, 10)
        self.vBoxLayout.insertWidget(0, self.channel_id_input)
        self.vBoxLayout.insertWidget(0, self.channel_id_label)
        self.vBoxLayout.insertWidget(0, self.channel_name_input)
        self.vBoxLayout.insertWidget(0, self.channel_name_label)

        self.setFixedSize(300, 300)

    def set_qss(self):
        self.channel_name_label.setObjectName("contentLabel")
        self.channel_id_label.setObjectName("contentLabel")

        with open(f'{BASE_DIR}/res/qss/light/video_card.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


class ToolButton(QToolButton):
    """ Tool button """

    def __init__(self, icon, size: tuple, iconSize: tuple, parent=None):
        super().__init__(parent=parent)
        self.isPressed = False
        self._icon = icon
        self._iconSize = iconSize
        self.setFixedSize(*size)

    def mousePressEvent(self, e):
        self.isPressed = True
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.isPressed = False
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setOpacity(0.63 if self.isPressed else 1)
        w, h = self._iconSize
        drawIcon(self._icon, painter, QRectF(
            (self.width() - w) / 2, (self.height() - h) / 2, w, h))


class ChannelItem(QWidget):
    """ Folder item """

    removed = pyqtSignal(QWidget)

    def __init__(self, channel: dict, parent=None):
        super().__init__(parent=parent)
        self.channel = channel
        self.hBoxLayout = QHBoxLayout(self)
        self.name_label = QLabel(channel['name'], self)
        self.removeButton = ToolButton(FIF.CLOSE, (39, 29), (12, 12), self)

        self.setFixedHeight(53)
        self.hBoxLayout.setContentsMargins(48, 0, 60, 0)
        self.hBoxLayout.addWidget(self.name_label, 0, Qt.AlignLeft)
        self.hBoxLayout.addSpacing(16)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.removeButton, 0, Qt.AlignRight)
        self.hBoxLayout.setAlignment(Qt.AlignVCenter)

        self.removeButton.clicked.connect(
            lambda: self.removed.emit(self))


class DistListSettingCard(ExpandSettingCard):
    channel_changed_signal = pyqtSignal(list)

    def __init__(self, config_item: ConfigItem, title: str, content: str = None, parent=None):
        super().__init__(QIcon(f'{BASE_DIR}/res/icons/link.svg'), title, content, parent)
        self.configItem = config_item
        self.add_channel_btn = PushButton(self.tr('Add'), self)

        self.channels = qconfig.get(config_item).copy()
        self.__initWidget()

    def __initWidget(self):
        self.addWidget(self.add_channel_btn)

        # initialize layout
        self.viewLayout.setSpacing(0)
        self.viewLayout.setAlignment(Qt.AlignTop)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        for channel in self.channels:
            self.__add_channel_item(channel['name'], channel['channel_id'])

        self.add_channel_btn.clicked.connect(self.__show_channel_dialog)

    def __show_channel_dialog(self):
        """ show folder dialog """
        w = ChannelDialog(self)
        w.setTitleBarVisible(False)
        if w.exec():
            channel = {'name': w.channel_name_input.text(), 'channel_id': w.channel_id_input.text()}
            if not channel or channel in self.channels:
                return

            self.__add_channel_item(channel['name'], channel['channel_id'])
            self.channels.append(channel)
            qconfig.set(self.configItem, self.channels)
            self.channel_changed_signal.emit(self.channels)

    def __add_channel_item(self, name: str, channel_id: str):
        """ add folder item """
        item = ChannelItem({'name': name, 'channel_id': channel_id}, self.view)
        item.removed.connect(self.__show_confirm_dialog)
        self.viewLayout.addWidget(item)
        self._adjustViewSize()

    def __show_confirm_dialog(self, item: ChannelItem):
        """ show confirm dialog """
        name = item.name_label.text()
        title = self.tr('Are you sure you want to delete the channel?')
        content = self.tr("If you delete the ") + f'"{name}"' + self.tr(
            " channel and remove it from the list, the channel will no longer appear in the list")
        w = Dialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.__remove_folder(item))
        w.exec_()

    def __remove_folder(self, item: ChannelItem):
        """ remove folder """
        for channel in self.channels:
            if channel['channel_id'] == item.channel['channel_id']:
                self.channels.remove(item.channel)
                self.viewLayout.deleteWidget(item)
                self._adjustViewSize()

                self.channel_changed_signal.emit(self.channels)
                qconfig.set(self.configItem, self.channels)

                return


class UploadCard(QFrame):
    del_signal = pyqtSignal(str)

    def __init__(self, title: str, path: str, parent=None):
        super().__init__(parent=parent)
        self.title = title
        self.path = path

        self.title_input = LineEdit(self)
        self.title_input.setText(title)
        self.path_label = QLabel(TextWrap.wrap(self.path, 55, True)[0], self)

        self.del_btn = qfluentwidgets.ToolButton(FIF.DELETE, self)

        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout()

        self.setFixedHeight(85)
        self.vBoxLayout.setSpacing(5)
        self.vBoxLayout.setContentsMargins(10, 0, 10, 0)
        self.hBoxLayout.setSpacing(5)
        self.hBoxLayout.setContentsMargins(5, 0, 5, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addSpacing(5)
        self.vBoxLayout.addWidget(self.title_input)
        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.vBoxLayout.addSpacing(5)
        self.vBoxLayout.addStretch(1)

        self.hBoxLayout.addWidget(self.path_label, stretch=5)
        self.hBoxLayout.addSpacing(5)
        self.hBoxLayout.addWidget(self.del_btn, stretch=1, alignment=Qt.AlignBottom)
        self.del_btn.clicked.connect(self.on_del_btn_clicked)

        self.set_qss()

    def set_qss(self):
        self.path_label.setObjectName('contentLabel')

        with open(f'{BASE_DIR}/res/qss/light/video_card.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def on_del_btn_clicked(self):
        self.del_signal.emit(self.objectName())
