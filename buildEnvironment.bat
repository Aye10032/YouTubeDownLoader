@echo off
echo %path%|findstr /i "%~dp0res"&&(goto run)

wmic ENVIRONMENT where "name='path' and username='<system>'" set VariableValue="%path%;%~dp0res"

:run

echo Done

pause