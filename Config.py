from enum import Enum

from qfluentwidgets import qconfig, OptionsConfigItem, OptionsValidator, EnumSerializer, QConfig

VERSION = '6.0.0'


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = "zh_CN"
    CHINESE_TRADITIONAL = "hk"
    ENGLISH = "en"
    AUTO = "Auto"


class Config(QConfig):
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), EnumSerializer(Language), restart=True)


cfg = Config()
qconfig.load('res/config.json', cfg)
