import html
import json
import os
import re
from multiprocessing import Process

import pyperclip
import requests
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

if not os.path.exists('Download_Video'):
    os.mkdir('Download_Video')

if not os.path.exists('res'):
    os.mkdir('res')


class window(wx.Frame):
    uploader = ''
    upload_date = ''
    title = ''
    description = ''
    URL = ''
    thumbnail = ''

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, '半自动搬运工具@Aye10032 V1.0', size=(600, 700),
                          style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX)

        self.Center()
        icon = wx.Icon('res/logo.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        panel = wx.Panel(self)

        font1 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '微软雅黑')  # 标题字体
        font2 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

        t1 = wx.StaticText(panel, -1, '个人设置', (0, 5), (600, -1), wx.ALIGN_CENTER)
        t1.SetFont(font1)

        # --------------------------------- 搬运者ID及线程设置部分 ---------------------------------

        wx.StaticText(panel, -1, '搬运者ID：', (22, 35))
        self.yourname = wx.TextCtrl(panel, -1, name, (90, 30), (130, 23))

        wx.StaticText(panel, -1, '下载线程：', (300, 35))
        listc = ['1', '2', '4', '6', '8', '16']
        self.xiancheng = wx.ComboBox(panel, -1, value=num, pos=(370, 30), size=(80, 23),
                                     choices=listc)

        # --------------------------------- 代理设置部分 ---------------------------------

        self.usebtn = wx.CheckBox(panel, -1, '使用代理', (320, 65), style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.usePor, self.usebtn)
        wx.StaticText(panel, -1, '代理IP：', (22, 65))
        self.ipaddress = wx.TextCtrl(panel, -1, soc, (90, 62), (170, 23))

        if useProxy:
            self.usebtn.SetValue(True)
        else:
            self.usebtn.SetValue(False)
            self.ipaddress.SetEditable(False)

        self.savebtn = button = wx.Button(panel, label='保存', pos=(430, 60), size=(60, 23))
        self.Bind(wx.EVT_BUTTON, self.save, button)

        wx.StaticText(panel, -1, '——————————————————————————————————————————————————————————————————',
                      (0, 85)).SetForegroundColour('gray')

        # --------------------------------- 源视频链接部分 ---------------------------------

        wx.StaticText(panel, -1, '视频链接：', (22, 110))
        self.youtubeURL = wx.TextCtrl(panel, -1, '', (90, 105), (350, 23))

        pic = wx.Image('res/download.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.startbtn = wx.BitmapButton(panel, -1, pic, pos=(470, 102), size=(70, 32))
        self.Bind(wx.EVT_BUTTON, self.start, self.startbtn)

        # --------------------------------- 视频信息部分 ---------------------------------

        wx.StaticText(panel, -1, '标题：', (22, 150))
        self.youtubeTitle = wx.TextCtrl(panel, -1, '【MC】【】', (90, 145), (450, 23))
        wx.StaticText(panel, -1, '视频来源：', (22, 180))
        self.youtubeLink = wx.TextCtrl(panel, -1, '转自 有能力请支持原作者', (90, 175), (450, 23))
        wx.StaticText(panel, -1, '视频简介', (0, 210), (520, -1), wx.ALIGN_CENTER)
        self.youtubesubmit = wx.TextCtrl(panel, -1, '作者：\r\n发布时间：\r\n搬运：\r\n视频摘要：\r\n原简介翻译：\r\n存档：\r\n其他外链：', (20, 240),
                                         (500, 400),
                                         style=wx.TE_MULTILINE)

        pic2 = wx.Image('res/copy.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.CopyLink = wx.BitmapButton(panel, -1, pic2, pos=(535, 430), size=(35, 35))
        self.Bind(wx.EVT_BUTTON, self.Copy, self.CopyLink)

    def usePor(self, event):
        if self.usebtn.GetValue():
            self.ipaddress.SetEditable(True)
            useProxy = True
        else:
            self.ipaddress.SetEditable(False)
            useProxy = False

    def save(self, event):
        soc = self.ipaddress.GetValue()
        useProxy = self.usebtn.GetValue()
        name = self.yourname.GetValue()
        xiancheng = self.xiancheng.GetValue()

        with open('res/config.json', 'w') as c:
            config['useProxy'] = useProxy
            config['name'] = name
            config['ipaddress'] = soc
            config['xiancheng'] = xiancheng
            json.dump(config, c, indent=4)

    def start(self, event):
        if self.youtubeURL.GetValue() == '':
            box = wx.MessageDialog(None, '未填入视频链接！', '警告', wx.OK | wx.ICON_EXCLAMATION)
            box.ShowModal()
        else:
            URL = self.youtubeURL.GetValue()
            self.updatemesage(URL)
            self.Update()
            # self.req_api(URL)
            # self.dl(URL)
            p1 = Process(target=dl)
            p2 = Process(target=req_api)
            p1.start()
            p2.start()

    def Copy(self, event):
        msg = self.youtubesubmit.GetValue()
        pyperclip.copy(msg)

    # --------------------------------- 更新信息 ---------------------------------
    def updatemesage(self, url):

        ydl_opts = {}

        if useProxy:
            ydl_opts = {
                'proxy': soc
            }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

            self.uploader = info_dict.get("uploader", None)
            self.upload_date = info_dict.get("upload_date", None)
            self.title = info_dict.get('title', None)
            self.thumbnail = info_dict.get('thumbnail', None)
            self.description = info_dict.get('description', None)

            self.youtubeTitle.SetValue('【MC】' + self.title + '【' + self.uploader + '】')
            self.youtubeLink.SetValue('转自' + url + ' 有能力请支持原作者')
            submit = '作者：' + self.uploader + '\r\n发布时间：' + self.upload_date + '\r\n搬运：' + name + '\r\n视频摘要：\r\n原简介翻译：' + self.description + '\r\n存档：\r\n其他外链：'
            self.youtubesubmit.SetValue(submit)

        downloadpath = 'Download_video/' + self.title.replace(':', '').replace('.', ' ').replace('|', ' ').replace(
            '\\', ' ').replace('/', ' ') + '/%(title)s.%(ext)s'
        dlpath = 'Download_video/' + self.title.replace(':', '').replace('.', ' ').replace('|', ' ').replace('\\',
                                                                                                             ' ').replace(
            '/', ' ')
        with open('res/temp.json', 'w') as c:
            config2['url'] = url
            config2['downloadpath'] = downloadpath
            config2['dlpath'] = dlpath
            json.dump(config2, c, indent=4)


# --------------------------------- 下载视频&封面 ---------------------------------
def dl():
    path = config2['downloadpath']
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


# --------------------------------- 下载字幕 ---------------------------------
def req_api():
    api_url = 'https://api.zhuwei.me/v1/captions/'
    v_url = config2['url']
    dlpath = config2['dlpath']
    have_sub = requests.get(api_url + v_url[-11:] + '?' + 'api-key=' + token).json()

    if have_sub['meta']['code'] == 200:
        res = have_sub['response']['captions']
        sub_title = res['title']
        sub_list = res['available_captions']

        find = False
        for i in sub_list:

            if i['language'] in config['single_language']:
                print('Find （' + sub_title + '） 【' + i['language'] + '】 subtitle!')

                sub_url = i['caption_content_url'] + '?api-key=' + token \
                          + ('&multilanguage=multilanguage' if config['multilanguage'] else '') \
                          + ('&notimeline=notimeline' if config['notimeline'] else '')

                # 获取字幕url数据
                sub_res = requests.get(sub_url)
                sub_content = sub_res.json().get('contents').get('content')

                # 写入字幕文件
                if not os.path.exists(dlpath):
                    os.mkdir(dlpath)

                if os.name == 'nt':

                    with open(dlpath + '/%s.srt' % re.sub('[\/:?"*<>|]', '-', html.unescape(sub_title)),
                              'w') as sub_file:
                        sub_file.write(html.unescape(sub_content))
                else:
                    with open(dlpath + '/%s.srt' % html.unescape(sub_title).replace('/', '-'),
                              'w') as sub_file:
                        sub_file.write(html.unescape(sub_content))
                print('Download 【' + sub_title + '.srt】 complete!')

                find = True
                break

        if find:
            print('Success find ' + i['language'] + ' subtitle!')
        else:
            print('Can\'t find ' + i['language'] + ' subtitle!')

    else:
        print('Can\'t find ' + v_url + ' sub! check video id!')


if __name__ == '__main__':
    app = wx.App()
    frame = window(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
