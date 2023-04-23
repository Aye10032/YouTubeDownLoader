from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QSplitter, QGridLayout, QLabel, QPushButton, QListWidget, QWidget, QPlainTextEdit, \
    QVBoxLayout


class EditWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Vertical)
        splitter.setSizes([4, 1])

        main_layout = QGridLayout()

        # 在 grid_layout 中添加其他组件
        label1 = QLabel("Label1")
        main_layout.addWidget(label1, 0, 0)

        push_button1 = QPushButton("Push Button 1")
        main_layout.addWidget(push_button1, 0, 1)

        list_widget1 = QListWidget()
        main_layout.addWidget(list_widget1, 1, 0, 1, 2)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        splitter.addWidget(main_widget)

        log_output = QPlainTextEdit()
        splitter.addWidget(log_output)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(splitter)

        self.set_qss()

    def set_qss(self):
        with open(f'res/qss/light/edit_widget.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
