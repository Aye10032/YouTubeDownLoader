# Video Download & Manage

[![](https://img.shields.io/badge/blog-@Aye10032-red.svg?style=flat-square)](https://www.aye10032.com) ![GitHub](https://img.shields.io/github/license/Aye10032/YouTubeDownLoader) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/Aye10032/YouTubeDownLoader) ![GitHub All Releases](https://img.shields.io/github/downloads/Aye10032/YouTubeDownLoader/total)

红石科技搬运组工具软件，用于自动下载视频，视频封面，字幕，同时规范简介格式。      
搬运组空间：[https://space.bilibili.com/1311124](https://space.bilibili.com/1311124)      
作者：Aye10032 [https://space.bilibili.com/40077740](https://space.bilibili.com/40077740)     

## 依赖环境

Windows系统（已测试）；Linux系统（未测试）、macos（未测试）        
代理软件;        


## 使用方法

将下载下来的exe文件放入一个新建文件夹中运行即可，第一次运行会在根目录下生成一些系统配置文件，之后正常运行即可。       
使用介绍视频：     
[![screenshot](screenshot.png)](https://www.bilibili.com/video/BV1S541157ej/)

## 设置

在设置界面，有以下设置选项：

### 普通设置

- **搬运者ID**
- **是否使用代理以及代理地址**：理论上支持socks以及http代理，但是socks可能存在某些问题，这里建议使用http代理
- **下载线程**：过大的线程可能会导致谷歌拒绝访问，请酌情设置
- **下载文件夹**：下载后的视频存放位置



### 高级设置

这里的设置关系到订阅信息和待搬运列表两个选项卡的启用，若没有设置，则选项卡不会启用

- **Google开发者密钥**：前往[谷歌API控制台](https://console.cloud.google.com/)获取你的token
- **订阅频道列表**：只有在添加了token之后此设置才生效
- **API服务器**：搬运组待搬运视频列表，如果你不使用此功能则不用填写



## 上传功能

要使用上传功能，需要先使用此项目获取你的cookies.json：[https://github.com/biliup/biliup-rs](https://github.com/biliup/biliup-rs)

之后，将生成的cookies.json文件放入config文件夹下即可



## 下载

GitHub:[下载地址](https://github.com/Aye10032/YouTubeDownLoader/releases/latest)        
Gitee(国内镜像):[下载地址](https://gitee.com/aye10032/YouTubeDownLoader/releases/v6.0.0)



## 项目依赖

- [yt_dlp](https://github.com/yt-dlp/yt-dlp)
- [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
- [biliup](https://github.com/biliup/biliup)



## 建议安装的第三方工具

- [ffmpeg](https://ffmpeg.org/)：用于合成下载后的视频和音频
- [PhantomJS](https://phantomjs.org/download.html)：有助于更好的解析视频资源
