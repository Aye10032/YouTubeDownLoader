import json
from multiprocessing import Process

import wx
import youtube_dl

with open('res/config.json', 'r') as conf:
    config = json.load(conf)
    name = config['name']
    soc = config['ipaddress']
    useProxy = config['useProxy']
    num = config['xiancheng']
    token = config['token']

with open('res/temp.json', 'r') as conf2:
    config2 = json.load(conf2)


class bucky(wx.Frame):

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Frame aka window', size=(300, 200))

        panel = wx.Panel(self)
        button = wx.Button(panel, label='exit', pos=(130, 10), size=(60, 60))

        self.Bind(wx.EVT_BUTTON, self.closebutton, button)

    def closebutton(self, event):
        url = 'https://youtu.be/JGv9KhsAHWI'
        path = 'Download_Video/res/%(title)s.%(ext)s'
        with open('res/temp.json', 'w') as c:
            config2['url'] = url
            config2['path'] = path
            json.dump(config2, c, indent=4)
        p1 = Process(target=dl)
        p1.start()


def dl():
    path = config2['path']
    url = config2['url']

    ydl_opts = {}
    if useProxy:
        ydl_opts = {
            'proxy': soc,
            "writethumbnail": True,
            "external_downloader_args": ['--max-connection-per-server', num, '--min-split-size', '1M'],
            "external_downloader": "aria2c",
            'outtmpl': path
        }
    else:
        ydl_opts = {
            "writethumbnail": True,
            "external_downloader_args": ['--max-connection-per-server', num, '--min-split-size', '1M'],
            "external_downloader": "aria2c",
            'outtmpl': path
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


if __name__ == '__main__':
    app = wx.App()
    frame = bucky(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
