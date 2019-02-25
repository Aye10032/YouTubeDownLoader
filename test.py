import json

import wx
import wx.grid as gridlib
import youtube_dl

format_code, extension, resolution, format_note, file_size = [], [], [], [], []
with open('res/config.json', 'r') as conf:
    config = json.load(conf)

with open('res/temp.json', 'r') as conf2:
    config2 = json.load(conf2)
    config2['vidoecode'] = 0
    config2['audiocode'] = 0


def updatemesage(url):
    ydl_opts = {}

    if config['useProxy']:
        ydl_opts = {
            'proxy': config['ipaddress']
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        video = ydl.extract_info(url, download=False)

        formats = video.get('formats')
        file_count = len(formats)

        with open('res/temp.json', 'w') as c:
            config2['count'] = file_count
            json.dump(config2, c, indent=4)

        for f in formats:
            format_code.append(f.get('format_id'))
            extension.append(f.get('ext'))
            resolution.append(ydl.format_resolution(f))
            format_note.append(f.get('format_note'))
            file_size.append(f.get('filesize'))


class TestFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "视频格式", size=(505, 400), style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX)
        icon = wx.Icon('res/logo.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.Center()
        self.grid = SimpleGrid(self)


class SimpleGrid(gridlib.Grid):
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent)

        count = config2['count']
        self.CreateGrid(count, 5)
        self.SetRowLabelSize(30)
        self.SetColSize(col=2, width=100)
        self.SetColSize(col=3, width=100)

        self.EnableEditing(False)
        self.DisableColResize(False)
        self.DisableRowResize(False)

        self.SetColLabelValue(0, "代号")
        self.SetColLabelValue(1, "格式")
        self.SetColLabelValue(2, "描述")
        self.SetColLabelValue(3, "编码信息")
        self.SetColLabelValue(4, "文件大小")
        self.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        for i in range(count):
            self.SetCellValue(i, 0, format_code[i])
            self.SetCellValue(i, 1, extension[i])
            self.SetCellValue(i, 2, resolution[i])
            self.SetCellValue(i, 3, format_note[i])
            self.SetCellValue(i, 4, str(file_size[i]))

        # 左单击
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)

    def OnCellLeftClick(self, evt):
        a = "%d" % (evt.GetRow())
        i = int(a)

        with open('res/temp.json', 'w') as c:
            if resolution[i] == 'audio only':
                config2['audiocode'] = format_code[i]
            else:
                config2['vidoecode'] = format_code[i]
            json.dump(config2, c, indent=4)

        print(format_code[i])
        evt.Skip()


if __name__ == '__main__':
    updatemesage('https://youtu.be/syYQxdIZ2Po')
    app = wx.App()
    frame = TestFrame(None)
    frame.Show()
    app.MainLoop()
