import os
import sys

BASE_DIR = ""
if getattr(sys, 'frozen', False):
    # we are running in a |PyInstaller| bundle
    BASE_DIR = sys._MEIPASS
else:
    # we are running in a normal Python environment
    BASE_DIR = os.path.dirname(__file__)
