# -*- mode: python -*-

block_cipher = None


a = Analysis(['F:\\软件\\youtubedownload\\YouTubeDownLoad\\MainRun.py'],
             pathex=['F:\\软件\\youtubedownload\\YouTubeDownLoad'],
             binaries=[('F:\\软件\\youtubedownload\\YouTubeDownLoad/res/aria2c.exe', 'lib')],
             datas=[('F:\\软件\\youtubedownload\\YouTubeDownLoad/res/HELP', 'res'), ('F:\\软件\\youtubedownload\\YouTubeDownLoad/res/LICENCE', 'res'), ('F:\\软件\\youtubedownload\\YouTubeDownLoad/res/copy.png', 'res'), ('F:\\软件\\youtubedownload\\YouTubeDownLoad/res/search.png', 'res'), ('F:\\软件\\youtubedownload\\YouTubeDownLoad\\res\\logo.ico', 'res'), ('F:\\软件\\youtubedownload\\YouTubeDownLoad\\res\\aria2c.exe', 'res')],
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
          name='MainRun',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True , icon='F:\\软件\\youtubedownload\\YouTubeDownLoad\\res\\logo.ico')
