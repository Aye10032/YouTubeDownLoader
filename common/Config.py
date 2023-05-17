import time
from enum import Enum

from PyQt5.QtCore import QLocale
from qfluentwidgets import qconfig, OptionsConfigItem, OptionsValidator, QConfig, ConfigItem, \
    RangeConfigItem, RangeValidator, BoolValidator, ConfigSerializer, FolderValidator

from Path import BASE_DIR

VERSION = '6.0.0'
TEMP_PATH = f'config/temp.json'
LICENCE_PATH = f'{BASE_DIR}/res/LICENCE.html'
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

LOG_PATH = 'log'
LOG_NAME = time.strftime("%Y-%m-%d", time.localtime())

INFO = 0
SUCCESS = 1
WARNING = 2


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    reprint_id = ConfigItem(
        'DownloadSetting', 'Reprint', 'Aye10032'
    )
    proxy_enable = ConfigItem(
        "DownloadSetting", "EnableProxy", True, BoolValidator())

    proxy = ConfigItem(
        'DownloadSetting', 'Proxy', 'http://127.0.0.1:1080'
    )
    thread = RangeConfigItem(
        "DownloadSetting", "Thread", 4, RangeValidator(1, 16))
    download_folder = ConfigItem(
        "DownloadSetting", "DownloadFolder", "download", FolderValidator())
    auto_quality = ConfigItem(
        "DownloadSetting", "AutoQuality", True, BoolValidator())

    api_token = ConfigItem(
        "AdvancedSetting", "ApiToken", "", restart=True
    )
    subscribe_channels = ConfigItem(
        "AdvancedSetting", "SubscribeChannels", [])
    api_server = ConfigItem(
        "AdvancedSetting", "ApiServer", "", restart=True
    )

    language = OptionsConfigItem(
        "System", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)


cfg = Config()
qconfig.load(f'config/config.json', cfg)
