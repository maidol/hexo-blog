---
title: linux-cmd
date: 2016-7-11 22:37:00
tags: linux cmd
---
- linux cmd 常用命令
>- 释放内存 `sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"` 
>- 查询当前文件夹空间大小 `du -hsx * | sort -rh | head -10` 
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
- scp复制文件 `scp /home/daisy/full.tar.gz k@172.19.2.75:/home/k` 
- ubuntu 安装ssh服务 
>- `sudo apt-get install openssh-server` `sudo service ssh start` 