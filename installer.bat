"C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python36_64\Scripts\pyinstaller" ^
    -F -w ^
    --noconfirm --log-level=WARN ^
    --onefile --nowindow ^
    --add-data="F:\软件\youtubedownload\YouTubeDownLoad/res/HELP;." ^
    --add-data="F:\软件\youtubedownload\YouTubeDownLoad/res/LICENCE;." ^
    --add-data="F:\软件\youtubedownload\YouTubeDownLoad/res/copy.png;img" ^
    --add-data="F:\软件\youtubedownload\YouTubeDownLoad/res/search.png;img" ^
    --add-binary="F:\软件\youtubedownload\YouTubeDownLoad/res/aria2c.exe;lib" ^
    --icon=F:\软件\youtubedownload\YouTubeDownLoad/res/logo.ico ^
    F:\软件\youtubedownload\YouTubeDownLoad\MainRun.py


pause