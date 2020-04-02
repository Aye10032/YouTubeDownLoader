# -*- mode: python -*-

block_cipher = None


a = Analysis(['D:\\program\\GitHub\\YouTubeDownLoad\\MainRun.py'],
             pathex=['D:\\program\\GitHub\\YouTubeDownLoad'],
             binaries=[],
             datas=[
             ('D:\\program\\GitHub\\YouTubeDownLoad/res/HELP', 'res'),
             ('D:\\program\\GitHub\\YouTubeDownLoad/res/LICENCE', 'res'),
             ('D:\\program\\GitHub\\YouTubeDownLoad/res/copy.png', 'res'),
             ('D:\\program\\GitHub\\YouTubeDownLoad/res/search.png', 'res'),
             ('D:\\program\\GitHub\\YouTubeDownLoad/res/play.png', 'res'),
             ('D:\\program\\GitHub\\YouTubeDownLoad/res/translate.png', 'res'),
             ('D:\\program\\GitHub\\YouTubeDownLoad\\res\\logo.ico', 'res'),
             ('D:\\program\\GitHub\\YouTubeDownLoad\\res\\aria2c.exe', 'res')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='YouTubeDownLoad_V.exe',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True, icon='D:\\program\\GitHub\\YouTubeDownLoad\\res\\logo.ico')