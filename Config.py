from enum import Enum

from PyQt5.QtCore import QLocale
from qfluentwidgets import qconfig, OptionsConfigItem, OptionsValidator, EnumSerializer, QConfig, ConfigItem, \
    RangeConfigItem, RangeValidator, BoolValidator, ConfigSerializer, FolderValidator

VERSION = '6.0.0'


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = "zh_CN"
    CHINESE_TRADITIONAL = "hk"
    ENGLISH = "en"
    AUTO = "Auto"


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    reprint_id = ConfigItem(
        'VideoSetting', 'Reprint', 'Aye10032'
    )
    proxy_enable = ConfigItem(
        "VideoSetting", "EnableProxy", True, BoolValidator())
    proxy = ConfigItem(
        'VideoSetting', 'Proxy', 'http://127.0.0.1:1080'
    )
    thread = RangeConfigItem(
        "VideoSetting", "Thread", 4, RangeValidator(1, 16))
    download_folder = ConfigItem(
        "VideoSetting", "Download", "download", FolderValidator())

    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)


cfg = Config()
qconfig.load('res/config.json', cfg)
