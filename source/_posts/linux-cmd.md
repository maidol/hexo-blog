---
title: linux-cmd
date: 2016-7-11 22:37:00
tags: 
  - linux 
  - cmd
---
- linux cmd 常用命令
>- 释放内存 `sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"` 
>- 查询当前文件夹空间大小 `du -hsx * | sort -rh | head -10` 
>- 内存/磁盘空间不足会导致bash tab无法补全 / pm2无法启动 / docker pull / docker start 无法成功执行 / 程序崩溃退出 等问题 
>- 查看cpu占用 `top` 
>- 查看内存占用 `free -m` 
>- 源码安装的一些注意
>>- ./configure --prefix=/opt/apache是什么意思
>>>- 这是按照路径的设置，./configure 会生成 makefile
>>>- 等 make 编译源代码生成相应的动态库或者可执行文件
>>>- 执行 make install 后，生成的动态库或者可执行文件就会拷贝到/opt/apache里面
- `chmod -R 754 ./` 4-read 2-write 1-ex
- `ps -ef | grep docker` 查看进程
- 修改用户密码 `passwd username` 
- scp复制文件 `scp /home/daisy/full.tar.gz k@172.19.2.75:/home/k` 需要ssh服务 
- ubuntu 安装ssh服务 
>- `sudo apt-get install openssh-server` `sudo service ssh start` 
- 退出telnet
>>- `ctrl + c` or `ctrl + ]` 然后 `quit` 
- 查看端口 tcp
>- netstat -anp | grep 5672
- 测试端口连通性(ubuntu)
>- tcp `telnet $IP $port` 
>- udp `nc -vzu $IP $port` -u代表udp协议 ，-v代表详细模式，-z代表只监测端口不发送数据; Connection to $IP $port port [udp/ntp] succeeded! ; 没有回显代表不连通 