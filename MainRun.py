# -*- coding:utf-8 -*-
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
        wx.Frame.__init__(self, parent, id, '半自动搬运工具@Aye10032 V1.0', size=(600, 720),
                          style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU)

        self.Center()
        icon = wx.Icon('res/logo.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        panel = wx.Panel(self)

        font1 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '微软雅黑')  # 标题字体

        t1 = wx.StaticText(panel, -1, '个人设置', (0, 5), (600, -1), wx.ALIGN_CENTER)
        t1.SetFont(font1)

        self.Bind(wx.EVT_CLOSE, self.closewindow)

        # --------------------------------- 菜单栏部分 ---------------------------------
        menubar = wx.MenuBar()
        first = wx.Menu()
        help = first.Append(wx.NewId(), '帮助', '软件使用帮助')
        about = first.Append(wx.NewId(), '关于', '软件信息')
        menubar.Append(first, '其他')
        self.Bind(wx.EVT_MENU, self.help, help)
        self.Bind(wx.EVT_MENU, self.about, about)
        self.SetMenuBar(menubar)

        # --------------------------------- 搬运者ID及线程设置部分 ---------------------------------

        wx.StaticText(panel, -1, '搬运者ID：', (22, 35))
        self.yourname = wx.TextCtrl(panel, -1, config['name'], (90, 30), (130, 23))

        wx.StaticText(panel, -1, '下载线程：', (300, 35))
        listc = ['1', '2', '4', '6', '8', '16']
        self.xiancheng = wx.ComboBox(panel, -1, value=config['xiancheng'], pos=(370, 30), size=(80, 23),
                                     choices=listc)

        # --------------------------------- 代理设置部分 ---------------------------------

        self.usebtn = wx.CheckBox(panel, -1, '使用代理', (320, 65), style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.usePor, self.usebtn)
        wx.StaticText(panel, -1, '代理IP：', (22, 65))
        self.ipaddress = wx.TextCtrl(panel, -1, config['ipaddress'], (90, 62), (170, 23))

        if config['useProxy']:
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

    def about(self, event):
        frame2.Show(True)

    def help(self, event):
        frame1.Show(True)

    def closewindow(self, event):
        self.Destroy()

    # --------------------------------- 更新信息 ---------------------------------
    def updatemesage(self, url):

        ydl_opts = {}

        if config['useProxy']:
            ydl_opts = {
                'proxy': config['ipaddress']
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
            submit = '作者：' + self.uploader + '\r\n发布时间：' + self.upload_date + '\r\n搬运：' + config[
                'name'] + '\r\n视频摘要：\r\n原简介翻译：' + self.description + '\r\n存档：\r\n其他外链：'
            self.youtubesubmit.SetValue(submit)

        downloadpath = 'Download_video/' + self.title.replace(':', '').replace('.', '').replace('|', '').replace(
            '\\', '').replace('/', '') + '/%(title)s.%(ext)s'
        dlpath = 'Download_video/' + self.title.replace(':', '').replace('.', '').replace('|', '').replace('\\',
                                                                                                           '').replace(
            '/', '')
        with open('res/temp.json', 'w') as c:
            config2['url'] = url
            config2['downloadpath'] = downloadpath
            config2['dlpath'] = dlpath
            json.dump(config2, c, indent=4)


# --------------------------------- 下载视频&封面 ---------------------------------
def dl():
    path = config2['downloadpath']
    url = config2['url']
    print(path)
    ydl_opts = {}
    if config['useProxy']:
        ydl_opts = {
            'proxy': config['ipaddress'],
            "writethumbnail": True,
            "external_downloader_args": ['--max-connection-per-server', config['xiancheng'], '--min-split-size', '1M'],
            "external_downloader": "aria2c",
            'outtmpl': path
        }
    else:
        ydl_opts = {
            "writethumbnail": True,
            "external_downloader_args": ['--max-connection-per-server', config['xiancheng'], '--min-split-size', '1M'],
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
    token = config['token']
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


# --------------------------------- 帮助界面 ---------------------------------
class helpwin(wx.Frame):
    def __init__(self, parent, id, titletext, text1):
        wx.Frame.__init__(self, parent, id, titletext, size=(500, 370))
        panel = wx.Panel(self)

        font1 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '微软雅黑')  # 标题字体

        title = wx.StaticText(panel, -1, text1, (0, 15), (500, -1), wx.ALIGN_CENTER)
        title.SetFont(font1)

        text = "Youtube Download\r\n\r\n红石科技搬运组工具软件，用于自动下载视频，视频封面，字幕，同时规范简介格式。\r\n字幕组空间：https://space.bilibili.com/1311124\r\n作者：Aye10032\r\n\r\n依赖环境\r\nWindows系统；\r\npython3：https://www.python.org/downloads/;\r\n代理软件;\r\n\r\n使用方法\r\n首次运行先运行buildEnvironment.bat，自动配置环境。\r\n或者你也可以选择自行配置环境：\r\npip install pyperclip requests youtube_dl\r\npip install -U wxPython\r\n之后再将本文件夹中的res文件夹加入系统环境变量的path变量中即可。\r\n\r\n正常运行直接双击运行run.bat即可\r\n\r\n界面设置\r\n\r\n设置搬运者ID，是否适用代理（如果代理是部署在路由器上选择不使用即可），以及代理IP，代理必须是以http：//开头，之后跟上IP及端口号即可。这里编辑完毕后点击保存下次运行软件时会自动载入配置。\r\n输入视频链接，点击下载按钮即可开始。运行结束后可以点击按钮复制简介部分的文字。"

        msg = wx.TextCtrl(panel, -1, text, (10, 40), (465, 250), style=wx.TE_MULTILINE)
        msg.SetEditable(False)

        button = wx.Button(panel, label='OK', pos=(220, 300), size=(60, 20))
        self.Bind(wx.EVT_BUTTON, self.closewindow, button)

    def closewindow(self, event):
        self.Destroy()


# --------------------------------- 关于界面 ---------------------------------
class aboutwin(wx.Frame):
    def __init__(self, parent, id, titletext, text1):
        wx.Frame.__init__(self, parent, id, titletext, size=(500, 370))
        panel = wx.Panel(self)

        font1 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '微软雅黑')  # 标题字体

        title = wx.StaticText(panel, -1, text1, (0, 15), (500, -1), wx.ALIGN_CENTER)
        title.SetFont(font1)

        text = '本软件使用了YouTube_dl库进行编写\r\n字幕下载采用了https://zhuwei.me/y2b/ 的字幕下载接口\r\n作者Aye10032,下载地址：https://github.com/Aye10032/YouTubeDownLoad/releases\r\n本软件和YouTube没有任何关系\r\n仅供学习、参考使用'

        msg = wx.TextCtrl(panel, -1, text, (10, 40), (465, 250), style=wx.TE_MULTILINE)
        msg.SetEditable(False)

        button = wx.Button(panel, label='OK', pos=(220, 300), size=(60, 20))
        self.Bind(wx.EVT_BUTTON, self.closewindow, button)

    def closewindow(self, event):
        self.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = window(parent=None, id=-1)
    frame1 = helpwin(parent=frame, id=-1, titletext='help', text1='软件帮助')
    frame2 = aboutwin(parent=frame, id=-1, titletext='about', text1='关于')
    frame.Show()
    frame1.Show(False)
    frame2.Show(False)
    frame1.Center()
    frame2.Center()
    app.MainLoop()
