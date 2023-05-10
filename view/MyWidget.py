from typing import Union

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QGridLayout, QTableWidgetItem, QFrame, \
    QHBoxLayout
from qfluentwidgets import SettingCard, FluentIconBase, Slider, qconfig, LineEdit, TableWidget, \
    TextWrap, PixmapLabel, ExpandLayout
from qfluentwidgets.components.dialog_box.dialog import Dialog

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
        signal_bus.switch2_download_signal.emit(self.path)

    def set_qss(self):
        self.title_label.setObjectName('titleLabel')
        self.content_label.setObjectName('contentLabel')

        with open(f'res/qss/light/video_card.qss', encoding='utf-8') as f:
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

        with open(f'res/qss/light/video_card.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
