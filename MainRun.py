# -*- coding:utf-8 -*-
import json
import os
import sys
import threading
import time
import webbrowser

from shutil import copy2

from requests import request, exceptions
import pyperclip
import wx
import wx.grid as gridlib
import youtube_dl
from googleapiclient.discovery import build
from httplib2 import socks, ProxyInfo, Http

# --------------------------------- 资源文件位置设置 ---------------------------------
basedir = ""
if getattr(sys, 'frozen', False):
    # we are running in a |PyInstaller| bundle
    basedir = sys._MEIPASS
else:
    # we are running in a normal Python environment
    basedir = os.path.dirname(__file__)

VERSION = 'V4.6.1'
RES_PATH = 'res'
LOG_PATH = 'log'
CONFIG_PATH = 'res/config.json'
TEMP_PATH = 'res/temp.json'
ARIA2C = 'aria2c.exe'
ARIA2C_PATH = basedir + '/res/aria2c.exe'
LOGO_PATH = basedir + '/res/logo.ico'
LICENCE_PATH = basedir + '/res/LICENCE'
HELP_PATH = basedir + "/res/HELP"
SEARCH_PATH = basedir + "/res/search.png"
COPY_PATH = basedir + "/res/copy.png"
TRANSLATE_PATH = basedir + "/res/translate.png"
PLAY_PATH = basedir + "/res/play.png"
LOG_NAME = time.strftime("%Y-%m-%d", time.localtime())
YOUTUBE_DEVELOPER_KEY = 'AIzaSyBLn6N3SVih9p3fdD97QcBn-weFM5j2WVI'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# --------------------------------- 前置检查部分开始 ---------------------------------
if not os.path.exists(ARIA2C):
    copy2(ARIA2C_PATH, os.getcwd())

if not os.path.exists(RES_PATH):
    os.makedirs('res')
if not os.path.exists(LOG_PATH):
    os.makedirs('log')
if not os.path.exists(CONFIG_PATH):
    default_config = {
        "name": "",
        "ipaddress": "http://127.0.0.1:1080",
        "useProxy": True,
        "xiancheng": "4",
        "multilanguage": True,
        "notimeline": False,
        "videopro": True,
        "channellist": [
            {
                "name": "ilmango",
                "url": "UCHSI8erNrN6hs3sUK6oONLA"
            }
        ]
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

with open(TEMP_PATH, 'r') as conf_temp:
    config_temp = json.load(conf_temp)

if not os.path.exists('Download_Video'):
    os.mkdir('Download_Video')

if not os.path.exists('res'):
    os.mkdir('res')

format_code, extension, resolution, format_note, file_size = [], [], [], [], []

rootdir = 'Download_Video'
root_list = os.listdir(rootdir)
filelist = []
channel_result = {}

channel_list = []
for u in config['channellist']:
    channel_list.append(u['name'])

url = "http://api.aye10032.com:4991/getTODOVideo"

done_response = request("GET", url)

done_list = []

for id, element in enumerate(done_response.json()['data']):
    done_list.append('NO.' + str(element['id']) + ' ' + element['description'] + '|' + str(id))


class window(wx.Frame):
    current_path = os.path.abspath(__file__)
    father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")

    uploader = ''
    upload_date = ''
    title = ''
    description = ''
    URL = ''
    thumbnail = ''
    basepath = ''
    hasEdit = False
    menuBar = None

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, '半自动搬运工具@Aye10032 ' + VERSION, size=(600, 745),
                          style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.SYSTEM_MENU)

        self.Center()
        icon = wx.Icon(LOGO_PATH, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        with open(TEMP_PATH, 'w') as c:
            config_temp['audiocode'] = 0
            config_temp['vidoecode'] = 0
            json.dump(config_temp, c, indent=4)

        panel = wx.Panel(self)

        font1 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '微软雅黑')  # 标题字体

        t1 = wx.StaticText(panel, -1, '个人设置', (0, 5), (600, -1), wx.ALIGN_CENTER)
        t1.SetFont(font1)

        self.Bind(wx.EVT_CLOSE, self.closewindow)

        # --------------------------------- 搬运者ID及线程设置部分 ---------------------------------

        wx.StaticText(panel, -1, '搬运者ID：', (22, 35))
        self.yourname = wx.TextCtrl(panel, -1, config['name'], (90, 30), (130, 23))

        wx.StaticText(panel, -1, '下载线程：', (327, 35))
        listc = ['1', '2', '4', '6', '8', '16']
        self.xiancheng = wx.ComboBox(panel, -1, value=config['xiancheng'], pos=(400, 30), size=(80, 23),
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
        self.youtubeURL = wx.TextCtrl(panel, -1, '', pos=(90, 105), size=(340, 23))

        self.channel_list_btn = wx.ComboBox(panel, -1, '', pos=(435, 104), size=(105, 25), choices=channel_list,
                                            style=wx.CB_READONLY)

        self.Bind(wx.EVT_COMBOBOX, self.list_channel, self.channel_list_btn)

        self.startbtn = wx.Button(panel, -1, '下载视频', pos=(470, 136), size=(70, 25))
        self.Bind(wx.EVT_BUTTON, self.start, self.startbtn)

        self.getbtn = wx.Button(panel, -1, '获取简介', pos=(390, 136), size=(70, 25))
        self.Bind(wx.EVT_BUTTON, self.get, self.getbtn)

        # --------------------------------- 质量代码部分 ---------------------------------
        self.highbtn = wx.CheckBox(panel, -1, '自定义视频质量   ', (13, 138), style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.provideo, self.highbtn)

        wx.StaticText(panel, -1, '格式代码：', (160, 138))
        self.qualitytext = wx.TextCtrl(panel, -1, '', (225, 135), (110, 23))

        if config['videopro']:
            self.highbtn.SetValue(True)
            self.qualitytext.SetEditable(True)
        else:
            self.highbtn.SetValue(False)
            self.qualitytext.SetEditable(False)

        pic1 = wx.Image(SEARCH_PATH, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.viewbtn = wx.BitmapButton(panel, -1, pic1, (340, 135), (23, 23))
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
        self.Bind(wx.EVT_ENTER_WINDOW, self.CopyMSG, self.CopyLink)
        self.Bind(wx.EVT_BUTTON, self.Copy, self.CopyLink)

        pic3 = wx.Image(TRANSLATE_PATH, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.Translate = wx.BitmapButton(panel, -1, pic3, pos=(535, 480), size=(35, 35))
        self.Bind(wx.EVT_BUTTON, self.translate, self.Translate)

        self.OpenLink = wx.Button(panel, -1, '🔗', pos=(535, 600), size=(35, 35))
        self.Bind(wx.EVT_BUTTON, self.openlink, self.OpenLink)

        self.statusbar = self.CreateStatusBar()

        pic4 = wx.Image(PLAY_PATH, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.OpenVideo = wx.BitmapButton(panel, -1, pic4, pos=(535, 550), size=(35, 35))
        self.OpenVideo.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.openvideo, self.OpenVideo)

        self.updateMenuBar()

    def usePor(self, event):
        if self.usebtn.GetValue():
            self.ipaddress.SetEditable(True)
        else:
            self.ipaddress.SetEditable(False)

    def list_channel(self, event):
        choice_channel = self.channel_list_btn.GetValue()
        choice_url = ''
        for u in config['channellist']:
            if u['name'] == self.channel_list_btn.GetValue():
                choice_url = u['url']
                break
        print('已选择' + choice_channel + '的频道(' + choice_url + ')')
        frame5 = ChannelFrame(parent=frame, url=choice_url)
        frame5.Show(True)

    def set_channel_url(self, event):
        self.youtubeURL.SetValue(config_temp['url'])

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
            if not os.path.exists(config_temp['dlpath']):
                os.mkdir(config_temp['dlpath'])

            msgpath = config_temp['dlpath'] + '/msg.json'

            origin = self.youtubeURL.GetValue()
            title = self.youtubeTitle.GetValue()
            link = self.youtubeLink.GetValue()
            submit = self.youtubesubmit.GetValue()

            msg = {
                "origin": origin,
                "title": title,
                "link": link,
                "submit": submit
            }
            with open(msgpath, 'w') as msgwrite:
                json.dump(msg, msgwrite, indent=4)

        updateFilelist()

    def view(self, event):
        with open(TEMP_PATH, 'w') as c:
            config_temp['url'] = self.youtubeURL.GetValue()
            json.dump(config_temp, c, indent=4)
        self.updatemesage()
        self.hasEdit = True
        frame3 = QualityFrame(parent=frame)
        frame3.Show(True)

    def load(self, event):
        msg = str(config_temp['vidoecode']) + '+' + str(config_temp['audiocode'])
        self.qualitytext.SetValue(msg)

    def get(self, event):
        if self.youtubeURL.GetValue() == '':
            box = wx.MessageDialog(None, '未填入视频链接！', '警告', wx.OK | wx.ICON_EXCLAMATION)
            box.ShowModal()
        else:
            self.updatemesage()
            self.Update()
        self.hasEdit = True

    def start(self, event):
        if self.youtubeURL.GetValue() == '':
            box = wx.MessageDialog(None, '未填入视频链接！', '警告', wx.OK | wx.ICON_EXCLAMATION)
            box.ShowModal()
        else:
            if not config['videopro']:
                self.updatemesage()
                self.Update()

            print("Download Process Start")

            t1 = threading.Thread(target=dl)
            t1.start()

        self.hasEdit = True

    def Copy(self, event):
        msg = self.youtubesubmit.GetValue()

        if not os.path.exists(config_temp['dlpath']):
            os.mkdir(config_temp['dlpath'])

        path = config_temp['dlpath'] + '/submit.txt'
        f = open(path, mode='w', encoding='utf8')
        f.write(msg)
        f.close()

        pyperclip.copy(msg)

    def CopyMSG(self, event):
        self.statusbar.SetStatusText('复制简介信息')

    def translate(self, event):
        frame3 = translatewin(parent=frame, id=-1, titletext='翻译', text1='原文')
        frame3.Show(True)

    def openlink(self, event):
        webbrowser.open(self.youtubeURL.GetValue())

    def openvideo(self, event):
        print('尝试打开 ' + self.basepath)
        os.startfile(self.basepath)

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

    # ---------------------------------- 更新信息框 ----------------------------------
    def updatemesage(self):
        self.uploader, self.title, self.thumbnail, self.description, self.upload_date \
            = returnmesage(self.youtubeURL.GetValue())

        if self.upload_date[4] == '0' and self.upload_date[6] == '0':
            date = self.upload_date[0:4] + '年' + self.upload_date[5] + '月' + self.upload_date[7:8] + '日'
        elif self.upload_date[4] == '0' and not self.upload_date[6] == 0:
            date = self.upload_date[0:4] + '年' + self.upload_date[5] + '月' + self.upload_date[6:8] + '日'
        elif not self.upload_date[4] == '0' and self.upload_date[6] == '0':
            date = self.upload_date[0:4] + '年' + self.upload_date[4:6] + '月' + self.upload_date[7:8] + '日'
        else:
            date = self.upload_date[0:4] + '年' + self.upload_date[4:6] + '月' + self.upload_date[6:8] + '日'

        self.youtubeTitle.SetValue('【MC】' + self.title + '【' + self.uploader + '】')
        self.youtubeLink.SetValue('转自' + config_temp['url'] + ' 有能力请支持原作者')
        submit = '作者：' + self.uploader + '\r\n发布时间：' + date + '\r\n搬运：' + config[
            'name'] + '\r\n视频摘要：\r\n原简介翻译：' + self.description + '\r\n存档：\r\n其他外链：'
        self.youtubesubmit.SetValue(submit)

        downloadpath = 'Download_video/' + self.title.replace(':', '').replace('.', '').replace('|', '').replace(
            '\\', '').replace('/', '').replace('?', '').replace('\"', '') + '/%(title)s.%(ext)s'
        dlpath = 'Download_video/' + self.title.replace(':', '').replace('.', '').replace('|', '').replace('\\',
                                                                                                           '').replace(
            '/', '').replace('?', '').replace('\"', '')
        with open(TEMP_PATH, 'w') as c:
            config_temp['url'] = self.youtubeURL.GetValue()
            config_temp['downloadpath'] = downloadpath
            config_temp['dlpath'] = dlpath
            json.dump(config_temp, c, indent=4)

    # --------------------------------- 加载视频信息 ---------------------------------

    def loadmsg(self, self2):
        # 调用全局的变量menuBar
        name = str(menuBar.FindItemById(self2.Id).GetItemLabel())
        msgpath = 'Download_Video/' + name + '/msg.json'
        # print(msgpath)
        with open(msgpath, 'r') as msgjson:
            msg = json.load(msgjson)

        url = msg['origin']
        title = msg['title']
        link = msg['link']
        submit = msg['submit']
        self.basepath = 'Download_Video/' + name
        self.youtubeURL.SetValue(url)
        self.youtubeTitle.SetValue(title)
        self.youtubeLink.SetValue(link)
        self.youtubesubmit.SetValue(submit)

        self.hasEdit = True

        templist = os.listdir(self.basepath)
        for i in templist:
            if i.__contains__('.mp4'):
                self.OpenVideo.Enable(True)
                self.basepath = self.father_path + '\\' + self.basepath + '\\' + i
            elif i.__contains__('.webm'):
                self.OpenVideo.Enable(True)
                self.basepath = self.father_path + '\\' + self.basepath + '\\' + i
            elif i.__contains__('.flv'):
                self.OpenVideo.Enable(True)
                self.basepath = self.father_path + '\\' + self.basepath + '\\' + i

    def addvideo(self, btn):
        # print(menuBar.FindItemById(btn.Id).GetItemLabel())
        index = int(str(menuBar.FindItemById(btn.Id).GetItemLabel()).split('|')[-1])
        choice_url = done_response.json()['data'][index]['url']
        # print(choice_url)
        self.youtubeURL.SetValue(choice_url)

    # --------------------------------- 菜单栏部分 ---------------------------------
    def updateMenuBar(self):
        _menubar = wx.MenuBar()
        file = wx.Menu()
        load = wx.Menu()
        for i in filelist:
            but_1 = load.Append(-1, i)
            self.Bind(wx.EVT_MENU, self.loadmsg, but_1)
        file.AppendSubMenu(load, '加载')
        savefilebtn = file.Append(-1, '保存', '保存当前视频信息')
        _menubar.Append(file, '文件')
        # 搬运列表
        group_list = wx.Menu()
        for url in done_list:
            but_a = group_list.Append(-1, url)
            self.Bind(wx.EVT_MENU, self.addvideo, but_a)
        _menubar.Append(group_list, '搬运列表')
        # 其他部分
        first = wx.Menu()
        help = first.Append(wx.ID_NEW, '帮助', '软件使用帮助')
        about = first.Append(wx.ID_NEW, '关于', '软件信息')
        update = first.Append(wx.ID_NEW, '检查更新', '检查软件更新')
        _menubar.Append(first, '其他')
        self.Bind(wx.EVT_MENU, self.help, help)
        self.Bind(wx.EVT_MENU, self.about, about)
        self.Bind(wx.EVT_MENU, self.savefileevt, savefilebtn)
        self.Bind(wx.EVT_MENU, self.updateevt, update)
        self.SetMenuBar(_menubar)


# --------------------------------- 更新信息 ---------------------------------
def returnmesage(url):
    ydl_opts = {}

    if config['useProxy']:
        ydl_opts = {
            'proxy': config['ipaddress']
        }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print(ydl_opts)
        youtubeext = youtube_dl.extractor.YoutubeIE
        ydl.add_info_extractor(youtubeext)

        info_dict = ydl.extract_info(url, download=False, force_generic_extractor=True)

        uploader = info_dict.get("uploader")
        title = info_dict.get('title')
        thumbnail = info_dict.get('thumbnail')
        description = info_dict.get('description')

        if not (info_dict.get("upload_date") is None):
            upload_date = info_dict.get("upload_date", None)
        else:
            upload_date = '00000000'

        formats = info_dict.get('formats')
        file_count = len(formats)

        with open(TEMP_PATH, 'w') as c:
            config_temp['count'] = file_count
            json.dump(config_temp, c, indent=4)

        for f in formats:
            format_code.append(f.get('format_id'))
            extension.append(f.get('ext'))
            resolution.append(ydl.format_resolution(f))
            format_note.append(f.get('format_note'))
            file_size.append(f.get('filesize'))

        return uploader, title, thumbnail, description, upload_date


def updateFilelist():
    filelistlist = []
    for i in range(0, len(root_list)):
        path = os.path.join(rootdir, root_list[i])
        if not os.path.isfile(path):
            temp = os.listdir(path)
            if 'msg.json' in temp:
                filelist.append(root_list[i])


# --------------------------------- 下载视频&封面 ---------------------------------
def dl():
    path = config_temp['downloadpath']
    msg = str(config_temp['vidoecode']) + '+' + str(config_temp['audiocode'])
    ydl_opts = {
        "writethumbnail": True,
        "external_downloader_args": ['--max-connection-per-server', config['xiancheng'], '--min-split-size', '1M'],
        "external_downloader": ARIA2C,
        'outtmpl': path,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitlesformat': 'srt',
        'subtitleslangs': ['zh-Hans', 'en'],
        'logger': Logger(LOG_PATH + '/' + LOG_NAME + '.log')
    }
    if config['useProxy']:
        ydl_opts['proxy'] = config['ipaddress']

    if config['videopro']:
        ydl_opts['format'] = msg

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([config_temp['url']])


# --------------------------------- 翻译界面 ---------------------------------
class translatewin(wx.Frame):
    originText = ''
    resText = ''

    def __init__(self, parent, id, titletext, text1):
        wx.Frame.__init__(self, parent, id, titletext, size=(500, 480))
        panel = wx.Panel(self)
        self.Center()
        icon = wx.Icon(LOGO_PATH, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        font1 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '微软雅黑')  # 标题字体

        title = wx.StaticText(panel, -1, text1, (0, 10), (500, -1), wx.ALIGN_CENTER)
        title.SetFont(font1)

        self.originTeaxArea = wx.TextCtrl(panel, -1, '', (10, 35), (465, 160), style=wx.TE_MULTILINE)

        button = wx.Button(panel, label='翻译', pos=(220, 200), size=(60, 20))
        self.Bind(wx.EVT_BUTTON, self.tran, button)

        self.res = wx.TextCtrl(panel, -1, self.resText, (10, 225), (465, 200), style=wx.TE_MULTILINE)
        self.res.SetEditable(False)

    def tran(self, event):
        url = "http://translate.google.cn/translate_a/single"
        self.originText = self.originTeaxArea.GetValue().replace('\n', '')
        querystring = {"client": "gtx", "dt": "t", "dj": "1", "ie": "UTF-8", "sl": "auto", "tl": "zh_CN",
                       "q": self.originText}

        payload = ""
        headers = {
            'User-Agent': "PostmanRuntime/7.11.0",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Postman-Token': "2fb29936-69ef-405e-be97-02ba2bf646ad,2d2b4882-edd6-4b30-9cb1-0802f7a89458",
            'Host': "translate.google.cn",
            'accept-encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

        response = request("GET", url, data=payload, headers=headers, params=querystring).json()
        for s in response['sentences']:
            self.resText = self.resText + s['trans']

        self.res.SetValue(self.resText)


# --------------------------------- 视频列表界面 ---------------------------------
class ChannelFrame(wx.Frame):
    def __init__(self, parent, url):
        wx.Frame.__init__(self, parent, -1, "近20个视频列表", size=(700, 400),
                          style=wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX)
        icon = wx.Icon(LOGO_PATH, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.Center()
        self.getlist(url)
        self.grid = ChannelGrid(self)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def getlist(self, channel_id):
        # 如下是代理设置
        if config['useProxy']:
            ipaddress = config['ipaddress'].split(':')[1][2:]
            ipport = int(config['ipaddress'].split(':')[2])
            proxy_info = ProxyInfo(socks.PROXY_TYPE_SOCKS5, ipaddress, ipport)
            http = Http(timeout=300, proxy_info=proxy_info)
        else:
            http = Http(timeout=300)

        # 构建youtube对象时增加http参数
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_DEVELOPER_KEY, http=http)

        result = youtube.search().list(
            part='snippet,id',
            channelId=channel_id,
            order='date',
            maxResults=20
        ).execute()

        global channel_result
        channel_result = result

    def OnExit(self, event):
        self.GetParent().set_channel_url(event)
        self.Destroy()


class ChannelGrid(gridlib.Grid):
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent)

        count = 20
        self.CreateGrid(count, 2)
        self.SetRowLabelSize(30)
        self.SetColSize(col=0, width=450)
        self.SetColSize(col=1, width=185)

        self.EnableEditing(False)
        self.DisableColResize(False)
        self.DisableRowResize(False)

        self.SetColLabelValue(0, "标题")
        self.SetColLabelValue(1, "日期")
        self.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        for i in range(count):
            self.SetRowSize(row=i, height=50)

            vtitle = channel_result.get('items')[i].get('snippet').get('title')
            if len(vtitle) > 30:
                vtitle_list = list(vtitle)
                vtitle_list.insert(30, '\n')
                vtitle = ''.join(vtitle_list)

            self.SetCellValue(i, 0, vtitle)
            self.SetCellValue(i, 1, channel_result.get('items')[i].get('snippet').get('publishedAt'))

        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)

    def OnCellLeftClick(self, evt):
        row = "%d" % (evt.GetRow())
        col = "%d" % (evt.GetCol())
        i = int(row)
        flag = int(col)

        url = 'https://youtu.be/' + channel_result.get('items')[i].get('id').get('videoId')

        if flag == 0:
            config_temp['url'] = url
            self.GetParent().OnExit(evt)
        elif flag == 1:
            webbrowser.open(url)

        evt.Skip()


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

        count = config_temp['count']
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
                config_temp['audiocode'] = format_code[i]
            else:
                config_temp['vidoecode'] = format_code[i]
            json.dump(config_temp, c, indent=4)

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
    downloadLink = ""
    appname = ""
    version = ""
    link = ""

    VERSION = VERSION.replace('v', 'V')

    def __init__(self, parent, id, titletext, text1):
        wx.Frame.__init__(self, parent, id, titletext, size=(400, 250))
        panel = wx.Panel(self)
        self.Center()
        icon = wx.Icon(LOGO_PATH, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        font1 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, '微软雅黑')  # 标题字体

        url = 'https://api.github.com/repos/Aye10032/YouTubeDownLoad/releases/latest'

        proxy = {
            'http': config['ipaddress']
        }
        print(proxy)

        try:
            response = request("GET", url)
            self.updaetGithubInf(response)
        except ConnectionResetError:
            response = request("GET", url, proxies=proxy)
            self.updaetGithubInf(response)
        except exceptions.ConnectionError:
            response = request("GET", url, proxies=proxy)
            self.updaetGithubInf(response)

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
        # win32api.ShellExecute(0, 'open', self.link, '', '', 1)
        webbrowser.open(self.link)

    def closewindow(self, event):
        self.Destroy()

    def updaetGithubInf(self, body):
        rjs = body.json()
        self.downloadLink = rjs['assets'][0]['browser_download_url']
        self.appname = rjs['assets'][0]['name']
        self.version = rjs['tag_name']
        self.link = rjs['html_url']

        self.version = self.version.replace('v', 'V')


class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'a')

    def write(self, message):
        self.terminal.write(message)
        self.terminal.flush()
        self.log.write(message)
        self.log.flush()

    def debug(self, message):
        self.terminal.write('[debug]' + message + '\n')
        self.terminal.flush()
        self.log.write('[debug]' + message + '\n')
        self.log.flush()

    def warning(self, message):
        self.terminal.write('[warning]' + message + '\n')
        self.terminal.flush()
        self.log.write('[warning]' + message + '\n')
        self.log.flush()

    def error(self, message):
        self.terminal.write('[error]' + message + '\n')
        self.terminal.flush()
        self.log.write('[error]' + message + '\n')
        self.log.flush()

    def isatty(self):
        pass

    def flush(self):
        pass


if __name__ == '__main__':
    sys.stdout.isatty = lambda: False
    sys.stdout = Logger(LOG_PATH + '/' + LOG_NAME + '.log', sys.stdout)
    sys.stderr = Logger(LOG_PATH + '/' + LOG_NAME + '.log', sys.stderr)
    updateFilelist()
    app = wx.App()
    frame = window(parent=None, id=-1)

    frame.Show()

    menuBar = frame.MenuBar
    app.MainLoop()
