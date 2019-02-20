import os
import sys

path = os.path.dirname(sys.executable) +'\\Lib\\site-packages'
print(path)

cmd1 = 'xcopy /s /e /i /y D:\Test\MyDoc E:\Test\MyDoc &&rd /s /q D:\Test\MyDoc'
os.system(cmd1)
