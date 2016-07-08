---
title: vps-deploy
date: 2016-7-06 22:37:00
tags: vps linode vpn nginx
---
- 创建普通用户, 之后所有的操作使用新用户登录进行
>- `adduser kmaidol` 创建用户kmaidol
>- 设置sodu权限
>>- `apt-get install vim`
>>- `chmod 744 /etc/sudoers` 获取写权限
>>- `vim /etc/sudoers` 编辑如下, 获得sudo权限
    # User privilege specification
    root ALL=(ALL) ALL
    kmaidol ALL=(ALL) ALL
>>- 使用 kmaidol 登陆
- 设置时区
>- `tzselect` 执行命令按提示操作
>- 设置localtime `sudo cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime`
>- `date` 查看时间
>- 更多时区信息可以在以下目录中去选取：`cd /usr/share/zoneinfo/`
- 安装 nvm node
>- 安装 curl `sudo apt-get install curl`
>- `curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.0/install.sh | bash`
>- 激活 nvm, 进入用户文件夹 /home/kmaidol, 执行 `. ~/.nvm/nvm.sh`
>- 安装node `nvm install v6`
>>- 登陆默认启动版本 `nvm alias default 0.10.x`
>- 安装nrm, 管理下载源  `npm install -g nrm`  命令 nrm ls/use/...
>- 安装bower  `npm install -g bower`
>- 安装pm2  `npm install -g pm2`
- 安装 git
>- `sudo apt-get install git`
- 源码安装shadowsocks 一次性验证
>- `sudo apt-get update` `sudo apt-get install -y python python-setuptools`
>- `git clone https://github.com/shadowsocks/shadowsocks.git`
>- `cd ./shadowsocks`
>- `git checkout master`
>- `sudo python setup.py install`
>- `ssserver -h`
>- 添加一次性验证 运行ssserver 时增加参数 `-a`, 或者 ss.json 文件添加 `'auth': true`
>- ss.json {
                "server": "159.203.234.63",
                "port_password": {
                        "10080":"123456"
                },
                "timeout": 300,
                "method": "aes-256-cfb"
             }
>- 启动shadowsocks `ssserver --manager-address 127.0.0.1:6001 -c ss.json -d start`   -d 代表守护进程运行
- 安装mongodb
>- `sudo apt-get install mongodb`
>- `mongod -h` 查看帮助,  mongod就是服务程序, mongo是客户端shell
>- mongodb 实现远程连接
>>- 1,添加管理员账 
>>>- `mongo` 本机登陆mongo
>>>- > use admin 
        switched to db admin 
     > db.addUser('kmaidol','xxxxxx')
>>- 2. 配置/etc/mongodb.conf
>>>- #bind_ip = 127.0.0.1   //注释此行 
>>>- auth = true       //将此行前的注释去掉
>>- 3，重启mongodb
>>>- `/etc/init.d/mongod `
>>- 4. 防火墙开放27017端口
>>>- `iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 27017 -j ACCEPT `
- 安装tmux
>- `apt-get install tmux`
>- 新建会话 `tmux new -s @session`
- 部署 shadowsocks-manager
>- 获取源码 `git clone https://github.com/shadowsocks/shadowsocks-manager.git`
>- 安装 `npm install -g bower` `cd shadowsocks-manager` `npm install` `bower install`
>- `cd shadowsocks-manager` `mv config.js.sample config.js` `node server`
- 安装nginx
>- `sudo apt-get install nginx`
>- 常用命令 启动`nginx -c filename` 停止`nginx -s stop/quit/` `pkill -9 nginx`
>- 重载配置 `nginx -s reload`
>- 检查配置文件是否正确 `nginx -t`
>- nginx 配置
>>- ###
        worker_processes 1;
        events {
        }
        http {
        #负责压缩数据流
        gzip              on;  
        gzip_min_length   1000;  
        gzip_types        text/plain text/css application/x-javascript;

        #设定负载均衡的服务器列表
        #weigth参数表示权值，权值越高被分配到的几率越大
        upstream shadowsocksManager{
        server localhost:6003; #shadowsocksManager     
        }
        # test #
        server {
        listen       80;
        server_name  v1.maidol.pw;
        location / {
                proxy_pass   http://www.google.com;
        }
        }
        # maidol.pw #   
        server {
        #侦听的80端口
        listen       80;
        listen       443;
        server_name  maidol.pw;
        #启用SSL模块
        ssl on;
        #证书文件放置路径
        ssl_certificate /home/kmaidol/cert/1_maidol.pw_bundle.crt;
        #私钥文件放置路径
        ssl_certificate_key /home/kmaidol/cert/2_maidol.pw.key;
        
        location / {
                proxy_pass   http://shadowsocksManager;    #在这里设置一个代理，和upstream的名字一样
        }
        }
        }
- 安装mysql(源码编译安装), 并设置远程登陆
- 安装redis, 并设置远程登陆