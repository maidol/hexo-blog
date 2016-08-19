---
title: study-note
date: 2016-06-27 20:31:36
tags:
---

2016-07-14
==============

知识积累
--------------
- 用户管理模块的理解 v2.0
>- 跟之前的理解有不同
>>- 整棵组织结构树 反应了所有的岗位和人员组成 
>>- 抛弃数据权限标识, 使用组织结构节点对数据进行标识 
>>- 每个组织结构节点具体对应每个职业岗位, 例如研发部门(经理岗位), 下面可能就会有多个开发岗位, 开发人员1, 开发人员2, 开发人员3 ... 每个开发岗位(就是一个account)可能暂时会有人员空缺, 正常情况下都是一个岗位对应一个员工, 也可能有多个人共同在一个岗位上, 就是存在同岗的情况 共用相同的资源, 开发人员1, 开发人员2, 开发人员3 都是平行关系, 工作内容也是相同, 但是不同的岗位, 都是组织结构的组成部分, 员工会分配到这些岗位上。整个完整的组织结构应该就反应了所有岗位, 岗位作为最小单位, 而人就占到岗位上 
>>- 反应到现实, 岗位应该是预先就已经定好的, 招聘单位会根据用人情况进行招聘, 一个员工入职就会分配到具体岗位(节点), 经理或开发人员1,2,3... 
>>- 一个员工的对数据的curd应该是跟随所在岗位的。一个员工有可能身兼多岗位, 不同的岗位 登陆系统后 应该看到的数据是不同的, 假如身兼多职, 应该在登陆前或者登陆后会有个岗位选择, 选择不同岗位其对数据的操作是不同的, 这样设计是合理的。例如新增一条数据, 这条数据应该有个与当前选择的岗位有关联关系 。如果一个身兼多岗位的员工登陆系统, 不对岗位进行隔离, 那么对数据的操作会很混乱 
- 用户管理模块的理解
>- 用户管理
>>- 创建用户, 分配默认数据权限(可以随机生成一个标识), 默认角色, 默认用户组
>- 角色管理
>>- 如果考虑公司组织结构的情景, 可以把角色与组织结构关联(n-n关系), 用户不直接关联角色, 而是与组织结构管理, 这样做, 对用户而言, 用户模块会好用些, 用户创建新用户时只需关注组织结构, 分配组织结构就够了, 而角色则分配给组织结构节点(在创建结构节点时做)
>>- 如果考虑更加更加多维的情况, 例如多了一个与组织结构同级类别的情节, 则可以把该情节也与角色关联, 这时会有两个维度与角色关联, 甚至可能再出现第三个第四个, 也如法炮制; 一般情况下 用户 - 组织结构 - 角色 - 功能权限 - 接口 已经足够了 
>- 用户组管理(公司组织结构)
>>- 作为公司组织结构, 可以为树形结构, 有等级, 单纯的节点即组(没有任何业务如职位等)与用户 一对多关系
>>- 也可以是离散结构, 点与点之间可以没有关系, 或者可以有级别关系
>>- 组织结构只是用以表达一个关系, 与角色权限的控制没关系, 组织结构应该与数据的显示有一定关系, 例如可以通过配置或者代码的方式, 来定义规则, 限制数据的显示, 当前节点可以查看上下节点的数据
>>- 
>- 接口权限管理
>>- 接口权限必须由开发人员进行维护
>>- 会有个关联表a, 关联了接口和界面视图功能, 多对一关系
>>- 查找用户的接口权限时, 需要查出用户拥有的角色, 再查询这些角色对应的所有功能权限, 最后查询这些功能权限对应的所有接口权限, 用户访问后台接口时就需要这些进行验证
>- 功能权限管理(界面视图)
>>- 界面视图功能可以直接由用户进行维护
>>- 界面视图, 例如一个button对应的编辑功能操作, 可能会对应了几个后台接口, 这样的话, 视图功能与后台接口就有一对多的关系, 这个关系需要维护好, 当为一个角色分配一个视图功能的时候, 需要相应地为角色添加对应的几个接口权限
>>- 功能权限可以用在控制界面的显示上, 有某个功能权限才显示对应的button
>>- 功能权限应该可以分级别, 例如单功能, 模块, 视图, 单功能是最小的单位, 多个单功能组成模块, 多个模块组成视图, 模块和视图可以简化分配功能时的操作
>>- 功能权限与角色关联 
>>- 用户登录后, 会查询出用户拥有的功能权限(查出用户拥有的角色, 再查询这些角色对应的所有功能权限), 这些功能权限控制界面视图如何显示
>>- 假设某个功能权限依赖某个接口权限, 而某用户拥有这个接口权限, 其不一定就能看到这个功能权限对应的界面视图, 因为功能权限与接口权限是独立解耦的
>- 数据权限管理
>>- dataType, dataId, dataRightId, RWtype
>>- 创建用户, 默认会分配一个默认数据权限id, dataRightId, 这个权限id是用户的数据标识
>>- 用户新建一条业务数据时, 对数据拥有RWtype-write操作, 而且用户可以对这条数据为其他用户dataRightId指定读写RWtype
>>- 根据不同的系统不同的业务需求, 可定制自己的数据权限规则, 为这些规则添加新功能, 例如admin角色可以突破数据权限限制,可以rw所有业务数据, 这时可以在不改动现有功能和界面的情况下, 添加一个这样的接口功能; 又或者组织结构的上级可以rw所有下级的数据, 也如上根据这条规则添加新的功能接口, 不要改动原有的业务逻辑
>>- 用户的业务数据列表, 应该分开几个列表, 自己可编辑的数据列表(包括别人分配而来的), 自己只读的数据列表(包括别人分配而来的和系统规则决定的--例如默认可以看到结构上下级的数据), 代理别人的数据列表(包括可读可写)
>>- 用户的上级可以强制获取下级的业务数据的读写操作并且可以为下级用户分配, 这是一个新的功能接口, 应该在原有业务功能独立开来增加功能; admin可以强制获取所有用户的业务数据的读写操作并且可以为任何一个用户分配读写操作, 同样道理

2016-07-03
==============

知识积累
--------------
- 源码安装shadowsocks
>- `apt-get update` `apt-get install -y python python-setuptools`
>- `git clone https://github.com/shadowsocks/shadowsocks.git`
>- `cd ./shadowsocks`
>- `sudo python setup.py install`
>- `ssserver -h`
>- 添加一次性验证 运行ssserver 时增加参数 `-a`, 或者 ss.json 文件添加 `'auth': true`
- linux部署环境
>- redis + nginx + mysql + mongod + vnstat + vnstatsvg + pm2 + 2个node后台程序 + 邮件服务, 占用才284M


2016-07-01
==============

知识积累
--------------
- 协议
>- socket不是一个协议，而是一个软件的抽象层，是对tcp/ip的封装实现，有各种语言版本的接口实现（c, c++ ,python, c# ...）
>- http ftp websocket socks 都是协议，而且是建立在tcp/ip协议之上，这些协议在通信前，需要先通过握手建立tcp/ip连接，然后才能发送数据，这些不同的协议根据自身的使用场景，对应的tcp/ip连接有不同的连接方式--长连接/短连接/实时连接
>>- http协议，通过tcp/ip握手建立连接，然后发送数据，收到数据后就断开连接
>>- websocket协议, ....................，保持与远程的连接，收发数据
>>- socks协议, ......................., 保持与远程的连接，收发转发数据
>>- socket, 本身就是tcp/ip的抽象实现
- shadowsocks android
>- 如果出现无法连接的情况（网络从wifi切换为移动网络/移动网络切换为wifi/从a wifi切换到b wifi 导致）, 尝试以下方法
>>- 方法一 把shadowsocks后台客户端连接关闭，再打开
>>- 方法二 把系统语言重英文切换为中文或者从中文切换为英文，再重启手机
- ss启动方式
>- ssserver --manager-address v1.maidol.pw:6001 -c ss.json -d start
>-一次性验证，就是每次发送数据到代理服务器，都在数据包添加一些验证数据
- ubuntu 部署shadowsocks vpn
>- 部署shadowsocks
>>- 安装shadowsocks `apt-get install python-pip` `pip install shadowsocks `
>>- 启动shadowsocks `ssserver --manager-address 127.0.0.1:6001 -c ss.json -d start`   -d 代表守护进程运行
>>>- --manager-adddress 设置shadowsocks的管理ip和port, shadowsocks api 通过此端口被其他程序访问 [manage api 简介](https://github.com/shadowsocks/shadowsocks/wiki/Manage-Multiple-Users)
>>>- ss.json {
                "server": "159.203.234.63",
                "port_password": {
                        "10080":"123456"
                },
                "timeout": 300,
                "method": "aes-256-cfb"
             }
>>>- ss.json文件 server 填写实际ip 不要填写域名，因为本机需要 `vim /etc/hosts` 添加 `127.0.0.1 v1.maidol.pw` 或者 `在局域网的地址 v1.maidol.pw`，server 填写域名v1.maidol.pw的话会导致外部访问不到shadowsocks服务
>>- 停止 `shadowsocks -d stop`
>- 部署shadowsocks-manager [](https://github.com/shadowsocks/shadowsocks-manager)
>>- 为保证安全，manager项目应该与shadowsocks vpn 部署在同一个局域网里面
>>- 上面 --manager-address 设置ip为127.0.0.1，则两个项目部署在同一个服务器里，需要 `vim /etc/hosts` 添加 `127.0.0.1 v1.maidol.pw` 才能保证manager项目可以访问shadowsocks api；--manager-address 设置ip为机器的局域网地址，需要 `vim /etc/hosts` 添加 `在局域网的地址 v1.maidol.pw`；如果 --manager-address 设置为外部域名或ip，则shadowsocks api 可以被局域网之外的机器访问到，不安全；因此manager项目部署在同一个局域网比较合理
>>- 依赖Nodejs  4.4 Mongodb 3.2
>>- 获取源码 `git clone https://github.com/shadowsocks/shadowsocks-manager.git`
>>- 安装 `npm install -g bower` `cd shadowsocks-manager` `npm install` `bower install`
>>- `cd shadowsocks-manager` `mv config.js.sample config.js` `node server`
>>- 创建服务器，其port 对应 127.0.0.1:6001 , 必须一致
- shadowsocks-android 无法连接的问题
>- 先关闭连接，尝试点击重置选项（重置所有后台服务），再连接，检测网络，是否成功


2016-05-29
==============

知识积累
--------------
- 微服务架构
>- 外部通过restapi通信, 微服务之间通过异步消息队列进行通信


2016-05-26
==============

知识积累
--------------
- ssh原理
> - 为了更好的理解SSH免密码登录原理，我们先来说说SSH的安全验证，SSH采用的是”非对称密钥系统”，即耳熟能详的公钥私钥加密系统，其安全验证又分为两种级别。  
>> - 1. 基于口令的安全验证
这种方式使用用户名密码进行联机登录，一般情况下我们使用的都是这种方式。整个过程大致如下：
（1）客户端发起连接请求。
（2）远程主机收到用户的登录请求，把自己的公钥发给客户端。
（3）客户端接收远程主机的公钥，然后使用远程主机的公钥加密登录密码，紧接着将加密后的登录密码连同自己的公钥一并发送给远程主机。
（4）远程主机接收客户端的公钥及加密后的登录密码，用自己的私钥解密收到的登录密码，如果密码正确则允许登录，到此为止双方彼此拥有了对方的公钥，开始双向加密解密。
PS：当网络中有另一台冒牌服务器冒充远程主机时，客户端的连接请求被服务器B拦截，服务器B将自己的公钥发送给客户端，客户端就会将密码加密后发送给冒牌服务器，冒牌服务器就可以拿自己的私钥获取到密码，然后为所欲为。因此当第一次链接远程主机时，在上述步骤的第（3）步中，会提示您当前远程主机的”公钥指纹”，以确认远程主机是否是正版的远程主机，如果选择继续后就可以输入密码进行登录了，当远程的主机接受以后，该台服务器的公钥就会保存到 ~/.ssh/known_hosts文件中。
>> - 2. 基于密匙的安全验证
这种方式你需要在当前用户家目录下为自己创建一对密匙，并把公匙放在需要登录的服务器上。当你要连接到服务器上时，客户端就会向服务器请求使用密匙进行安全验证。服务器收到请求之后，会在该服务器上你所请求登录的用户的家目录下寻找你的公匙，然后与你发送过来的公匙进行比较。如果两个密匙一致，服务器就用该公匙加密“质询”并把它发送给客户端。客户端收到“质询”之后用自己的私匙解密再把它发送给服务器。与第一种级别相比，第二种级别不需要在网络上传送口令。
PS：简单来说，就是将客户端的公钥放到服务器上，那么客户端就可以免密码登录服务器了，那么客户端的公钥应该放到服务器上哪个地方呢？默认为你要登录的用户的家目录下的 .ssh 目录下的 authorized_keys 文件中（即：~/.ssh/authorized_keys）


2016-05-02
==============

知识积累
--------------
- nginx

2016-04-24
==============

知识积累
--------------
- es6 harmony-reflect [源码地址](https://github.com/tvcutsem/harmony-reflect)
> - 使用harmony-reflect实现aop


2016-04-14
==============

知识积累
--------------
- Promise 理解 [http://www.cnblogs.com/fsjohnhuang/p/4135149.html](http://www.cnblogs.com/fsjohnhuang/p/4135149.html)  
![Promise执行流程](E:\Records\Study\Promise执行流程.png)
> - `function Promise(fn){
      this.status = 'pending';
      this._resolve = [];
      this._reject = [];
      this.resolve = function(value){ this.status = 'resolve'; for item in this._resolve, item(value);};
      this.reject = function(err){ this.status = 'reject'; for item in this._reject, item(err);};
      this.then = function(resolve, reject){ this._resolve.push(resolve); this._reject.push(reject); 最后 return 一个promise类型};
      this.catch = function(null, reject){ this._resolve.push(null); this._reject.push(reject);};
      fn(this.resolve, this.reject);
  }
  Promise.resolve = function(value){ return new Promise(function(resolve, reject){ resolve(value);});};
  Promise.reject = function(reason){ return new Promise(function(resolve, reject{ reject(reason);}));};`
> - fn是一个异步任务, 在任务完成时执行resolve, 失败报错时执行reject, 以下为示例
>> - `function getImg(url) {  
    var p = Promise();  
    var img = new Image();  
    img.onload = function() {  
        p.resolve(this);  
    };  
    img.onerror = function(err) {  
        p.reject(err);  
    };  
    img.url = url;  
    return p;  
};`
>> - `function getImg(url) {  
    return Promise(function(resolve, reject) {  
        var img = new Image();  
        img.onload = function() {  
            resolve(this);  
        };  
        img.onerror = function(err) {  
            reject(err);  
        };  
        img.url = url;  
    });  
};`
>> - 状态转换事件处理函数(then(resolve,reject)), resolve或reject会return一个值,由于resovle的入参为非thenable对象或非Promise对象，因此直接修改当前promise的状态和保存状态转换事件处理函数的实参即可（若resolve的入参为thenable对象或Promise对象，则将控制权交给该对象，由该对象来设置当前promise的状态和状态转换事件处理函数的实参），然后将控制权移交 finale方法 。finale方法内部会遍历deffereds数组并根据状态调用对应的处理函数和修改promise链表中下一个promise对象的状态。


2016-03-27
==============

知识积累
--------------
- Tmux Resurrect & Continuum: 持久保存 Tmux 会话 [工具教程](https://linuxtoy.org/archives/tmux-resurrect-and-continuum.html)
> - 需要注意的是，使用这两个 Tmux 插件要求 Tmux 是 1.9 及以上版本
> - Tmux Resurrect 能够备份 Tmux 会话的各种细节，包括所有会话、窗口、窗格以及它们的顺序，每个窗格的当前工作目录，精确的窗格布局，活动及替代的会话和窗口，窗口聚焦，活动窗格，窗格中运行的程序等等，非常贴心。安装 Tmux Resurrect，可执行：
>> - `mkdir ~/.tmux` `cd ~/.tmux` `git clone https://github.com/tmux-plugins/tmux-resurrect.git`
>> - 官方推荐通过 Tmux 插件管理器来安装，如果你需要安装多个插件，不妨自行尝试。然后在 ~/.tmux.conf 中添加下列内容：`run-shell ~/.tmux/tmux-resurrect/resurrect.tmux`
>> - 保存后，重载 Tmux 配置：`tmux source-file ~/.tmux.conf`
>> - 现在，要保存 Tmux 会话，我们只要按 前缀键 + Ctrl-s 就可以了。此时，Tmux 状态栏会显示“Saving ...”字样，完毕后会提示 Tmux 环境已保存。还原则按 前缀键 + Ctrl-r 即可
> - Tmux Continuum 更进一步，它将 Tmux 会话的保存及还原自动化，定时备份，然后在 Tmux 启动时还原
>> - Tmux Continuum 的安装 `cd ~/.tmux` `git clone https://github.com/tmux-plugins/tmux-continuum.git` 
>> - 接着，将以下内容添加到 ~/.tmux.conf：`run-shell ~/.tmux/tmux-continuum/continuum.tmux`
>> - Tmux Continuum 默认每隔 15 分钟备份一次，如果你觉得频率过高，可以设置为 1 小时一次：`set -g @continuum-save-interval '60'`
>> - 重载 Tmux 配置 `tmux source-file ~/.tmux.conf`
- ubuntu源码安装tmux2.0
> - tmux依赖libevent 2.x，[下载源码安装](http://libevent.org)
> - 安装 `sudo apt-get install libncurses-dev`, 避免error: "curses not found"
> - 安装完成重新登陆终端，避免error: cannot open shared object file: No such file or directory
- 安装licode遇到mongodb启动时报错 ERROR: Insufficient free space for journal files  Please make at least 3379MB available in /var/lib/mongodb/journal or use --smallfiles
> - 至少需要3Gb的硬盘空间是，可以使用小文件 来解决
请使用下面命令：
`/usr/local/mongodb/bin/mongod --smallfiles --dbpath=/usr/local/mongodb/data --logpath=/usr/local/mongodb/logs/mongodb.log --port=12789 --logappend&`，
即加上--smallfiles参数即可
`ps  -ef |grep mongodb` 或者 `netstat -an |grep 12789` 查看是否启动成功
- `ulimit -a`
- docker 安装 licode(git clone最新版本)
> - dockerfile的镜像使用ubuntu14.04，安装时保证网络通畅（尽量翻墙下载）
> - 使用dockerfile进行安装`docker build -t licode-image .`, 如果安装不成功（网络原因或者其他）, 则如下命令进入容器，继续重新安装，确保每一步都能安装成功。
>> - `./installUbuntuUnattend.sh`，安装所有依赖，必须确保没有error，对于warnning可以忽略
>> - `./installZerio.sh`，这步会下载安装node 0.10.37，下载安装失败的话则会导致后面编译失败
>> - `./installNuve.sh`，安装过程会启动mongodb，必须确保mongodb启动成功，有可能会因为硬盘空间不足而启动失败，这时就要手动重新启动，或者修改对应的启动脚本进行启动。这一步会产生licode_config.js文件
> - `docker run -it --name licode -p 3001:3001 -p 3004:3004 -p 8080:8080 -p 3000:3000 -p 30000-31000:30000-31000/udp licode-image-work /bin/bash` , 启动容器， 如果启动失败报错，有可能是防火墙iptables的路由限制udp，udp的范围调整一下-`-p 30000-30100:30000-30100/udp` 
>>- 改进 ``docker run -id --name licode -p 3001:3001 -p 3004:3004 -p 8080:8080 -p 3000:3000 -p 30000-31000:30000-31000/udp licode-image-work ./init.sh` ,/bin/bash 放在脚本init.sh里, 使用参数 -di 
>> - `-it` 参数启动容器, 容器里面的程序不会在后台运行, 当从容器的控制台退出, 当前session运行的程序就会退出, 最好使用`-d`参数run容器, 然后`exec -it $容器名称 /bin/bash`进入容器控制台进行操作 
>>- 或者参考这种做法 I´d recommend that when using this image in the form that is shown in this example, you disable userland-proxy adding this to `vim /etc/default/docker`: DOCKER_OPTS="--userland-proxy=false" ; `sudo service docker restart` 
If you don´t, docker will try to start a proxy process for each of the ports you are exposing from 30000 to 31000 in udp.... I´m pretty sure you don´t want that, with iptables is enough in most cases. 
> - 最关键的配置，在docker里面启动licode，需要注意修改文件licode_config.js
>> - config.erizoController.publicIP = '192.168.1.113'; //192.168.1.113 为物理主机的ip，不是licode所在的docker容器的ip，因为外部网络(例如打开一个网站, 这个网站是部署在docker容器里)通过物理主机(容器宿主)然后才访问到licode
>> - config.erizoAgent.publicIP = '192.168.1.113'; //192.168.1.113 为物理主机的ip，不是licode所在的docker容器的ip，因为外部网络通过物理主机然后才访问到licode
> - `./initLicode.sh`，运行licode。如果第一次运行报错(出现这种情况的原因尚且未知)，尝试操作`pkill node`，再重试`./initLicode.sh` 
> - `./initBasicEample.sh`，如果启动报错，检查mongo是否启动成功
>> - 每次进入docker容器都得手动启动mongodb，可以使用一些自动化脚本来解决问题 `mongod --dbpath /opt/licode/build/db --logpath /opt/licode/build/mongo.log --fork`
> - 停止, 开启, 进入 `docker stop licode` `docker start licode` `docker exec -it licode /bin/bash ` exit 退出当前容器
> - 访问 https://192.168.1.113:3004 , 不起作用的话, 需要刷新下页面 
- 使用docker hub 部署licode 
> - `docker pull rofl256/licodebasic` rofl256/licodebasic这个镜像可以成功运行; 目前测试lynckia/licode未能成功运行



2016-03-26
==============

知识积累
--------------
- virtualbox 添加硬盘
> - VitrualBox是不允许更改重置硬盘大小的，所以当硬盘不足时，只能添加新硬盘。步骤如下：
>> - 关闭Ubuntu系统，打开VistualBox，"设置"->"存储"->“添加虚拟硬盘”
>> - 启动Ubuntu系统，操作命令如下：
>>> - `sudo fdisk -l` // 查看现有系统磁盘空间, 可以看到新增加的磁盘空间 /dev/sdb ，这里我们需要给新的磁盘空间分区
>>> - `sudo fdisk /dev/sdb`, Command (m for help): m // 键入m，可看到帮助信息
>>> - Command (m for help): n //新建分区
>>> - Command (m for help): p //选择添加主分区
>>> - Command (m for help): 1 //选择主分区编号为1， 这样创建后的主分区为sdb1
>>> - First Cylinder(1-1014,default 1): 1 // 第一个主分区起始的磁盘块数
>>> -  Last cylindet or +siza or +sizeM or +sizeK: +1024MB // 可以是以MB为单位的数字或者以磁盘块数，这里我们输入+1024MB表示分区大小为1G
>>> - 这样我们就创建完一个分区，如果要创建更多分区可以照上面的步骤继续创建
>>> - 最后，键入：w，保存所有并退出，完成新磁盘的分区
>>> - 格式化磁盘分区 `sudo mkfs -t ext3 /dev/sdb1` // 用ext3格式对 /dev/sdb1 进行格式化
>>> - 挂载分区
>>>> - `sudo mkdir /data` // 创建新的挂载点
>>>> - `sudo mount /dev/sdb1 /data` // 将新磁盘分区挂载到 /data 目录下
>>> -  开机自动挂载
>>>> - `vi /etc/fstab` // 修改 /etc/fstab 文件, 在 /etc/fatab 文件中，添加如下内容：/dev/sdb1 /data ext3 defaults 1 2


2016-03-23
==============

知识积累
--------------
- tmux 的使用
> - 一个tmux session 可以包含多个window，一个window包含多个pane，一个pane对应一个终端session
> - split窗口。可以在一个terminal下打开多个终端，也可以对当前屏幕进行各种split，即可以 同时打开多个显示范围更小的终端。
> - 在使用SSH的环境下，避免网络不稳定，导致工作现场的丢失。想象以下场景， 你在执行一条命令的过程中，由于网络不稳定，SSH连接断开了。这个时候，你就不知道之前 的那条命令是否执行成功。如果此时你打开了很多文件，进入了较深层次的目录，由于网络 不稳定，SSH连接断开。重新连接以后，你又不得不重新打开那些文件，进入那个深层次的 目录。如果使用了tmux，重新连接以后，就可以直接回到原来的工作环境，不但提高了工作 效率，还降低了风险，增加了安全性。
> - 安装`apt-get install tmux`
> - 列出当前所有会话`tmux ls`
> - 新建会话`tmux new -s @session`
> - 接入指定会话`tmux a -t @session`
> - 断开会话`tmux detach`  -> Ctrl+b d
> - 关闭服务(所有会话)`tmux kill-server`
> - 关闭会话`tmux kill-session -t @session`
> - 关闭窗口`tmux kill-window -t @name`
> - 关闭会话`tmux kill-pane -t @name`
> - 快捷键使用
>> - 快捷键参考 按下 Ctrl-b 后的快捷键如下：
>>> - 基础
>>>> - ? 获取帮助信息
>>> - 会话管理
>>>> - s 列出所有会话
>>>> - $ 重命名当前的会话
>>>> - d 断开当前的会话
>>> - 窗口管理
>>>> - c 创建一个新窗口
>>>> - , 重命名当前窗口
>>>> - w 列出所有窗口
>>>> - % 水平分割窗口
>>>> - " 竖直分割窗口
>>>> - n 选择下一个窗口
>>>> - p 选择上一个窗口
>>>> - 0~9 选择0~9对应的窗口
>>> - 窗格管理
>>>> - % 创建一个水平窗格
>>>> - " 创建一个竖直窗格
>>>> - 方向键 将光标移入左侧的窗格*
>>>> - 方向键 将光标移入下方的窗格*
>>>> - 方向键l 将光标移入右侧的窗格*
>>>> - 方向键 将光标移入上方的窗格*
>>>> - C+方向键 调整pane尺寸
>>>> - q 显示窗格的编号
>>>> - o 在窗格间切换
>>>> - } 与下一个窗格交换位置
>>>> - { 与上一个窗格交换位置
>>>> - [ 滚屏要进入copy-mode，即前缀+[，然后就可以用上下键来滚动屏幕，配置了vi快捷键模式，就 可以像操作vi一样来滚动屏幕，非常的方便。退出直接按‘q’键即可；复制模式copy-mode
前缀 [ 进入复制模式
按 space 开始复制，移动光标选择复制区域
按 Enter 复制并退出copy-mode。
将光标移动到指定位置，按 PREIFX ] 粘贴
>>>> - ] 粘贴
>>>> - ! 在新窗口中显示当前窗格
>>>> - x 关闭当前窗格> 要使用带“*”的快捷键需要提前配置，配置方法可以参考上文的“在窗格间移动光标”一节。——译者注
>>> - 其他
>>>> - t 在当前窗格显示时间
>>>> - z 如果你用的是tmux >= 1.8，那么可以用 C-b z 来最大化一个pane，想恢复的时候再次按 C-b z 就是了
- docker ubuntu image
> - ubuntu:14.04 daocloud.io/ubuntu:14.04 
> - ubuntu:12.04 daocloud.io/ubuntu:12.04



2016-03-23
==============

知识积累
--------------
- ubuntu14.04 安装docker
> - 升级你的包管理器 `sudo apt-get update`
> - 查看你是否安装了wget `which wget` 如果wget没有安装，先升级包管理器，然后再安装它 `sudo apt-get update $ sudo apt-get install wget`
> - 获取最新版本的 Docker 安装包 `wget -qO- https://get.docker.com/ | sh`
> - 验证 Docker 是否被正确的安装 `sudo docker run hello-world`
- Docker去sudo 在Ubuntu下，在执行Docker时，每次都要输入sudo，同时输入密码，这里把当前用户执行权限添加到相应的docker用户组里面
> - 添加一个新的docker用户组 `sudo groupadd docker`
> -  添加当前用户到docker用户组里，注意这里的king为ubuntu登录用户名 `sudo gpasswd -a king docker`
> - 重启Docker后台监护进程 `sudo service docker restart`
> -  重启之后，尝试一下，是否生效 `docker version`
> - 若还未生效，则系统重启，则生效 `sudo reboot`
- 下载Ubuntu镜像 `docker pull ubuntu:14.04` 这条命令的作用是从Docker仓库中获取ubuntu的镜像
> - 下载完成以后，使用 `docker images`，可以列出所有本地的镜像
> - 启动第一个容器 `docker run -ti ubuntu`
> - 注意：我们在不指定Tag的情况下，默认选择Tag为latest的镜像启动容器。 指定Tag启动命令为：`docker run -ti ubuntu:14.04`; 刚刚的`docker run -ti ubuntu`命令中没有指定执行程序，Docker默认执行/bin/bash
- docker 常用命令
> - `docker images`：列出所有镜像(images)
> - `docker ps`：列出正在运行的(容器)containers
> - `docker pull ubuntu`：下载镜像
> - `docker run -i -t ubuntu /bin/bash`：运行ubuntu镜像
> - `docker commit 3a09b2588478 ubuntu:mynewimage`：提交你的变更，并且把容器保存成Tag为mynewimage的新的ubuntu镜像.(注意，这里提交只是提交到本地仓库，类似git)
- 源码安装node
> - 一、更新你的系统
iteblog# `sudo apt-get update`
iteblog# `sudo apt-get install git-core curl build-essential openssl libssl-dev`
> - 二、安装Node.js
首先我们先从github上将Node.js库克隆到本地：
iteblog# `git clone https://github.com/nodejs/node.git`
iteblog# `cd node`
如果你需要安装特定版本的Node，可以如下操作：
iteblog# `git tag` # 这个命令将会显示Node的所有版本的列表
iteblog# `git checkout v0.10.33`
然后可以编译和安装Node：
iteblog# `./configure`
iteblog# `make`
iteblog# `sudo make install`
安装完毕，我们就可以在命令行里面输入以下命令以便确认Node是否安装完毕:
iteblog# `node -v`
v0.10.33
这个命令会输出你安装Node版本信息，如果你电脑上面输出和下面的类似，那恭喜你了，安装Node成功。
> - 三、安装NPM
这个很简单，NPM官方提供了安装NPM的脚本，所以我们把这个脚本下载下来执行一下就可以：
iteblog# `wget https://npmjs.org/install.sh --no-check-certificate`
iteblog# `chmod 777 install.sh`
iteblog# `./install.sh`
iteblog# `npm -v`
2.7.6
如果你输入`npm -v`，返回的是一个类似上面的版本信息，那么NPM也就安装成功了！


2016-03-20
==============

知识积累
--------------
- visual studio code 无法安装插件
> - 第一次安装/或者重装 visual studio code 无法安装插件，原因是因为无法连接到插件服务器，dns解析失败，可以通过在浏览器访问插件服务网站(vscode extensions market)，之后再尝试安装
- visual studio code 自动换行
> - file -> preferences -> user settings: add: "editor.wrappingColumn": 0


2016-03-19
==============

知识积累
--------------
- asp.net core 1.0
> - Install on CentOS7
> - 与nodejs对比, dnvm <-> nvm, dnx/dnu <-> node/npm, dnvm管理不同版本的dnx, 每个版本的dnx目前有mono和core两种类型
>> - [guide line](https://docs.asp.net/en/latest/getting-started/installing-on-linux.html#installing-on-centos-7)
>> - Install the .NET Version Manager(DNVM)
>>> - install unzip if you don't already have it, `sudo yum install unzip`
>>> - Download and install DNVM, `curl -sSL https://raw.githubusercontent.com/aspnet/Home/dev/dnvminstall.sh | DNX_BRANCH=dev sh && source ~/.dnx/dnvm/dnvm.sh`
>>> - `dnvm list/...`
>> - Install the .NET Execution Environment (DNX) The .NET Execution Environment (DNX) is used to build and run .NET projects. 
>>> - The .NET Execution Environment (DNX) is used to build and run .NET projects. Use DNVM to install DNX for Mono 
>>> - DNX support for .NET Core is not available for CentOS, Fedora and derivative in this release, but will be enabled in a future release.
>>> - To install DNX for Mono:
>>>> - Install Mono via the mono-complete package
>>>>> - `rpm --import "http://keyserver.ubuntu.com/pks/lookup?op=get&search=0x3FA7E0328081BFF6 A14DA29AA6A19B38D3D831EF" `
>>>>> - `yum-config-manager --add-repo http://download.mono-project.com/repo/centos/ ` (有可能提示找不到 yum-config-manager ，这个是因为系统默认没有安装这个命令，这个命 令在 yum-utils 包里，可以通过命令 `yum -y install yum-utils` 安装)
>>>>> - `yum –y install mono-complete.x86_64 `
安装所有的软件包
>>>>> - 运行 mono –V 确认已经成功安装
>>>> - Use DNVM to install DNX for Mono: `dnvm upgrade -r mono`
>>> - Install Libuv. Libuv is a multi-platform asynchronous IO library that is used by Kestrel, a cross-platform HTTP server for hosting ASP.NET 5 web applications.To build libuv you should do the following:
>>>> - `sudo yum install automake libtool wget`
>>>> - `wget http://dist.libuv.org/dist/v1.8.0/libuv-v1.8.0.tar.gz`
>>>> - `tar -zxf libuv-v1.8.0.tar.gz`
>>>> - `cd libuv-v1.8.0`
>>>> - `sudo sh autogen.sh`
>>>> - `sudo ./configure`
>>>> - `sudo make`
>>>> - `sudo make check`
>>>> - `sudo make install`
>>>> - `sudo ln -s /usr/lib64/libdl.so.2 /usr/lib64/libdl`
>>>> - `sudo ln -s /usr/local/lib/libuv.so.1.0.0 /usr/lib64/libuv.so`
>> - Running the asp.net core samples
>>> - `git clone https://github.com/aspnet/Home.git`
>>> - Change directory to the folder of the sample you want to run
>>> - Run `dnu restore` to restore the packages required by that sample
>>> - Run the sample using the appropriate DNX command:
>>>> - For the console app run `dnx run`
>>>> - For the web apps run `dnx kestrel`
>>>> - You should see the output of the console app or a message that says the site is now started
>>>> - You can navigate to the web apps in a browser by navigating to http://localhost:5004
- linux 搭建 asp.net core Web Application 项目
> - `npm install -g yo generator-aspnet gulp bower`
> - run `yo aspnet`, follow the prompts and pick the Web Application
> - go to the WebApplication folder and run dnu restore to install of the necessary NuGet packages to run the application:
>> - `cd WebApplication`
>> - `dnu restore` You can also run the command dnx: Restore Packages within VS Code from the Command Palette


2016-03-18
==============

知识积累
--------------
- git 的获取方式有ssh和http/https
> - 两种方式互斥, ssh方式clone得到的代码需要ssh的方式进行pull等操作, 反之亦然
> - 如果使用https/http方式获取, 则每次的git pull等操作都需要输入用户名密码, 可以使用credi.helper的方式记忆用户名密码, 就不需要每次都输入
> - ssh方式则需要生产并添加key
> - 如果你之前已经一直使用https方式进行开发，当前想要切换成为ssh方式进行开发，只需要执行如下几步的操作即可：
`git remote rm origin git remote add origin "Git仓库的ssh格式地址" git push origin`
> - 存在多个ssh key时的共存处理
> - 存在多个key会导致程序无法连接到目标主机, 例如在使用过程当中visual studio code的git插件无法pull, 显示权限问题permission
>> - 修改配置文件在 ~/.ssh 目录下新建一个config文件 touch config 添加内容：
Host gitlab.com
    HostName gitlab.com
    PreferredAuthentications publickey
    IdentityFile ~/.ssh/id_rsa
Host github.com
    HostName github.com
    PreferredAuthentications publickey
    IdentityFile ~/.ssh/id_rsa_github`
- visual studio code 使用 git 无法 pull 的问题
> - 重新clone, 默认是master, 在checkout其他分支前, 先pull或fetch master, 再在bash下面pull或fetch所有的分支


2016-03-12
==============

知识积累
--------------

- nodejs 版本控制nvm, 包服务管理nrm, 前端包管理bower, 后端包管理npm
> - 安装nvm [教程](https://github.com/creationix/nvm), 进入用户文件夹 /home/kmaidol , 执行命令 `curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.0/install.sh | bash`
>> - 激活 nvm, 进入用户文件夹 /home/kmaidol, 执行` . ~/.nvm/nvm.sh`
>> - 用户登录时自动激活nvm, 需要编辑文件 ~/.bashrc, ~/.profile, or ~/.zshrc, 添加如下内容 (这是针对手动安装方式。curl 这种使用脚本的安装方式会自动添加这些内容)
>>> - export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" # This loads nvm
>> - 命令 `nvm ls/use/install/...`
>> - 登陆默认启动版本`nvm alias default 0.10.x`
>> - 列出nodejs版本 `nvm ls-remote`, 安装nodejs `nvm install v5.8`
> - 安装nrm, `npm install -g nrm`
>> - 命令 `nrm ls/use/...`
> - 安装bower, `npm install -g bower`
>> - 命令 `bower init/install/...`
>>> - 建议在项目目录下添加文件'.bowerrc', 里面添加内容'{
   "directory": "public/lib"
}', 自定义包的下载目录
- licode 运行环境搭建 [教程](http://lynckia.com/licode/install.html).以下所有操作保证在 ubuntu12.4-desktop/server (非docker镜像)下执行, 包括git clone.
> - 安装之前先确定licode需要的node版本, licode的安装与编译对于太高或太低版本有兼容问题, 最后确定安装v0.10.37版本, 并设置合适的npm镜像源, 以下操作在此node版本下操作, 建议使用nvm管理node版本(ps:问题貌似是出在installErizo.sh, 这里gyp的编译有可能报错, 需要用到v0.10.37；这里安装编译成功后, 可以切换到更高版本的nodejs运行程序。留意安装过程的报错, 遇到安装报错不要慌, 一般都是依赖版本问题或者缺少依赖, 冷静逐个击破)
> - `sudo apt-get install git` `git clone https://github.com/ging/licode.git`
> - 以下建议使用`sudo`
>> - `./licode/scripts/installUbuntuDeps.sh`
>> - `./licode/scripts/installErizo.sh` 
>> - `./licode/scripts/installNuve.sh`
>> - `./licode/scripts/installBasicExample.sh`
>> - `./licode/scripts/initLicode.sh`
>> - `./licode/scripts/initBasicExample.sh`
> - Now you can connect to "localhost:3001" and test your basic videoconference example!
> - 查看进程 `sudo netstat -anp | grep node`
> - 关闭所有进程 `sudo pkill node`
> - chrome浏览器在版本47之后对webrtc的安全性进行了调整, webrtc的接口须在https的来源中使用。在本机上访问可以用http或者https, 其他机子必须用https
> - 测试网站(licode/extras/basic_example/basicServer.js)开启了两个端口3001(http)和3004(https), 本机可以通过3001或者3004访问, 其他机子通过3004访问
> - 为设置支持https, 在执行`./licode/scripts/initLicode.sh`前, 还需要先编辑文件 licode/licode_config.js , `config.erizoController.ssl=true, config.erizoController.lissten_ssl=true`
- ubuntu 挂载光盘
> - Ubuntu 用指令掛載 CDROM 已經不用像以前那樣，在 mount 的時候，要給一堆的參數才能掛載，現在，只要先用下面的這一行指令來找出 CDROM 的代碼。
`ls /dev | grep cdrom`
> - 然後，再直接用那個代碼來掛載就可以了，例如阿舍用上面的指令找到的 CDROM 代碼是 cdrom1，那就可以用下面的這一行指令來把它掛載到 /media/cdrom (没有则手动创建) 資料夾用哩
`sudo mount /dev/cdrom1 /media/cdrom`

