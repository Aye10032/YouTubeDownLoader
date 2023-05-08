from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget
from qfluentwidgets import ScrollArea, ExpandLayout


class LocalVideoInterface(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        self.scroll_area = ScrollArea(self)
        self.scroll_widget = QWidget(self)
        self.expand_layout = ExpandLayout(self.scroll_widget)


