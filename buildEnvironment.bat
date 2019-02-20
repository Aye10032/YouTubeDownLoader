@echo off
echo %~dp0res
setx /m path "%res%;%~dp0res"
pause