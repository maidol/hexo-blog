---
title: Ubuntu 14.04 / Debian 7.8 禁止 IPv6 的设置方法
date: 2016-7-07 22:37:00
tags: ubuntu deploy ipv6
---
- `vim /etc/sysctl.conf`
>-  添加内容, 如果是 OpenVZ 环境，请把最后一条的 eth0 改成 venet0 ，同理如果网卡是 eth1 或者其他的名字，也要相应修改。
    net.ipv6.conf.all.disable_ipv6 = 1
    net.ipv6.conf.default.disable_ipv6 = 1
    net.ipv6.conf.lo.disable_ipv6 = 1
    net.ipv6.conf.eth0.disable_ipv6 = 1
>- 执行 `sudo sysctl -p`
>- `ifconfig` 查看