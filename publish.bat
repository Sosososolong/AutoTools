:: 不显示下面的命令
@echo off
:: 不显示下面命令的输出
python ./publish.py %1 >> log.txt
ping 127.0.0.1 -n 2 >> log.txt
exit
