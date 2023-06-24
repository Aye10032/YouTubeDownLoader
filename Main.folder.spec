# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['D:\\program\\python\\YouTubeDownLoader\\Main.py'],
    pathex=['D:\\program\\python\\YouTubeDownLoader'],
    binaries=[],
    datas=[
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\key_black.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\key_white.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\link_black.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\link_white.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\logo.ico', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\number_black.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\number_white.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\play_black.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\play_white.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\server_black.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\icons\\server_white.svg', 'res\\icons'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\lang\\zh_CN.qm', 'res\\lang'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\lang\\zh_CN.ts', 'res\\lang'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\light\\download_interface.qss', 'res\\qss\\light'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\light\\main.qss', 'res\\qss\\light'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\light\\scroll_interface.qss', 'res\\qss\\light'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\light\\upload_interface.qss', 'res\\qss\\light'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\light\\video_card.qss', 'res\\qss\\light'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\dark\\download_interface.qss', 'res\\qss\\dark'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\dark\\main.qss', 'res\\qss\\dark'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\dark\\scroll_interface.qss', 'res\\qss\\dark'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\dark\\upload_interface.qss', 'res\\qss\\dark'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\qss\\dark\\video_card.qss', 'res\\qss\\dark'),
              ('D:\\program\\python\\YouTubeDownLoader\\res\\LICENCE.html', 'res'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YouTubeDownLoader_V',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='D:\\program\\python\\YouTubeDownLoader\\res\icons\\logo.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Main',
)
