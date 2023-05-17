# -*- mode: python -*-

block_cipher = None


a = Analysis(['D:\\program\\python\\YouTubeDownLoader\\Main.py'],
             pathex=['D:\\program\\python\\YouTubeDownLoader'],
             binaries=[],
             datas=[
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\key.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\link.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\logo.ico', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\number.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\play.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\server.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\lang\\zh_CN.qm', 'res\\lang'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\lang\\zh_CN.ts', 'res\\lang'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\light\\download_interface.qss', 'res\\qss\\light'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\light\\main.qss', 'res\\qss\\light'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\light\\scroll_interface.qss', 'res\\qss\\light'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\light\\upload_interface.qss', 'res\\qss\\light'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\light\\video_card.qss', 'res\\qss\\light'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\LICENCE.html', 'res'),
             ],
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
          console=False,
          icon='D:\\program\\python\\YouTubeDownLoader\\res\icons\\logo.ico')