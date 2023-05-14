from PyQt5.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    """ Signal bus """

    path2_download_signal = pyqtSignal(str)
    url2_download_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)


signal_bus = SignalBus()
