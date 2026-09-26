---
title: Ubuntu 14.04 / Debian 7.8 禁用 IPv6 的设置方法
date: 2016-07-07 22:37:00
categories: Linux
tags:
  - ubuntu
  - deploy
  - ipv6
---

通过 `sysctl` 内核参数在 Ubuntu 14.04 / Debian 7.8 上永久禁用 IPv6。

<!-- more -->

## 1. 修改内核参数

编辑 `/etc/sysctl.conf`：

```bash
sudo vim /etc/sysctl.conf
```

在文件末尾添加：

```ini
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
net.ipv6.conf.eth0.disable_ipv6 = 1
```

> **注意**：最后一行中的 `eth0` 是网卡名称，需要按实际情况修改。OpenVZ 环境改成 `venet0`；如果网卡叫 `eth1` 或其他名字，也要相应修改。可以用 `ip link` 查看网卡名称。

## 2. 使配置生效

```bash
sudo sysctl -p
```

## 3. 验证

```bash
# 输出 1 表示 IPv6 已禁用
cat /proc/sys/net/ipv6/conf/all/disable_ipv6

# 网卡信息中不再出现 inet6 地址
ifconfig
# 或
ip addr
```
