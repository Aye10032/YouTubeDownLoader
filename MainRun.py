# -*- coding:utf-8 -*-
import html
import json
import os
import re
import sys
import threading
import webbrowser
from shutil import copy2

import pyperclip
import requests
import wx
import wx.grid as gridlib
import youtube_dl

# --------------------------------- 资源文件位置设置 ---------------------------------
basedir = ""
if getattr(sys, 'frozen', False):
    # we are running in a |PyInstaller| bundle
    basedir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    basedir = os.path.dirname(__file__)

VERSION = 'V3.0'
RES_PATH = 'res'
CONFIG_PATH = 'res/config.json'
TEMP_PATH = 'res/temp.json'
ARIA2C = 'aria2c.exe'
ARIA2C_PATH = basedir + '/res/aria2c.exe'
LOGO_PATH = basedir + '/res/logo.ico'
LICENCE_PATH = basedir + '/res/LICENCE'
HELP_PATH = basedir + "/res/HELP"
SEARCH_PATH = basedir + "/res/search.png"
COPY_PATH = basedir + "/res/copy.png"

# --------------------------------- 前置检查部分开始 ---------------------------------
if not os.path.exists(ARIA2C):
    copy2(ARIA2C_PATH, os.getcwd())

if not os.path.exists(RES_PATH):
    os.makedirs('res')
if not os.path.exists(CONFIG_PATH):
    default_config = {
        "name": "",
        "ipaddress": "http://127.0.0.1:1080",
        "useProxy": True,
        "xiancheng": "4",
        "token": "5460f6d462bc3067e27a3fbc8d732799339a7f85",
        "single_language": "en",
        "multilanguage": False,
        "notimeline": False,
        "videopro": True
    }
    with open(CONFIG_PATH, 'w+') as conf:
        json.dump(default_config, conf, indent=4)

if not os.path.exists(TEMP_PATH):
    default_config = {}
    with open(TEMP_PATH, 'w+') as conf:
        json.dump(default_config, conf, indent=4)
# --------------------------------- 前置检查部分结束 ---------------------------------
with open(CONFIG_PATH, 'r') as conf:
    config = json.load(conf)

with open(TEMP_PATH, 'r') as conf2:
    config2 = json.load(conf2)

if not os.path.exists('Download_Video'):
    os.mkdir('Download_Video')

if not os.path.exists('res'):
    os.mkdir('res')

format_code, extension, resolution, format_note, file_size = [], [], [], [], []

rootdir = 'Download_Video'
list = os.listdir(rootdir)
filelist = []


class window(wx.Frame):
    uploader = ''
    upload_date = ''
    title = ''
    description = ''
    URL = ''
    thumbnail = ''
    hasEdit = False
    menuBar = None

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, '半自动搬运工具@Aye10032 ' + VERSION, size=(600, 720),
                          style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU)

        self.Center()
        icon = wx.Icon(LOGO_PATH, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        with open(TEMP_PATH, 'w') as c:
            config2['audiocode'] = 0
            config2['vidoecode'] = 0
            json.dump(config2, c, indent=4)

        panel = wx.Panel(self)

        font1 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '微软雅黑')  # 标题字体

        t1 = wx.StaticText(panel, -1, '个人设置', (0, 5), (600, -1), wx.ALIGN_CENTER)
        t1.SetFont(font1)

        self.Bind(wx.EVT_CLOSE, self.closewindow)

        self.updateMenuBar()

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

        self.startbtn = wx.Button(panel, -1, '下载视频', pos=(470, 104), size=(70, 25))
        self.Bind(wx.EVT_BUTTON, self.start, self.startbtn)

        self.getbtn = wx.Button(panel, -1, '获取简介', pos=(470, 136), size=(70, 25))
        self.Bind(wx.EVT_BUTTON, self.get, self.getbtn)

        # --------------------------------- 质量代码部分 ---------------------------------
        self.highbtn = wx.CheckBox(panel, -1, '自定义视频质量   ', (13, 138), style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.provideo, self.highbtn)

        wx.StaticText(panel, -1, '格式代码：', (160, 138))
        self.qualitytext = wx.TextCtrl(panel, -1, '', (225, 135), (130, 23))

        if config['videopro']:
            self.highbtn.SetValue(True)
            self.qualitytext.SetEditable(True)
        else:
            self.highbtn.SetValue(False)
            self.qualitytext.SetEditable(False)

        pic1 = wx.Image(SEARCH_PATH, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.viewbtn = wx.BitmapButton(panel, -1, pic1, (370, 135), (23, 23))
        # self.loadbtn = wx.Button(panel, -1, '加载', (380, 135), (40, 23))
        self.Bind(wx.EVT_BUTTON, self.view, self.viewbtn)
        # self.Bind(wx.EVT_BUTTON, self.load, self.loadbtn)

        # --------------------------------- 视频信息部分 ---------------------------------

        wx.StaticText(panel, -1, '标题：', (22, 170))
        self.youtubeTitle = wx.TextCtrl(panel, -1, '【MC】【】', (90, 165), (450, 23))
        wx.StaticText(panel, -1, '视频来源：', (22, 200))
        self.youtubeLink = wx.TextCtrl(panel, -1, '转自 有能力请支持原作者', (90, 195), (450, 23))
        wx.StaticText(panel, -1, '视频简介', (0, 230), (520, -1), wx.ALIGN_CENTER)
        self.youtubesubmit = wx.TextCtrl(panel, -1, '作者：\r\n发布时间：\r\n搬运：\r\n视频摘要：\r\n原简介翻译：\r\n存档：\r\n其他外链：', (20, 260),
                                         (500, 395),
                                         style=wx.TE_MULTILINE)

        pic2 = wx.Image(COPY_PATH, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.CopyLink = wx.BitmapButton(panel, -1, pic2, pos=(535, 430), size=(35, 35))
        self.Bind(wx.EVT_BUTTON, self.Copy, self.CopyLink)

    def usePor(self, event):
        if self.usebtn.GetValue():
            self.ipaddress.SetEditable(True)
            useProxy = True
        else:
            self.ipaddress.SetEditable(False)
            useProxy = False

    def provideo(self, event):
        if self.highbtn.GetValue():
            self.qualitytext.SetEditable(True)
        else:
            self.qualitytext.SetEditable(False)

        with open(CONFIG_PATH, 'w') as c:
            config['videopro'] = self.highbtn.GetValue()
            json.dump(config, c, indent=4)

    def save(self, event):
        soc = self.ipaddress.GetValue()
        useProxy = self.usebtn.GetValue()
        name = self.yourname.GetValue()
        xiancheng = self.xiancheng.GetValue()

        with open(CONFIG_PATH, 'w+') as c:
            config['useProxy'] = useProxy
            config['name'] = name
            config['ipaddress'] = soc
            config['xiancheng'] = xiancheng
            json.dump(config, c, indent=4)

    def savefileevt(self, event):
        self.savefile()

    def savefile(self):

        if self.hasEdit:
            if not os.path.exists(config2['dlpath']):
                os.mkdir(config2['dlpath'])

            msgpath = config2['dlpath'] + '/msg.json'

            title = self.youtubeTitle.GetValue()
            link = self.youtubeLink.GetValue()
            submit = self.youtubesubmit.GetValue()

            msg = {
                "title": title,
                "link": link,
                "submit": submit
            }
            with open(msgpath, 'w') as msgwrite:
                json.dump(msg, msgwrite, indent=4)

        updateFilelist()

    def view(self, event):
        with open(TEMP_PATH, 'w') as c:
            config2['url'] = self.youtubeURL.GetValue()
            json.dump(config2, c, indent=4)
        self.updatemesage()
        self.hasEdit = True
        frame3 = QualityFrame(parent=frame)
        frame3.Show(True)

    def load(self, event):
        msg = str(config2['vidoecode']) + '+' + str(config2['audiocode'])
        self.qualitytext.SetValue(msg)

    def get(self, event):
        if self.youtubeURL.GetValue() == '':
            box = wx.MessageDialog(None, '未填入视频链接！', '警告', wx.OK | wx.ICON_EXCLAMATION)
            box.ShowModal()
        else:
            URL = self.youtubeURL.GetValue()
            self.updatemesage()
            self.Update()
        self.hasEdit = True

    def start(self, event):
        if self.youtubeURL.GetValue() == '':
            box = wx.MessageDialog(None, '未填入视频链接！', '警告', wx.OK | wx.ICON_EXCLAMATION)
            box.ShowModal()
        else:
            URL = self.youtubeURL.GetValue()
            if not config['videopro']:
                self.updatemesage()
                self.Update()
            # self.req_api(URL)
            # self.dl(URL)
            print("Download Process Start")
            # p1 = Process(target=dl)
            t1 = threading.Thread(target=dl)
            # p2 = Process(target=req_api)
            t2 = threading.Thread(target=req_api)
            t1.start()
            t2.start()
            # p1.start()
            # p2.start()
        self.hasEdit = True

    def Copy(self, event):
        msg = self.youtubesubmit.GetValue()

        if not os.path.exists(config2['dlpath']):
            os.mkdir(config2['dlpath'])

        path = config2['dlpath'] + '/submit.txt'
        f = open(path, mode='w', encoding='utf8')
        f.write(msg)
        f.close()

        pyperclip.copy(msg)

    def setGUI(self, title, link, sub):
        self.youtubeTitle.SetValue(title)
        self.youtubeLink.SetValue(link)
        self.youtubesubmit.SetValue(sub)

    def about(self, event):
        frame2 = aboutwin(parent=frame, id=-1, titletext='about', text1='关于')
        frame2.Show(True)

    def help(self, event):
        frame1 = helpwin(parent=frame, id=-1, titletext='help', text1='软件帮助')
        frame1.Show(True)

    def updateevt(self, event):
        frame4 = updatewin(parent=frame, id=-1, titletext='update', text1='检查更新')
        frame4.Show(True)

    def closewindow(self, event):
        self.savefile()
        self.Destroy()

    # --------------------------------- 加载视频信息 ---------------------------------

    def loadmsg(self, self2):
        # 调用全局的变量menuBar
        name = menuBar.FindItemById(self2.Id).Name
        print(name)
        msgpath = 'Download_Video/' + name + '/msg.json'
        with open(msgpath, 'r') as msgjson:
            msg = json.load(msgjson)

        title = msg['title']
        link = msg['link']
        submit = msg['submit']
        self.youtubeTitle.SetValue(title)
        self.youtubeLink.SetValue(link)
        self.youtubesubmit.SetValue(submit)

    # --------------------------------- 更新信息 ---------------------------------
    def updatemesage(self):

        ydl_opts = {}

        if config['useProxy']:
            ydl_opts = {
                'proxy': config['ipaddress']
            }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.youtubeURL.GetValue(), download=False)

            self.uploader = info_dict.get("uploader", None)
            self.upload_date = info_dict.get("upload_date", None)
            self.title = info_dict.get('title', None)
            self.thumbnail = info_dict.get('thumbnail', None)
            self.description = info_dict.get('description', None)

            if self.upload_date[4] == '0':
                date = self.upload_date[0:4] + '年' + self.upload_date[5] + '月' + self.upload_date[6:8] + '日'
            else:
                date = self.upload_date[0:4] + '年' + self.upload_date[4:6] + '月' + self.upload_date[6:8] + '日'

            formats = info_dict.get('formats')
            file_count = len(formats)

            with open(TEMP_PATH, 'w') as c:
                config2['count'] = file_count
                json.dump(config2, c, indent=4)

            for f in formats:
                format_code.append(f.get('format_id'))
                extension.append(f.get('ext'))
                resolution.append(ydl.format_resolution(f))
                format_note.append(f.get('format_note'))
                file_size.append(f.get('filesize'))

            self.youtubeTitle.SetValue('【MC】' + self.title + '【' + self.uploader + '】')
            self.youtubeLink.SetValue('转自' + config2['url'] + ' 有能力请支持原作者')
            submit = '作者：' + self.uploader + '\r\n发布时间：' + date + '\r\n搬运：' + config[
                'name'] + '\r\n视频摘要：\r\n原简介翻译：' + self.description + '\r\n存档：\r\n其他外链：'
            self.youtubesubmit.SetValue(submit)

        downloadpath = 'Download_video/' + self.title.replace(':', '').replace('.', '').replace('|', '').replace(
            '\\', '').replace('/', '').replace('?', '') + '/%(title)s.%(ext)s'
        dlpath = 'Download_video/' + self.title.replace(':', '').replace('.', '').replace('|', '').replace('\\',
                                                                                                           '').replace(
            '/', '').replace('?', '')
        with open(TEMP_PATH, 'w') as c:
            config2['url'] = self.youtubeURL.GetValue()
            config2['downloadpath'] = downloadpath
            config2['dlpath'] = dlpath
            json.dump(config2, c, indent=4)

    # --------------------------------- 菜单栏部分 ---------------------------------
    def updateMenuBar(self):
        _menubar = wx.MenuBar()
        file = wx.Menu()
        load = wx.Menu()
        for i in filelist:
            but_1 = load.Append(-1, i)
            self.Bind(wx.EVT_MENU, self.loadmsg, but_1)
        file.Append(-1, '加载', load)
        savefilebtn = file.Append(-1, '保存')
        _menubar.Append(file, '文件')
        # 其他部分
        first = wx.Menu()
        help = first.Append(wx.NewId(), '帮助', '软件使用帮助')
        about = first.Append(wx.NewId(), '关于', '软件信息')
        update = first.Append(wx.NewId(), '检查更新', '检查软件更新')
        _menubar.Append(first, '其他')
        self.Bind(wx.EVT_MENU, self.help, help)
        self.Bind(wx.EVT_MENU, self.about, about)
        self.Bind(wx.EVT_MENU, self.savefileevt, savefilebtn)
        self.Bind(wx.EVT_MENU, self.updateevt, update)
        self.SetMenuBar(_menubar)


def updateFilelist():
    filelistlist = []
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        if not os.path.isfile(path):
            temp = os.listdir(path)
            if 'msg.json' in temp:
                filelist.append(list[i])


# --------------------------------- 下载视频&封面 ---------------------------------
def dl():
    path = config2['downloadpath']
    msg = str(config2['vidoecode']) + '+' + str(config2['audiocode'])
    ydl_opts = {
        "writethumbnail": True,
        "external_downloader_args": ['--max-connection-per-server', config['xiancheng'], '--min-split-size', '1M'],
        "external_downloader": ARIA2C,
        'outtmpl': path
    }
    if config['useProxy']:
        ydl_opts['proxy'] = config['ipaddress']

    if config['videopro']:
        ydl_opts['format'] = msg

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([config2['url']])


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


# --------------------------------- 视频质量界面 ---------------------------------

class QualityFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "视频格式", size=(505, 400), style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX)
        icon = wx.Icon(LOGO_PATH, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.Center()
        self.grid = SimpleGrid(self)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def OnExit(self, event):
        self.GetParent().load(event)
        self.Destroy()


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

        with open(TEMP_PATH, 'w') as c:
            if resolution[i] == 'audio only':
                config2['audiocode'] = format_code[i]
            else:
                config2['vidoecode'] = format_code[i]
            json.dump(config2, c, indent=4)

        evt.Skip()


# --------------------------------- 帮助界面 ---------------------------------
class helpwin(wx.Frame):
    def __init__(self, parent, id, titletext, text1):
        wx.Frame.__init__(self, parent, id, titletext, size=(500, 370))
        panel = wx.Panel(self)
        self.Center()
        icon = wx.Icon(LOGO_PATH, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        font1 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '微软雅黑')  # 标题字体

        title = wx.StaticText(panel, -1, text1, (0, 15), (500, -1), wx.ALIGN_CENTER)
        title.SetFont(font1)

        f = open(HELP_PATH, mode='r', encoding='utf8')
        text = f.read()

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
        self.Center()
        icon = wx.Icon(LOGO_PATH, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        font1 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '微软雅黑')  # 标题字体

        title = wx.StaticText(panel, -1, text1, (0, 15), (500, -1), wx.ALIGN_CENTER)
        title.SetFont(font1)

        f = open(LICENCE_PATH, mode='r', encoding='utf8')
        text = f.read()

        msg = wx.TextCtrl(panel, -1, text, (10, 40), (465, 250), style=wx.TE_MULTILINE)
        msg.SetEditable(False)

        button = wx.Button(panel, label='OK', pos=(220, 300), size=(60, 20))
        self.Bind(wx.EVT_BUTTON, self.closewindow, button)

    def closewindow(self, event):
        self.Destroy()


# --------------------------------- 更新界面 ---------------------------------
class updatewin(wx.Frame):
    url = 'https://api.github.com/repos/Aye10032/YouTubeDownLoad/releases/latest'

    r = requests.get(url)
    rjs = r.json()
    downloadLink = rjs['assets'][0]['browser_download_url']
    appname = rjs['assets'][0]['name']
    version = rjs['tag_name']
    link = rjs['html_url']

    def __init__(self, parent, id, titletext, text1):
        wx.Frame.__init__(self, parent, id, titletext, size=(400, 250))
        panel = wx.Panel(self)
        self.Center()
        icon = wx.Icon(LOGO_PATH, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        font1 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '微软雅黑')  # 标题字体

        if self.version == VERSION:
            inf = wx.StaticText(panel, -1, '当前版本已经是最新', (0, 40), (400, -1), wx.ALIGN_CENTER)
            inf.SetFont(font1)
            wx.StaticText(panel, -1, '当前版本  ' + VERSION, (0, 80), (400, -1), wx.ALIGN_CENTER)
            wx.StaticText(panel, -1, '最新版本  ' + self.version, (0, 100), (400, -1), wx.ALIGN_CENTER)
            buttonopen = wx.Button(panel, label='确定', pos=(170, 150), size=(60, 25))
            self.Bind(wx.EVT_BUTTON, self.closewindow, buttonopen)
        else:
            inf = wx.StaticText(panel, -1, '有新的可使用版本!', (0, 35), (400, -1), wx.ALIGN_CENTER)
            inf.SetFont(font1)
            wx.StaticText(panel, -1, '点击 确定 按钮前往下载', (0, 60), (400, -1), wx.ALIGN_CENTER)
            wx.StaticText(panel, -1, '当前版本  ' + VERSION, (0, 80), (400, -1), wx.ALIGN_CENTER)
            wx.StaticText(panel, -1, '最新版本  ' + self.version, (0, 100), (400, -1), wx.ALIGN_CENTER)
            buttonopen = wx.Button(panel, label='确定', pos=(100, 150), size=(60, 25))
            buttoncancel = wx.Button(panel, label='取消', pos=(240, 150), size=(60, 25))
            self.Bind(wx.EVT_BUTTON, self.openevt, buttonopen)
            self.Bind(wx.EVT_BUTTON, self.closewindow, buttoncancel)

    def openevt(self, event):
        webbrowser.open(self.link)

    def closewindow(self, event):
        self.Destroy()


if __name__ == '__main__':
    updateFilelist()
    app = wx.App()
    frame = window(parent=None, id=-1)
    # frame1 = helpwin(parent=frame, id=-1, titletext='help', text1='软件帮助')
    # frame2 = aboutwin(parent=frame, id=-1, titletext='about', text1='关于')
    #
    frame.Show()
    # frame1.Show(False)
    # frame2.Show(False)

    # frame3 = outPutwin(parent=frame, id=-1, titletext='output', text1='输出')
    # frame3.Show(True)
    # frame3.Center()

    # frame1.Center()
    # frame2.Center()
    menuBar = frame.MenuBar
    app.MainLoop()
