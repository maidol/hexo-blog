---
title: VPS 部署笔记
date: 2016-07-06 22:37:00
categories: Linux
tags:
  - vps
  - linode
  - vpn
  - nginx
---

在一台全新的 Ubuntu VPS 上从零搭建环境的完整记录：用户与安全、时区、Node.js、shadowsocks、MongoDB、Nginx、MySQL、Redis、Hexo、RabbitMQ、SSH 免密登录等。

<!-- more -->

> **说明**：以下操作均在 Ubuntu 下进行，写于 2016 年。文中的软件版本（MySQL 5.7.13、Redis 3.2.1、RabbitMQ 3.6.3 等）都比较旧，实际安装时请替换为当前版本，并以官方文档为准。
>
> 文中的 `your_server_ip`、`yourpassword`、`kmaidol` 等都是占位符，请替换成自己的值。

## 目录

- [1. 创建普通用户并禁止 root 远程登录](#1-创建普通用户并禁止-root-远程登录)
- [2. 设置时区与时间同步](#2-设置时区与时间同步)
- [3. 禁用 IPv6](#3-禁用-IPv6)
- [4. 安装 nvm 与 Node.js](#4-安装-nvm-与-Node-js)
- [5. 安装 Git](#5-安装-Git)
- [6. shadowsocks](#6-shadowsocks)
- [7. MongoDB](#7-MongoDB)
- [8. tmux](#8-tmux)
- [9. Nginx](#9-Nginx)
- [10. MySQL（源码编译安装）](#10-MySQL（源码编译安装）)
- [11. Redis（源码安装）](#11-Redis（源码安装）)
- [12. Hexo](#12-Hexo)
- [13. Cloud9 IDE](#13-Cloud9-IDE)
- [14. RabbitMQ](#14-RabbitMQ)
- [15. SSH 免密码登录](#15-SSH-免密码登录)
- [16. 流量监控](#16-流量监控)

## 1. 创建普通用户并禁止 root 远程登录

之后的所有操作都用新建的普通用户登录完成。

### 1.1 创建用户并授予 sudo 权限

```bash
# 创建用户 kmaidol
adduser kmaidol

# 推荐做法：把用户加入 sudo 组
usermod -aG sudo kmaidol
```

也可以直接编辑 sudoers 文件。**务必使用 `visudo`**，它会在保存前检查语法，避免因为写错把自己锁在外面。不要用 `chmod` 修改 `/etc/sudoers` 的权限后再用 vim 编辑：

```bash
visudo
```

在 `User privilege specification` 部分添加一行：

```text
# User privilege specification
root    ALL=(ALL:ALL) ALL
kmaidol ALL=(ALL:ALL) ALL
```

然后用 `kmaidol` 重新登录，或者执行 `su - kmaidol` 切换用户。

### 1.2 禁止 root 远程登录

服务器开着 root 远程登录很不安全，应该关掉。

> **注意**：必须先确认新用户已经拿到 sudo 权限，**并且能够远程登录**，再执行下面的操作。否则可能再也登录不上服务器。

```bash
sudo vim /etc/ssh/sshd_config
```

把 `PermitRootLogin` 的值改为 `no`：

```text
PermitRootLogin no
```

重启 ssh 服务：

```bash
sudo service ssh restart
```

再用 root 登录，会发现已经登录不上了。

## 2. 设置时区与时间同步

```bash
# 交互式选择时区，按提示操作
tzselect

# 设置本地时间为上海时区
sudo cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 查看当前时间
date
```

更多时区可以在 `/usr/share/zoneinfo/` 目录中选择。在 Ubuntu 16.04 及以上版本，推荐直接用 `sudo timedatectl set-timezone Asia/Shanghai`。

与时间服务器同步：

```bash
sudo apt-get install ntpdate
sudo ntpdate cn.pool.ntp.org
# 把系统时间写入硬件时钟
sudo hwclock --systohc
```

## 3. 禁用 IPv6

参见 [Ubuntu 14.04 / Debian 7.8 禁用 IPv6 的设置方法](/2016/07/07/ubuntu-禁用ipv6/)。

## 4. 安装 nvm 与 Node.js

```bash
sudo apt-get install curl
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.0/install.sh | bash

# 激活 nvm（安装脚本会自动写入 ~/.bashrc，重新登录后也会生效）
. ~/.nvm/nvm.sh

# 安装 Node.js v6，并设为默认版本
nvm install v6
nvm alias default v6
```

常用的全局工具：

```bash
npm install -g nrm    # 管理 npm 下载源：nrm ls / nrm use <registry>
npm install -g bower  # 前端包管理
npm install -g pm2    # Node 进程管理
```

## 5. 安装 Git

```bash
sudo apt-get install git
```

## 6. shadowsocks

### 6.1 源码安装（支持一次性验证 OTA）

```bash
sudo apt-get update
sudo apt-get install -y python python-setuptools
git clone https://github.com/shadowsocks/shadowsocks.git
cd shadowsocks
git checkout master
sudo python setup.py install

# 查看帮助
ssserver -h
```

开启一次性验证（OTA）有两种方式：运行 `ssserver` 时加上 `-a` 参数，或者在配置文件中加上 `"one_time_auth": true`。

配置文件 `ss.json` 示例：

```json
{
  "server": "your_server_ip",
  "port_password": {
    "10080": "yourpassword"
  },
  "timeout": 300,
  "method": "aes-256-cfb",
  "one_time_auth": true
}
```

启动与停止：

```bash
# -d 表示以守护进程方式运行
sudo ssserver --manager-address 127.0.0.1:6001 -c ss.json -d start
sudo ssserver -d stop
```

`sslocal` 是 Linux 下的 shadowsocks 客户端，用法可以通过 `sslocal -h` 查看。

> OTA 和 `aes-256-cfb` 这类流加密方式都已经被 shadowsocks 废弃，新部署建议使用 AEAD 加密方式（如 `chacha20-ietf-poly1305`）。

### 6.2 用 Docker 部署

```bash
docker pull oddrationale/docker-shadowsocks
docker run -d -p 1984:1984 oddrationale/docker-shadowsocks \
  -s 0.0.0.0 -p 1984 -k $SSPASSWORD -m aes-256-cfb
```

该镜像使用 `ENTRYPOINT` 把容器当作可执行程序运行，更多命令行参数见 [shadowsocks 文档](https://github.com/shadowsocks/shadowsocks)。

### 6.3 部署 shadowsocks-manager

```bash
git clone https://github.com/shadowsocks/shadowsocks-manager.git
cd shadowsocks-manager
npm install -g bower
npm install
bower install
mv config.js.sample config.js
node server
```

## 7. MongoDB

### 7.1 安装

```bash
sudo apt-get install mongodb
```

用 apt-get 安装后会自动注册为服务（`/etc/init.d/mongodb`）：

```bash
sudo service mongodb start|stop|restart|status
```

几个程序的区别：`mongod` 是服务端程序（`mongod -h` 查看帮助），`mongodb` 服务脚本封装了 `mongod`，`mongo` 是客户端 shell。

### 7.2 开启远程连接

**第 1 步：添加管理员账号**

```bash
mongo   # 本机登录
```

```js
use admin
db.createUser({ user: 'kmaidol', pwd: 'xxxxxx', roles: ['root'] })
```

> 原文使用的 `db.addUser()` 在 MongoDB 2.6 起已经废弃，3.0 后被移除，请改用 `db.createUser()`。

**第 2 步：修改 `/etc/mongodb.conf`**

```ini
# bind_ip = 127.0.0.1   # 注释掉此行，允许远程连接
auth = true             # 去掉此行前的注释，开启认证
```

**第 3 步：重启 MongoDB**

```bash
sudo service mongodb restart
```

**第 4 步：防火墙开放 27017 端口**

```bash
sudo iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 27017 -j ACCEPT
```

如果需要远程登录指定的数据库，要在对应的数据库里创建用户。例如对数据库 `test`：

```js
use test
db.createUser({ user: 'kmaidol', pwd: 'xxxxxx', roles: ['readWrite'] })
```

之后就可以用这个用户访问 `test` 库了。

## 8. tmux

```bash
sudo apt-get install tmux
tmux new -s <session>   # 新建会话
tmux a -t <session>     # 进入已打开的会话
```

更多用法见 [tmux 使用入门](/2016/07/23/tmux-learn/)。

## 9. Nginx

### 9.1 安装与常用命令

```bash
sudo apt-get install nginx
```

| 用途 | 命令 |
| --- | --- |
| 指定配置文件启动 | `sudo nginx -c /path/to/nginx.conf` |
| 快速停止 / 优雅停止 | `sudo nginx -s stop` / `sudo nginx -s quit` |
| 强制结束进程 | `sudo pkill -9 nginx` |
| 重载配置 | `sudo nginx -s reload` |
| 检查配置文件语法 | `sudo nginx -t` |

### 9.2 配置示例（含 SSL）

```nginx
worker_processes 1;

events {
}

http {
    # 压缩数据流
    gzip              on;
    gzip_min_length   1000;
    gzip_types        text/plain text/css application/x-javascript;

    # 负载均衡的服务器列表
    # 可以用 weight 参数设置权重，权重越高，被分配到的概率越大
    upstream shadowsocksManager {
        server localhost:6003;
    }

    # test
    server {
        listen       80;
        server_name  v1.maidol.pw;

        location / {
            proxy_pass http://www.google.com;
        }
    }

    # maidol.pw
    server {
        listen       80;
        listen       443 ssl;   # 只在 443 端口启用 SSL
        server_name  maidol.pw;

        # 证书文件路径
        ssl_certificate     /home/kmaidol/cert/1_maidol.pw_bundle.crt;
        # 私钥文件路径
        ssl_certificate_key /home/kmaidol/cert/2_maidol.pw.key;

        location / {
            # 代理到上面定义的 upstream，名字要一致
            proxy_pass http://shadowsocksManager;
        }
    }
}
```

> **注意**：原配置在同一个 server 里同时 `listen 80` 和 `listen 443`，又写了 `ssl on;`。这样 80 端口也会被强制走 SSL，HTTP 访问会失败。正确写法是 `listen 443 ssl;`。另外，`ssl on;` 指令在 Nginx 1.15 起已经废弃。

## 10. MySQL（源码编译安装）

### 10.1 准备环境

```bash
sudo apt-get install build-essential libncurses5-dev cmake

# 创建 mysql 用户（禁止登录）和数据目录
sudo groupadd mysql
sudo useradd -s /sbin/nologin -g mysql mysql
sudo mkdir -p /data/mysql/data
```

### 10.2 下载源码

MySQL 5.7.5 之后的版本编译时依赖 boost，所以直接下载自带 boost 的源码包：

```bash
cd /usr/local/src
sudo wget http://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-boost-5.7.13.tar.gz
sudo tar zxvf mysql-boost-5.7.13.tar.gz
cd mysql-5.7.13/
```

> 网上有些教程会先执行 `sh BUILD/autorun.sh`，**不要执行**，否则会安装失败。

### 10.3 编译安装

从 MySQL 5.5 开始，`./configure` 编译配置方式已经取消，改用 `cmake`：

```bash
cmake . -DCMAKE_INSTALL_PREFIX=/usr/local/mysql \
  -DSYSCONFDIR=/etc \
  -DMYSQL_DATADIR=/data/mysql/data \
  -DWITH_MYISAM_STORAGE_ENGINE=1 \
  -DWITH_INNOBASE_STORAGE_ENGINE=1 \
  -DWITH_PARTITION_STORAGE_ENGINE=1 \
  -DWITH_FEDERATED_STORAGE_ENGINE=1 \
  -DWITH_BLACKHOLE_STORAGE_ENGINE=1 \
  -DEXTRA_CHARSETS=all \
  -DDEFAULT_CHARSET=utf8mb4 \
  -DDEFAULT_COLLATION=utf8mb4_general_ci \
  -DWITH_EMBEDDED_SERVER=1 \
  -DENABLED_LOCAL_INFILE=1 \
  -DENABLE_DTRACE=0 \
  -DWITH_BOOST=boost \
  -DENABLE_DOWNLOADS=1

make
sudo make install
```

主要参数说明：

| 参数 | 说明 |
| --- | --- |
| `-DCMAKE_INSTALL_PREFIX=/usr/local/mysql` | 安装路径 |
| `-DMYSQL_DATADIR=/data/mysql/data` | 数据目录 |
| `-DDEFAULT_CHARSET=utf8mb4` | 默认字符集 |
| `-DDEFAULT_COLLATION=utf8mb4_general_ci` | 默认排序规则 |
| `-DWITH_INNOBASE_STORAGE_ENGINE=1` | 安装 InnoDB 引擎 |
| `-DWITH_BOOST=boost` | boost 的位置（源码包自带的 `boost` 目录） |
| `-DENABLE_DOWNLOADS=1` | 下载可选文件，例如 Google 的测试套件，用于运行单元测试 |

### 10.4 初始化

```bash
# 目录授权
sudo chown -R mysql:mysql /usr/local/mysql
sudo chown -R mysql:mysql /data/mysql/

# 生成配置文件（5.7.18 起不再提供 my-default.cnf，需要自己新建 /etc/my.cnf）
sudo cp /usr/local/mysql/support-files/my-default.cnf /etc/my.cnf

# 初始化数据库（/data/mysql/data 必须为空）
sudo /usr/local/mysql/bin/mysqld --initialize --user=mysql --explicit_defaults_for_timestamp=1
```

如果出现下面的警告：

```text
[Warning] TIMESTAMP with implicit DEFAULT value is deprecated. Please use --explicit_defaults_for_timestamp server option (see documentation for more details).
```

在 `/etc/my.cnf` 的 `[mysqld]` 段加上 `explicit_defaults_for_timestamp = 1` 即可。

### 10.5 注册服务并启动

```bash
sudo cp /usr/local/mysql/support-files/mysql.server /etc/init.d/mysql
sudo service mysql start
```

### 10.6 配置环境变量

不配置的话，`mysql` 客户端命令不可用。在 `/etc/profile` 末尾添加：

```bash
export PATH=/usr/local/mysql/bin:$PATH
```

然后执行 `source /etc/profile` 使其生效。

### 10.7 修改 root 密码

MySQL 5.7 使用 `mysqld --initialize` 初始化时，会为 root 生成一个**临时密码**，并打印在初始化命令的输出和错误日志中（行内包含 `A temporary password is generated for root@localhost`）。

> 原文说"密码保存在 `/root/.mysql_secret`"，那是 MySQL 5.6 用 `mysql_install_db` 初始化时的行为，5.7 的 `--initialize` 不会生成这个文件。

用临时密码登录后修改密码：

```bash
mysql -u root -p
```

```sql
ALTER USER 'root'@'localhost' IDENTIFIED BY 'yourpassword';
```

> 5.7.6 以前的写法是 `SET PASSWORD = PASSWORD('yourpassword');`，新版本已经废弃。

### 10.8 添加允许远程访问的用户

```sql
-- MySQL 5.7 写法
GRANT ALL PRIVILEGES ON *.* TO 'username'@'%' IDENTIFIED BY 'yourpassword';
FLUSH PRIVILEGES;

-- MySQL 8.0 起 GRANT 不能再创建用户，需要分两步
CREATE USER 'username'@'%' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON *.* TO 'username'@'%';
```

格式为 `GRANT 权限 ON 数据库名.表名 TO 用户@登录主机`。`@` 后面是允许访问的客户端 IP 或主机名：`%` 表示任意客户端；如果写 `localhost`，这个用户就只能本地访问，不能远程访问。

查看用户：

```sql
USE mysql;
SELECT user, host FROM user;
```

## 11. Redis（源码安装）

### 11.1 编译

```bash
sudo apt-get install make
wget http://download.redis.io/releases/redis-3.2.1.tar.gz
tar xzf redis-3.2.1.tar.gz
cd redis-3.2.1
make
make test
```

编译好的程序在 `src` 目录下，可以直接运行：

```bash
src/redis-server --port 6380
# 或指定配置文件
src/redis-server /etc/redis/redis.conf

# 内置客户端
src/redis-cli
```

### 11.2 安装到系统

```bash
sudo make install
```

安装后就不需要用 `src/redis-server` 启动，直接执行 `redis-server` 即可。

> **注意**：`redis-server` 不带参数启动时**不会**读取任何配置文件，而是使用内置的默认配置，并提示 `no config file specified, using the default config`。一般都要指定配置文件启动：`redis-server /etc/redis/redis.conf`。

停止服务：

```bash
redis-cli shutdown
```

### 11.3 后台运行

编辑 `redis.conf`，把 `daemonize no` 改为：

```ini
daemonize yes
```

### 11.4 注册为系统服务并开机启动

```bash
sudo mkdir -p /etc/redis
# 服务脚本默认读取 /etc/redis/<端口>.conf
sudo cp ./redis.conf /etc/redis/6379.conf
sudo cp ./utils/redis_init_script /etc/init.d/redis

sudo service redis start
sudo service redis stop

# 开机启动
sudo update-rc.d redis defaults
```

也可以直接运行源码包里的 `sudo ./utils/install_server.sh`，它会交互式地完成上面这些步骤。

### 11.5 允许远程访问并开启密码验证

编辑 `redis.conf`：

```ini
# 注释掉 bind，或改为 0.0.0.0，允许其他主机访问
# bind 127.0.0.1

# 开启密码验证
requirepass yourpassword
```

> Redis 3.2 起默认开启 `protected-mode`：没有设置密码并且没有配置 bind 时，会拒绝远程连接。设置了 `requirepass` 后可以正常远程访问。

远程登录：

```bash
redis-cli -h <ip> -p <port> -a yourpassword
```

## 12. Hexo

参见 [Hexo + GitHub Pages 搭建博客](/2016/07/06/hexo-deploy/)。

## 13. Cloud9 IDE

[c9/core](https://github.com/c9/core)（该项目已经停止维护）：

```bash
git clone https://github.com/c9/core.git c9
cd c9
scripts/install-sdk.sh
node server.js --auth username:password
```

然后访问 `http://localhost:8181/ide.html`。

## 14. RabbitMQ

RabbitMQ 依赖 Erlang。下面记录了几种安装方式，**实测只有 14.3 的二进制包方式和 14.5 的 Docker 方式可行**。

### 14.1 源码安装 Erlang

```bash
wget http://erlang.org/download/otp_src_19.0.tar.gz
tar zxvf otp_src_19.0.tar.gz
cd otp_src_19.0
./configure --prefix=/home/kmaidol/erlang
make
make install
```

如果 `configure` 报错：

```text
configure: error: No curses library functions found
configure: error: /bin/sh '/home/kmaidol/erlang/configure' failed for erts
```

原因是缺少 ncurses 包，安装后重新执行 `configure`：

```bash
sudo apt-get install libncurses5-dev
```

在 `/etc/profile` 中添加环境变量，然后执行 `source /etc/profile` 使其生效：

```bash
# set erlang environment
export PATH=$PATH:/home/kmaidol/erlang/bin
```

执行 `erl`，能进入 Erlang shell 就说明安装成功。

### 14.2 源码安装 RabbitMQ

```bash
wget https://github.com/rabbitmq/rabbitmq-server/archive/rabbitmq_v3_6_3.tar.gz
tar zxvf rabbitmq_v3_6_3.tar.gz
cd rabbitmq_v3_6_3
make
make install
```

如果 `make` 时报错 `error: rabbitmq-components.mk must be updated!`，先执行下面的命令，再重新 `make`：

```bash
make rabbitmq-components-mk
```

在 `/etc/profile` 中添加环境变量，并执行 `source /etc/profile`：

```bash
# set rabbitmq environment
export PATH=$PATH:/usr/rabbitmq/sbin
```

启动：`rabbitmq-server start`。

### 14.3 使用预编译二进制包安装（实测可行）

```bash
# 安装 Erlang 及依赖；缺少依赖时启动会报 error missing_dependencies,[crypto,ssl]
sudo apt-get install -y erlang-nox erlang-dev erlang-src

# 下载并解压二进制包
wget http://www.rabbitmq.com/releases/rabbitmq-server/v3.6.3/rabbitmq-server-generic-unix-3.6.3.tar.xz
xz -d rabbitmq-server-generic-unix-3.6.3.tar.xz
tar -xvf rabbitmq-server-generic-unix-3.6.3.tar

# 建议放到当前用户目录下，避免 sudo 时出现 command not found
cp -rf ./rabbitmq_server-3.6.3 /home/k/rabbitmq
```

在 `/etc/profile` 中添加环境变量，并执行 `source /etc/profile`：

```bash
# set rabbitmq environment
export PATH=$PATH:/home/k/rabbitmq/sbin
```

常用命令：

```bash
rabbitmq-server start      # 前台启动
rabbitmq-server -detached  # 后台启动
rabbitmqctl status         # 查看状态
rabbitmqctl stop           # 停止
```

### 14.4 使用 apt-get 安装

> 下面的 `www.rabbitmq.com/debian` 软件源已经停用，新版本请参考[官方文档](https://www.rabbitmq.com/install-debian.html)。

```bash
sudo apt-get update
sudo apt-get -y upgrade

# 添加 RabbitMQ 软件源
echo "deb http://www.rabbitmq.com/debian/ testing main" | sudo tee -a /etc/apt/sources.list
# 添加签名 key
curl http://www.rabbitmq.com/rabbitmq-signing-key-public.asc | sudo apt-key add -

sudo apt-get update
sudo apt-get install rabbitmq-server
```

### 14.5 使用 Docker 部署（推荐）

**官方镜像**（[rabbitmq](https://hub.docker.com/_/rabbitmq/)）：

```bash
docker pull rabbitmq

# 使用默认配置启动
docker run -d --hostname my-rabbit --name some-rabbit rabbitmq:3

# 启用 Web 管理后台，需要使用 3-management 标签
docker run -d --hostname my-rabbit \
  --name rabbitmq \
  -p your-ip:15672:15672 \
  -p your-ip:5672:5672 \
  -e RABBITMQ_DEFAULT_USER=xxxx \
  -e RABBITMQ_DEFAULT_PASS=xxxx \
  -e RABBITMQ_DEFAULT_VHOST=my_vhost \
  rabbitmq:3-management
```

`your-ip` 不指定时默认是 `0.0.0.0`。进入容器管理：`docker exec -it rabbitmq /bin/bash`，`exit` 退出。对容器修改后，可以用 `docker commit` 固化为镜像。

**frodenas/rabbitmq 镜像**（[frodenas/rabbitmq](https://hub.docker.com/r/frodenas/rabbitmq/)）：

```bash
docker pull frodenas/rabbitmq
docker run -d --hostname my-rabbit \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_USERNAME=username \
  -e RABBITMQ_PASSWORD=pwd \
  -e RABBITMQ_VHOST=myvhost \
  frodenas/rabbitmq
```

### 14.6 Web 管理后台与用户管理

启用管理插件：

```bash
rabbitmq-plugins enable rabbitmq_management
```

然后在浏览器访问 `http://[your IP]:15672/`。

默认用户 `guest`（密码 `guest`）拥有 `/` 虚拟主机的全部权限，但**只能从 localhost 访问**（包括管理插件），建议删除或修改密码。如果需要临时解除限制，可以在配置文件 `rabbitmq.config` 中添加：

```erlang
[{rabbit, [{loopback_users, []}]}].
```

用 guest 远程登录并创建管理员用户后，再删掉这段配置，guest 就无法远程登录了，之后改用新用户登录。

> 二进制安装包默认没有这个配置文件（`/etc/rabbitmq/rabbitmq.config`），可以从源码包中复制示例文件 `docs/rabbitmq.config.example`。

用户与权限管理：

```bash
# 新增用户
rabbitmqctl add_user username password
# 设置 administrator 角色，设置角色后才能登录 Web 管理后台
rabbitmqctl set_user_tags username administrator
# 查看用户列表
rabbitmqctl list_users
# 修改用户密码
rabbitmqctl change_password username newpassword

# 新建 virtual host
rabbitmqctl add_vhost test_host
rabbitmqctl list_vhosts

# 给用户 test 分配 test_host 的权限，三个正则依次是 configure / write / read 权限
rabbitmqctl set_permissions -p test_host test "test-*" ".*" ".*"
```

执行完上面的命令后，用户 `test` 就可以访问虚拟主机 `test_host` 的资源了。

## 15. SSH 免密码登录

目标：让 A 机免密码登录 B 机（假设 B 机为 `192.168.1.181`，用户为 `user`）。

**第 1 步：在 A 机上生成密钥对**

```bash
ssh-keygen -t rsa -P ''
```

`-P` 指定密钥的密码，`-P ''` 表示空密码。不加 `-P` 的话，需要按三次回车。命令会在 `~/.ssh/` 下生成 `id_rsa`（私钥）和 `id_rsa.pub`（公钥）。

**第 2 步：把公钥复制到 B 机**

推荐直接用 `ssh-copy-id`，一步完成复制和追加：

```bash
ssh-copy-id user@192.168.1.181
```

也可以手动操作：

```bash
# 在 A 机上执行
scp ~/.ssh/id_rsa.pub user@192.168.1.181:~/id_rsa.pub

# 在 B 机上执行
mkdir -p ~/.ssh && chmod 700 ~/.ssh
cat ~/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

> `authorized_keys` 的权限必须是 600，`~/.ssh` 目录的权限必须是 700，否则 sshd 会拒绝使用这个公钥。

**第 3 步：在 A 机上登录 B 机**

```bash
ssh user@192.168.1.181
```

原理见 [学习笔记](/2016/06/27/study-note/) 中的"SSH 原理"部分。

## 16. 流量监控

```bash
# iftop：实时查看网卡流量
sudo apt-get install iftop
sudo iftop -i eth0

# vnstat：按小时、天、月统计流量
sudo apt-get install vnstat
vnstat -i eth0
```

> 待补充：shadowsocks 按端口限制流量和带宽、用 iptables 统计流量。
