# -*- mode: python -*-

block_cipher = None


a = Analysis(['D:\\program\\python\\YouTubeDownLoader\\MainRun.py'],
             pathex=['D:\\program\\python\\YouTubeDownLoader'],
             binaries=[],
             datas=[
             ('D:\\program\\python\\YouTubeDownLoader/res/HELP', 'res'),
             ('D:\\program\\python\\YouTubeDownLoader/res/LICENCE', 'res'),
             ('D:\\program\\python\\YouTubeDownLoader/res/copy.png', 'res'),
             ('D:\\program\\python\\YouTubeDownLoader/res/search.png', 'res'),
             ('D:\\program\\python\\YouTubeDownLoader/res/play.png', 'res'),
             ('D:\\program\\python\\YouTubeDownLoader/res/translate.png', 'res'),
             ('D:\\program\\python\\YouTubeDownLoader\\res\\logo.ico', 'res'),
             ('D:\\program\\python\\YouTubeDownLoader\\res\\aria2c.exe', 'res')],
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
          name='YouTubeDownLoader_V.exe',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True, icon='D:\\program\\python\\YouTubeDownLoader\\res\\logo.ico')