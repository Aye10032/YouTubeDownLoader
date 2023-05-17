from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme, qconfig

from Path import BASE_DIR


class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    MAIN_WINDOW = 'main'
    DOWNLOAD = 'download_interface'
    SCROLL = 'scroll_interface'
    UPLOAD = 'upload_interface'
    CARD = 'video_card'

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme

        return f"{BASE_DIR}/res/qss/{theme.value.lower()}/{self.value}.qss"
