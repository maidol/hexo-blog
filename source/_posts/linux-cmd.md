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