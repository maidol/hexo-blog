---
title: Linux 常用命令
date: 2016-07-11 22:37:00
categories: Linux
tags:
  - linux
  - cmd
---

日常运维中常用的 Linux 命令速查，涵盖系统资源、文件权限、进程、网络和源码安装等。

<!-- more -->

## 系统资源

| 用途 | 命令 |
| --- | --- |
| 查看 CPU 占用 | `top`（或更直观的 `htop`） |
| 查看内存占用 | `free -m` |
| 查看磁盘分区使用情况 | `df -h` |

```bash
# 当前目录下占用空间最大的 10 项
du -hsx * | sort -rh | head -10

# 释放页缓存
sync && sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
```

> **注意**：内存或磁盘空间不足时，会出现 bash Tab 无法补全、pm2 无法启动、`docker pull` / `docker start` 执行失败、程序崩溃退出等各种问题。排查问题时先看一眼 `free -m` 和 `df -h`。

`drop_caches` 只会释放干净的缓存，执行前先 `sync` 把脏页写回磁盘。它通常只用于测试，生产环境一般不需要手动执行。

## 文件权限

```bash
chmod -R 754 ./
```

权限由三位八进制数组成，依次对应 **所有者 / 所属组 / 其他人**，每一位是以下数值之和：

| 数值 | 权限 |
| --- | --- |
| 4 | 读（r） |
| 2 | 写（w） |
| 1 | 执行（x） |

所以 `754` 表示：所有者 `rwx`，所属组 `r-x`，其他人 `r--`。

## 用户与进程

```bash
# 修改用户密码
passwd username

# 查看进程
ps -ef | grep docker
```

## 远程与文件传输

```bash
# scp 复制文件到远程主机（远程主机需要运行 ssh 服务）
scp /home/daisy/full.tar.gz k@172.19.2.75:/home/k

# Ubuntu 安装并启动 ssh 服务
sudo apt-get install openssh-server
sudo service ssh start
```

## 网络与端口

```bash
# 查看 TCP 端口占用（-p 显示进程信息需要 root 权限）
sudo netstat -anp | grep 5672
# 较新的系统推荐使用 ss
sudo ss -tlnp | grep 5672
```

测试端口连通性（Ubuntu）：

```bash
# TCP
telnet $IP $PORT
# 或
nc -vz $IP $PORT

# UDP
nc -vzu $IP $PORT
```

`nc` 参数说明：`-u` 使用 UDP 协议，`-v` 详细输出，`-z` 只检测端口、不发送数据。连通时会输出类似 `Connection to $IP $PORT port [udp/ntp] succeeded!` 的信息。

> **注意**：UDP 是无连接协议，`nc -vzu` 的结果只能作为参考。防火墙静默丢包时同样可能显示成功，最可靠的办法是让服务端实际回包来验证。

退出 telnet：先按 `Ctrl + ]` 进入 telnet 命令模式，再输入 `quit` 回车。

## 源码安装

以 `./configure --prefix=/opt/apache` 为例，源码安装一般分三步：

1. `./configure --prefix=/opt/apache`：检查编译环境、设置**安装路径**，并生成 `Makefile`。
2. `make`：编译源代码，生成相应的动态库或可执行文件。
3. `make install`：把生成的动态库和可执行文件复制到 `--prefix` 指定的目录（这里是 `/opt/apache`）。
