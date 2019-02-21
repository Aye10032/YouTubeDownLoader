# Youtube Download

红石科技搬运组工具软件，用于自动下载视频，视频封面，字幕，同时规范简介格式。      
字幕组空间：[https://space.bilibili.com/1311124](https://space.bilibili.com/1311124)      
作者：Aye10032     

## 依赖环境

Windows系统；      
python3     
代理软件        

## 使用方法

首次运行先运行buildEnvironment.bat，自动配置环境，或者你也可以选择自行配置环境：
```batch
pip install pyperclip requests youtube_dl
pip install -U wxPython

# 之后再将本文件夹中的res文件夹加入系统环境变量的path变量中即可
```

正常运行直接双击运行run.bat即可

## 界面设置

设置搬运者ID，是否适用代理（如果代理是部署在路由器上选择不使用即可），以及代理IP，**代理必须是以http：//开头**，之后跟上IP及端口号即可。
这里编辑完毕后点击保存下次运行软件时会自动载入配置。

输入视频链接，点击下载按钮即可开始。运行结束后可以点击按钮复制简介部分的文字。