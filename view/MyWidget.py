from typing import Union

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QSizePolicy, QGridLayout
from qfluentwidgets import SettingCard, FluentIconBase, Slider, qconfig, FluentStyleSheet, LineEdit
from qfluentwidgets.components.dialog_box.dialog import Ui_MessageBox, Dialog
from qframelesswindow import FramelessDialog


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
