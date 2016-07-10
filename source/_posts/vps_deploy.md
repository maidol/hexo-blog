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
>>- 如果需要远程登陆指定的数据库, 需要在对应的数据库里创建用户(). 例如有数据库 test, 则`use test`, 再在test数据库创建用户 `db.addUser('kmaidol','xxxxxx')`, 之后就可以使用这个用户访问test
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
>- nginx 配置 (含ssl)
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
>- 安装环境准备 
>>- `sudo apt-get install build-essential libncurses5-dev cmake` 
>>- `sudo groupadd mysql` `sudo useradd -g mysql mysql` `sudo mkdir -p /data/mysql/` `sudo mkdir -p /data/mysql/data/`
>- mysql5.7.5之后版本都要安装boost包。所以我选择是下载已经自带boost安装包的mysql安装包：
>- `wget http://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-boost-5.7.13.tar.gz`
>- `tar zxvf mysql-boost-5.7.13.tar.gz` `cd mysql-5.7.13/`
>- `sh BUILD/autorun.sh`
>- MySQL从5.5版本开始，通过./configure进行编译配置方式已经被取消，取而代之的是cmake工具 
>- `cmake -DCMAKE_INSTALL_PREFIX=/usr/local/mysql -DSYSCONFDIR=/etc -DWITH_MYISAM_STORAGE_ENGINE=1 -DWITH_INNOBASE_STORAGE_ENGINE=1 -DWITH_PARTITION_STORAGE_ENGINE=1 -DWITH_FEDERATED_STORAGE_ENGINE=1 -DEXTRA_CHARSETS=all -DDEFAULT_CHARSET=utf8mb4 -DDEFAULT_COLLATION=utf8mb4_general_ci -DWITH_EMBEDDED_SERVER=1 -DENABLED_LOCAL_INFILE=1 -DWITH_BOOST=boost -DENABLE_DOWNLOADS=1` 
>- mysql configure 安装参数解释：
>>- -DCMAKE_INSTALL_PREFIX=/usr/local/mysql #指定安装路径 
-DDEFAULT_CHARSET=utf8mb4 #默认使用utf8mb4字符 
-DDEFAULT_COLLATION=utf8mb4_general_ci #校验字符 
-DWITH_INNOBASE_STORAGE_ENGINE=1 #安装innodb引擎  
-DWITH_BOOST=boost #指定boost的安装位置 
-DENABLE_DOWNLOADS #是否要下载可选的文件。例如，启用此选项（设置为1），cmake将下载谷歌所使用的测试套件运行单元测试 
>- `make && make install` 
>- `chown -R mysql:mysql /usr/local/mysql #对mysql目录进行赋予权限` 
>- 生成mysql配置文件 `cp /usr/local/mysql/support-files/my-default.cnf /etc/my.cnf` 
>- 对数据库进行初始化 `/usr/local/mysql/bin/mysqld --initialize --user=mysql` 
>- 复制文件mysql.server 可以使用service 命令进行控制 `cp /usr/local/mysql/support-files/mysql.server /etc/init.d/mysql` `service mysql start` #启动mysql 
>- 登录数据库修改密码 `/usr/local/mysql/bin/mysql -u root -p` 
>- 输入密码回车。登录成功后，输入以下字符，来修改密码，比如我要修改密码为root `set password = password('root');` 
- 源码安装redis, 并设置远程登陆
>- 安装make `sudo apt-get make`
>- 获取安装包 `wget http://download.redis.io/releases/redis-3.2.1.tar.gz`
>- 安装 `tar xzf redis-3.2.1.tar.gz` `cd redis-3.2.1` `make`
>- The binaries that are now compiled are available in the src directory. Run Redis with: `src/redis-server` 
>- You can interact with Redis using the built-in client: `src/redis-cli`
>- 设置守护进程运行redis
>>- `vim redis.conf` 修改 `daemonize no` -> `daemonize yes`
>- `make install`, 执行这句命令可把redis安装到系统, 就无需使用 `src/redis-server` 来启动, 直接 `redis-server`
>- 启动redis服务, 一般需指定自定义的配置文件 `redis-server redis.conf`, 不指的话则读取默认配置 
>- 停止redis服务 `redis-cli shutdown` 
>- 设置远程登陆, 并开启密码验证 
>>- `vim redis.conf`, 找到requirepass，然后修改如下: requirepass yourpassword; `# bind 127.0.0.1` 去除 # 
>>- 登陆 `redis-cli -h ip -p port -a yourpassword ` 
>- 设置 redis 开机启动
- 安装hexo
>- 配置环境
>>- 安装node, 安装git
>>- 安装hexo
>>>- `mkdir blog` `cd ./blog` `npm install-g hexo` 
>>>- 初始化 `hexo init` 
>>>- 生成静态页 `hexo generate` or `hexo g` 
>>>- 本地启动服务 `hexo server` 浏览器输入http://localhost:4000 
>>- 配置Github, 部署到Github 
>>>- 登陆Github, 建立Repository. 建立与你用户名对应的仓库，仓库名必须为【your_user_name.github.io】 
>>>- 建立关联 
>>>>- `cd ./blog` `vim _config.yml` 翻到最后, 如下编辑 
deploy: 
type: git 
repo: https://github.com/maidol/maidol.github.io.git 
branch: master 
>>>>- 执行命令 `npm install hexo-deployer-git --save` 
>>>>- 配置github用户信息 `git config --global user.email "you@example.com"` `git config --global user.name "Your Name"` 
>>>>- 本地执行部署 `git pull` `hexo deploy` 浏览器中输入http://maidol.github.io/ 
>>>>- 每次部署的步骤 `hexo clean` `hexo generate` `hexo deploy` 
>>- Hexo的常用命令 
>>>- `hexo new"postName"` #新建文章 
>>>- `hexo new page"pageName"` #新建页面 
>>>- `hexo generate` #生成静态页面至public目录 
>>>- `hexo server` #开启预览访问端口 
>>>- `hexo deploy` #将.deploy目录部署到GitHub 
- 流量监控 vnstat/iftop 