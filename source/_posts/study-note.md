---
title: 学习笔记
date: 2016-06-27 20:31:36
categories: 笔记
tags:
  - 笔记
  - 权限设计
  - docker
  - tmux
  - licode
---

2016 年上半年的日常学习笔记，按日期倒序排列，内容包括权限系统设计、shadowsocks、SSH 原理、Promise、tmux、Docker、licode、Git 等。

<!-- more -->

## 2016-07-14

### 用户管理模块的理解 v2.0

这一版和之前的理解（见下一节）有所不同：

- 整棵组织结构树反映了所有的岗位和人员组成。
- 抛弃数据权限标识，改用组织结构节点来标识数据。
- 每个组织结构节点对应一个具体的岗位。例如研发部门（经理岗位）下面有多个开发岗位：开发人员 1、开发人员 2、开发人员 3……
  - 每个岗位就是一个 account，可能暂时有人员空缺。
  - 正常情况下一个岗位对应一个员工，也可能多个人同在一个岗位（同岗），共用相同的资源。
  - 开发人员 1、2、3 是平行关系，工作内容也相同，但属于不同的岗位，都是组织结构的组成部分。
  - 岗位是最小单位，员工被分配到岗位上。完整的组织结构就反映了所有岗位。
- 对应到现实：岗位是预先定好的，用人单位根据用人情况招聘，员工入职后被分配到具体岗位（节点），比如经理或开发人员 1、2、3。
- 员工对数据的增删改查（CRUD）跟随所在岗位：
  - 一个员工可能身兼多个岗位，不同岗位登录系统后看到的数据应该不同。
  - 身兼多职时，应该在登录前或登录后选择岗位，选择不同的岗位，对数据的操作也不同。
  - 例如新增一条数据时，这条数据要和当前选择的岗位关联。
  - 如果不对岗位进行隔离，身兼多岗的员工对数据的操作会很混乱。

### 用户管理模块的理解（v1）

整体模型：**用户 → 组织结构 → 角色 → 功能权限 → 接口权限**，一般情况下已经足够。

#### 用户管理

创建用户时，分配默认数据权限（可以随机生成一个标识）、默认角色和默认用户组。

#### 角色管理

- 考虑公司组织结构的场景时，可以把角色和组织结构关联（多对多关系）。用户不直接关联角色，而是关联组织结构。
  - 这样用户模块更好用：创建新用户时只需要关注组织结构，分配组织结构就够了。
  - 角色则在创建组织结构节点时分配给节点。
- 如果还有其他与组织结构同级的维度，也可以把该维度与角色关联。这时会有两个维度与角色关联，出现第三个、第四个维度时也照此处理。

#### 用户组管理（公司组织结构）

- 可以是树形结构，有层级。单纯的节点就是组（不带职位等业务），组与用户是一对多关系。
- 也可以是离散结构，点与点之间可以没有关系，也可以有级别关系。
- 组织结构只用来表达一种关系，与角色权限的控制无关。但它应该与数据的显示有关，例如可以通过配置或代码定义规则来限制数据的显示，比如当前节点可以查看上下级节点的数据。

#### 接口权限管理

- 接口权限必须由开发人员维护。
- 用一张关联表把接口和界面视图功能关联起来，是多对一关系。
- 查找用户的接口权限：先查出用户拥有的角色，再查这些角色对应的所有功能权限，最后查这些功能权限对应的所有接口权限。用户访问后台接口时，就用这些接口权限进行验证。

#### 功能权限管理（界面视图）

- 界面视图功能可以由用户直接维护。
- 一个界面功能（例如某个 button 对应的编辑操作）可能对应多个后台接口，即视图功能与后台接口是一对多关系，这个关系需要维护好。给角色分配一个视图功能时，要相应地给角色加上对应的几个接口权限。
- 功能权限可以控制界面的显示：有某个功能权限才显示对应的 button。
- 功能权限可以分级：单功能、模块、视图。单功能是最小单位，多个单功能组成模块，多个模块组成视图。模块和视图可以简化分配功能时的操作。
- 功能权限与角色关联。
- 用户登录后，查询出用户拥有的功能权限（先查角色，再查角色对应的所有功能权限），用这些功能权限控制界面视图的显示。
- 功能权限和接口权限是独立解耦的。某个功能权限依赖某个接口权限时，拥有这个接口权限的用户不一定能看到这个功能对应的界面视图。

#### 数据权限管理

- 主要字段：`dataType`、`dataId`、`dataRightId`、`RWtype`。
- 创建用户时，默认分配一个数据权限 ID（`dataRightId`），作为用户的数据标识。
- 用户新建一条业务数据时，拥有这条数据的写权限（`RWtype = write`），并且可以给其他用户的 `dataRightId` 指定这条数据的读写权限。
- 可以根据不同系统的业务需求定制数据权限规则，**以新增功能接口的方式扩展，而不改动原有的业务逻辑**。例如：
  - admin 角色可以突破数据权限限制，读写所有业务数据。
  - 组织结构的上级可以读写所有下级的数据。
- 用户的业务数据应该分成几个列表：
  - 自己可编辑的数据（包括别人分配来的）；
  - 自己只读的数据（包括别人分配来的，以及系统规则决定的，例如默认可以看到上下级的数据）；
  - 代理别人的数据（包括可读和可写）。
- 上级可以强制获取下级业务数据的读写权限，并再分配给下级用户；admin 可以强制获取所有用户业务数据的读写权限，并分配给任何用户。这些都应该作为独立于原有业务的新功能接口来实现。

## 2016-07-03

### 源码安装 shadowsocks

```bash
sudo apt-get update
sudo apt-get install -y python python-setuptools
git clone https://github.com/shadowsocks/shadowsocks.git
cd shadowsocks
sudo python setup.py install
ssserver -h
```

开启一次性验证：运行 `ssserver` 时加参数 `-a`，或者在 `ss.json` 中加上 `"one_time_auth": true`。

### Linux 部署环境的资源占用

redis + nginx + mysql + mongod + vnstat + vnstatsvg + pm2 + 2 个 Node 后台程序 + 邮件服务，内存一共只占用了 284M。

## 2016-07-01

### 协议

- **socket 不是协议**，而是一个软件抽象层，是对 TCP/IP 的封装，有各种语言的接口实现（C、C++、Python、C# 等）。
- HTTP、FTP、WebSocket、SOCKS 都是协议，并且建立在 TCP/IP 之上。通信前都要先通过握手建立 TCP 连接，然后才能发送数据。不同的协议根据自身的使用场景，采用不同的连接方式（短连接、长连接、实时连接）：
  - **HTTP**：建立 TCP 连接后发送请求，收到响应后断开（HTTP/1.1 默认开启 keep-alive，可以复用连接）。
  - **WebSocket**：通过一次 HTTP 握手升级协议，之后保持与远端的长连接，双向收发数据。
  - **SOCKS**：保持与远端的连接，收发并转发数据。

### shadowsocks Android 客户端无法连接

在网络切换后（Wi-Fi 切换到移动网络、移动网络切换到 Wi-Fi、从 A Wi-Fi 切换到 B Wi-Fi）可能出现无法连接的情况，可以依次尝试：

1. 关闭 shadowsocks 客户端连接，再重新打开。
2. 先断开连接，点击"重置"（重置所有后台服务），再连接，检测网络是否正常。
3. 把系统语言从英文切换到中文（或反过来），然后重启手机。

### 部署 shadowsocks

安装与启动：

```bash
sudo apt-get install python-pip
sudo pip install shadowsocks

# -d 表示以守护进程方式运行
ssserver --manager-address 127.0.0.1:6001 -c ss.json -d start
# 停止
ssserver -d stop
```

`--manager-address` 设置 shadowsocks 的管理 IP 和端口，其他程序通过这个端口调用 shadowsocks 的管理 API，见 [Manage Multiple Users](https://github.com/shadowsocks/shadowsocks/wiki/Manage-Multiple-Users)。

`ss.json` 示例：

```json
{
  "server": "your_server_ip",
  "port_password": {
    "10080": "yourpassword"
  },
  "timeout": 300,
  "method": "aes-256-cfb"
}
```

> `server` 要填写实际 IP，不要填写域名。因为本机为了让 manager 访问管理 API，需要在 `/etc/hosts` 中添加 `127.0.0.1 v1.example.com`（或 `<局域网地址> v1.example.com`）。如果 `server` 填域名 `v1.example.com`，它会被解析成本地地址，导致外部访问不到 shadowsocks 服务。

一次性验证（OTA）：每次发送数据到代理服务器时，都在数据包中附加一些验证数据。

### 部署 shadowsocks-manager

项目地址：[shadowsocks-manager](https://github.com/shadowsocks/shadowsocks-manager)，依赖 Node.js 4.4 和 MongoDB 3.2。

为了安全，manager 应该和 shadowsocks 部署在同一个局域网内：

| `--manager-address` 设置为 | 部署方式 | `/etc/hosts` 需要添加 |
| --- | --- | --- |
| `127.0.0.1` | 两者部署在同一台服务器 | `127.0.0.1 v1.example.com` |
| 局域网地址 | 两者部署在同一局域网 | `<局域网地址> v1.example.com` |
| 外网域名或 IP | 不推荐：管理 API 会暴露给局域网外的机器，不安全 | — |

```bash
git clone https://github.com/shadowsocks/shadowsocks-manager.git
cd shadowsocks-manager
npm install -g bower
npm install
bower install
mv config.js.sample config.js
node server
```

在 manager 中创建服务器时，端口要和上面的 `127.0.0.1:6001` 一致。

## 2016-05-29

### 微服务架构

对外通过 REST API 通信，微服务之间通过异步消息队列通信。

## 2016-05-26

### SSH 原理

SSH 采用"非对称密钥系统"，也就是常说的公钥/私钥加密系统。它的安全验证分为两种级别。

#### 1. 基于口令的安全验证

用用户名和密码登录，我们平时一般用的就是这种方式。大致过程如下：

1. 客户端发起连接请求。
2. 远程主机收到登录请求，把自己的公钥发给客户端。
3. 客户端用远程主机的公钥加密登录密码，发送给远程主机。
4. 远程主机用自己的私钥解密，得到登录密码，密码正确就允许登录。

**中间人攻击**：如果网络中有一台冒牌服务器 B 冒充远程主机，拦截了客户端的连接请求，并把自己的公钥发给客户端，客户端就会把用 B 的公钥加密的密码发过去，B 用自己的私钥就能拿到密码，然后为所欲为。

所以第一次连接远程主机时，在第 3 步之前会提示当前远程主机的"公钥指纹"，让你确认远程主机是否可信。选择继续后才能输入密码登录。确认之后，这台服务器的公钥会保存到 `~/.ssh/known_hosts` 文件中，以后连接时会自动校验。

> 严格来说，SSH 实际是先通过密钥交换（如 Diffie-Hellman）协商出一个对称会话密钥，之后的所有通信（包括密码）都用这个会话密钥加密。上面的描述是简化后的理解。

#### 2. 基于密钥的安全验证

需要在当前用户的家目录下为自己创建一对密钥，并把公钥放到要登录的服务器上。连接服务器时：

1. 客户端请求用密钥进行安全验证。
2. 服务器在你要登录的用户的家目录下找到你的公钥，用它加密一个"质询"（challenge）发给客户端。
3. 客户端用自己的私钥解密质询，再发回服务器。
4. 服务器验证通过，允许登录。

和第一种方式相比，这种方式不需要在网络上传送口令。

> 上面"用公钥加密质询"是 SSH-1 的做法。SSH-2 中实际是客户端用私钥对本次会话的数据进行**签名**，服务器用 `authorized_keys` 里的公钥**验证签名**。

简单来说，把客户端的公钥放到服务器上，客户端就可以免密码登录服务器了。公钥默认放在要登录的用户家目录下的 `~/.ssh/authorized_keys` 文件中。具体操作见 [VPS 部署笔记：SSH 免密码登录](/2016/07/06/vps_deploy/#15-SSH-免密码登录)。

## 2016-05-02

### nginx

待补充。

## 2016-04-24

### ES6 harmony-reflect

用 [harmony-reflect](https://github.com/tvcutsem/harmony-reflect)（为当时的 JS 引擎提供 ES6 `Proxy` / `Reflect` API 的 shim）实现 AOP。

## 2016-04-14

### Promise 的理解

参考：[http://www.cnblogs.com/fsjohnhuang/p/4135149.html](http://www.cnblogs.com/fsjohnhuang/p/4135149.html)

下面是帮助理解 Promise 内部结构的**伪代码**，不能直接运行：

```js
function Promise(fn) {
  this.status = 'pending';
  this._resolve = [];   // 成功回调队列
  this._reject = [];    // 失败回调队列

  this.resolve = function (value) {
    this.status = 'resolved';
    this._resolve.forEach(cb => cb(value));
  };
  this.reject = function (err) {
    this.status = 'rejected';
    this._reject.forEach(cb => cb(err));
  };
  this.then = function (onResolve, onReject) {
    this._resolve.push(onResolve);
    this._reject.push(onReject);
    return /* 一个新的 promise，用于链式调用 */;
  };
  this.catch = function (onReject) {
    return this.then(null, onReject);
  };

  fn(this.resolve, this.reject);
}

Promise.resolve = function (value) {
  return new Promise(function (resolve) { resolve(value); });
};
Promise.reject = function (reason) {
  return new Promise(function (resolve, reject) { reject(reason); });
};
```

`fn` 是一个异步任务：任务成功时调用 `resolve`，失败时调用 `reject`。例如用原生 Promise 加载图片：

```js
function getImg(url) {
  return new Promise(function (resolve, reject) {
    var img = new Image();
    img.onload = function () {
      resolve(this);
    };
    img.onerror = function (err) {
      reject(err);
    };
    img.src = url;
  });
}

getImg('/logo.png').then(function (img) {
  document.body.appendChild(img);
});
```

> 原笔记的示例中写的是 `img.url = url`，这不会触发图片加载，应该是 `img.src = url`。另外 `Promise(...)` 必须用 `new` 调用。

**状态转换**：`resolve` 的参数不是 thenable 对象或 Promise 对象时，直接修改当前 promise 的状态，并保存传给状态处理函数的实参。如果参数是 thenable 对象或 Promise 对象，则把控制权交给该对象，由它来设置当前 promise 的状态和实参。之后控制权移交给 `finale` 方法，`finale` 会遍历 `deferreds` 数组，根据状态调用对应的处理函数，并修改 promise 链中下一个 promise 的状态。

## 2016-03-27

### Tmux Resurrect & Continuum：持久保存 tmux 会话

参考：[工具教程](https://linuxtoy.org/archives/tmux-resurrect-and-continuum.html)。这两个插件要求 tmux 1.9 及以上版本。

**Tmux Resurrect** 可以备份 tmux 会话的各种细节：所有会话、窗口、窗格及其顺序，每个窗格的当前工作目录，精确的窗格布局，活动及替代的会话和窗口，窗口焦点，活动窗格，窗格中运行的程序等等。

```bash
mkdir ~/.tmux
cd ~/.tmux
git clone https://github.com/tmux-plugins/tmux-resurrect.git
```

官方推荐通过 [tpm](https://github.com/tmux-plugins/tpm) 插件管理器安装，需要安装多个插件时可以试试。然后在 `~/.tmux.conf` 中添加：

```bash
run-shell ~/.tmux/tmux-resurrect/resurrect.tmux
```

重载配置：`tmux source-file ~/.tmux.conf`。

- 保存会话：`前缀键 + Ctrl-s`。状态栏会显示 "Saving ..."，完成后提示环境已保存。
- 还原会话：`前缀键 + Ctrl-r`。

**Tmux Continuum** 更进一步，把保存和还原自动化：定时备份，并在 tmux 启动时自动还原。

```bash
cd ~/.tmux
git clone https://github.com/tmux-plugins/tmux-continuum.git
```

在 `~/.tmux.conf` 中添加：

```bash
# 默认每 15 分钟备份一次，可以改为 60 分钟（选项写在 run-shell 之前）
set -g @continuum-save-interval '60'
run-shell ~/.tmux/tmux-continuum/continuum.tmux
```

然后执行 `tmux source-file ~/.tmux.conf` 重载配置。

### Ubuntu 源码安装 tmux 2.0

- tmux 依赖 libevent 2.x，需要先[下载源码安装](http://libevent.org)。
- 先执行 `sudo apt-get install libncurses-dev`，避免报错 `curses not found`。
- 安装完成后重新登录终端，避免报错 `cannot open shared object file: No such file or directory`（也可以执行 `sudo ldconfig`）。

### MongoDB 报错：Insufficient free space for journal files

安装 licode 时，MongoDB 启动报错：

```text
ERROR: Insufficient free space for journal files
Please make at least 3379MB available in /var/lib/mongodb/journal or use --smallfiles
```

journal 文件至少需要 3GB 左右的磁盘空间。空间不够时，可以加上 `--smallfiles` 参数启动：

```bash
/usr/local/mongodb/bin/mongod --smallfiles \
  --dbpath=/usr/local/mongodb/data \
  --logpath=/usr/local/mongodb/logs/mongodb.log \
  --port=12789 --logappend &
```

检查是否启动成功：

```bash
ps -ef | grep mongod
netstat -an | grep 12789
```

### ulimit

`ulimit -a` 查看当前 shell 的资源限制，例如最大打开文件数、最大进程数等。

### Docker 安装 licode（git clone 最新版本）

Dockerfile 使用的基础镜像是 Ubuntu 14.04，安装时要保证网络通畅（尽量使用代理）。

用 Dockerfile 构建镜像：

```bash
docker build -t licode-image .
```

如果构建失败（网络或其他原因），就进入容器手动重新安装，确保每一步都成功：

| 脚本 | 说明 |
| --- | --- |
| `./installUbuntuUnattend.sh` | 安装所有依赖。必须确保没有 error，warning 可以忽略 |
| `./installErizo.sh` | 这一步会下载安装 Node 0.10.37，下载安装失败会导致后面编译失败 |
| `./installNuve.sh` | 安装过程会启动 MongoDB，必须确保启动成功。可能因为磁盘空间不足而启动失败，这时需要手动启动，或修改对应的启动脚本。这一步会生成 `licode_config.js` |

> 原笔记中第二个脚本写作 `installZerio.sh`，licode 的脚本目录中并没有这个文件（见下文 2016-03-12 列出的脚本），应为 `installErizo.sh`。

启动容器：

```bash
docker run -it --name licode \
  -p 3001:3001 -p 3004:3004 -p 8080:8080 -p 3000:3000 \
  -p 30000-31000:30000-31000/udp \
  licode-image-work /bin/bash
```

如果启动失败，可能是 iptables 对 UDP 有限制，可以把 UDP 范围调小，例如 `-p 30000-30100:30000-30100/udp`。

**改进**：用 `-it` 前台启动时，退出容器控制台后当前 session 中运行的程序也会退出。更好的做法是用 `-di` 后台启动，把 `/bin/bash` 放到 `init.sh` 脚本的末尾：

```bash
docker run -di --name licode \
  -p 3001:3001 -p 3004:3004 -p 8080:8080 -p 3000:3000 \
  -p 30000-31000:30000-31000/udp \
  licode-image-work ./init.sh

# 然后进入容器控制台操作
docker exec -it licode /bin/bash
```

也有一种建议是禁用 userland-proxy。否则 Docker 会为 30000~31000 的每个 UDP 端口都启动一个代理进程，大多数情况下只用 iptables 就够了。在 `/etc/default/docker` 中添加：

```bash
DOCKER_OPTS="--userland-proxy=false"
```

然后执行 `sudo service docker restart`。

**最关键的配置**：在 Docker 中运行 licode，需要修改 `licode_config.js`：

```js
// 192.168.1.100 是物理主机（容器宿主）的 IP，而不是 licode 所在容器的 IP，
// 因为外部网络要先经过物理主机才能访问到容器里的 licode
config.erizoController.publicIP = '192.168.1.100';
config.erizoAgent.publicIP = '192.168.1.100';
```

启动：

- 执行 `./initLicode.sh` 启动 licode。第一次运行报错时（原因未知），先 `pkill node` 再重试。
- 执行 `./initBasicExample.sh` 启动示例。报错的话先检查 MongoDB 是否启动成功。
- 每次进入容器都要手动启动 MongoDB，可以写进自动化脚本：

  ```bash
  mongod --dbpath /opt/licode/build/db --logpath /opt/licode/build/mongo.log --fork
  ```

容器管理：

```bash
docker stop licode
docker start licode
docker exec -it licode /bin/bash   # exit 退出
```

访问 `https://192.168.1.100:3004`，没有反应的话刷新一下页面。

### 使用 Docker Hub 镜像部署 licode

```bash
docker pull rofl256/licodebasic
```

`rofl256/licodebasic` 镜像可以成功运行，`lynckia/licode` 镜像测试时没能成功运行。

## 2016-03-26

### VirtualBox 添加硬盘

当时的做法是：VirtualBox 图形界面不能直接调整已有虚拟硬盘的大小，硬盘空间不足时就添加一块新硬盘。

> VirtualBox 4.0 起可以用 `VBoxManage modifyhd <disk.vdi> --resize <MB>` 扩容动态分配的 VDI/VHD 硬盘，扩容后还需要在系统内调整分区。

**第 1 步**：关闭 Ubuntu，打开 VirtualBox，依次选择"设置" → "存储" → "添加虚拟硬盘"。

**第 2 步**：启动 Ubuntu，给新硬盘分区。

```bash
# 查看磁盘，可以看到新增的 /dev/sdb
sudo fdisk -l
# 对新磁盘分区
sudo fdisk /dev/sdb
```

在 fdisk 交互界面依次输入：

| 输入 | 作用 |
| --- | --- |
| `m` | 查看帮助 |
| `n` | 新建分区 |
| `p` | 选择主分区 |
| `1` | 分区编号为 1，创建后的分区为 `/dev/sdb1` |
| 回车 | 起始扇区使用默认值 |
| `+1G` | 分区大小，这里表示 1GB。也可以用 `+1024M` 或扇区数 |
| `w` | 保存并退出 |

要创建更多分区，重复上面的步骤即可。

**第 3 步**：格式化并挂载。

```bash
# 用 ext3 格式化 /dev/sdb1
sudo mkfs -t ext3 /dev/sdb1
# 创建挂载点并挂载
sudo mkdir /data
sudo mount /dev/sdb1 /data
```

**第 4 步**：开机自动挂载。编辑 `/etc/fstab`，添加一行：

```text
/dev/sdb1  /data  ext3  defaults  0  2
```

> 第 5 列是 dump 备份标志，一般为 0；第 6 列是开机检查顺序，根分区为 1，其他分区为 2。

## 2016-03-23

### tmux 的使用

- 一个 tmux 会话（session）可以包含多个窗口（window），一个窗口可以包含多个窗格（pane），每个窗格对应一个终端。
- 可以在一个终端里打开多个窗口，也可以把当前屏幕分割成多个显示范围更小的终端。
- 在 SSH 环境下，可以避免网络不稳定导致工作现场丢失。想象一下：执行一条命令时 SSH 断开了，你不知道命令有没有执行成功；打开了很多文件、进入了很深的目录，断线重连后又得全部重来。用了 tmux，重新连接后就能直接回到原来的工作环境，不但提高了效率，还降低了风险。

常用命令：

| 用途 | 命令 |
| --- | --- |
| 安装 | `sudo apt-get install tmux` |
| 列出所有会话 | `tmux ls` |
| 新建会话 | `tmux new -s <session>` |
| 接入指定会话 | `tmux a -t <session>` |
| 断开会话 | `tmux detach`，或快捷键 `Ctrl+b d` |
| 关闭服务（所有会话） | `tmux kill-server` |
| 关闭会话 | `tmux kill-session -t <session>` |
| 关闭窗口 | `tmux kill-window -t <window>` |
| 关闭窗格 | `tmux kill-pane -t <pane>` |

快捷键（先按前缀键 `Ctrl+b`，再按下表中的键）：

| 分类 | 按键 | 作用 |
| --- | --- | --- |
| 基础 | `?` | 获取帮助 |
| 会话 | `s` | 列出所有会话 |
| 会话 | `$` | 重命名当前会话 |
| 会话 | `d` | 断开当前会话 |
| 窗口 | `c` | 新建窗口 |
| 窗口 | `,` | 重命名当前窗口 |
| 窗口 | `w` | 列出所有窗口 |
| 窗口 | `n` / `p` | 切换到下一个 / 上一个窗口 |
| 窗口 | `0`~`9` | 切换到对应编号的窗口 |
| 窗格 | `%` | 左右分割出新窗格 |
| 窗格 | `"` | 上下分割出新窗格 |
| 窗格 | 方向键 | 把光标移到对应方向的窗格 |
| 窗格 | `Ctrl+方向键` | 调整窗格尺寸 |
| 窗格 | `q` | 显示窗格编号 |
| 窗格 | `o` | 在窗格间切换 |
| 窗格 | `}` / `{` | 与下一个 / 上一个窗格交换位置 |
| 窗格 | `!` | 把当前窗格拆成一个新窗口 |
| 窗格 | `x` | 关闭当前窗格 |
| 窗格 | `z` | 最大化 / 还原当前窗格（tmux 1.8 及以上） |
| 复制 | `[` | 进入复制模式，可以用方向键滚屏，按 `q` 退出 |
| 复制 | `]` | 粘贴 |
| 其他 | `t` | 在当前窗格显示时钟 |

复制模式的用法：

1. 按 `前缀键 [` 进入复制模式（配置了 vi 模式的话可以像 vi 一样移动）。
2. 按空格开始选择，移动光标选择复制区域。
3. 按回车复制并退出复制模式。
4. 把光标移到目标位置，按 `前缀键 ]` 粘贴。

### Docker Ubuntu 镜像

| 官方镜像 | DaoCloud 镜像 |
| --- | --- |
| `ubuntu:14.04` | `daocloud.io/ubuntu:14.04` |
| `ubuntu:12.04` | `daocloud.io/ubuntu:12.04` |

### Ubuntu 14.04 安装 Docker

```bash
sudo apt-get update
# 确认已经安装 wget，没有的话先安装
which wget || sudo apt-get install wget
# 获取最新版本的 Docker 安装包并安装
wget -qO- https://get.docker.com/ | sh
# 验证 Docker 是否安装正确
sudo docker run hello-world
```

### Docker 免 sudo

在 Ubuntu 上执行 Docker 命令每次都要输入 sudo 和密码，可以把当前用户加入 `docker` 用户组：

```bash
sudo groupadd docker
sudo gpasswd -a $USER docker
sudo service docker restart
```

重新登录后执行 `docker version` 检查是否生效，不生效就重启系统（`sudo reboot`）。

### 下载 Ubuntu 镜像并启动容器

```bash
# 从 Docker 仓库获取 ubuntu 镜像
docker pull ubuntu:14.04
# 列出本地所有镜像
docker images
# 启动第一个容器
docker run -ti ubuntu
```

注意：不指定 tag 时，默认使用 tag 为 `latest` 的镜像。指定 tag 启动：`docker run -ti ubuntu:14.04`。`docker run -ti ubuntu` 没有指定要执行的程序，Docker 默认执行 `/bin/bash`。

### Docker 常用命令

| 命令 | 说明 |
| --- | --- |
| `docker images` | 列出所有镜像 |
| `docker ps` | 列出正在运行的容器 |
| `docker pull ubuntu` | 下载镜像 |
| `docker run -i -t ubuntu /bin/bash` | 运行 ubuntu 镜像 |
| `docker commit 3a09b2588478 ubuntu:mynewimage` | 把容器保存为 tag 为 `mynewimage` 的新镜像（只提交到本地，类似 git） |

### 源码安装 Node.js

**一、更新系统并安装编译依赖**

```bash
sudo apt-get update
sudo apt-get install git-core curl build-essential openssl libssl-dev
```

**二、编译安装 Node.js**

```bash
git clone https://github.com/nodejs/node.git
cd node

# 查看所有版本，并切换到需要的版本
git tag
git checkout v0.10.33

./configure
make
sudo make install

# 确认安装成功，会输出版本号，例如 v0.10.33
node -v
```

**三、npm**

Node.js 0.6.3 起已经自带 npm，上面装好 Node 后执行 `npm -v` 能看到版本号即可，不需要单独安装。

> 原笔记中用 `wget https://npmjs.org/install.sh --no-check-certificate` 下载脚本，再 `chmod 777` 后执行。这种方式既跳过了证书校验，又给了过大的权限，不推荐。

## 2016-03-20

### Visual Studio Code 无法安装插件

第一次安装或重装 VS Code 后无法安装插件，原因是连不上插件服务器（DNS 解析失败）。可以先在浏览器中访问一次插件市场（VS Code Marketplace），再回来安装。

### Visual Studio Code 自动换行

打开 File → Preferences → User Settings，添加：

```json
{
  "editor.wordWrap": "on"
}
```

> 2016 年的旧版本使用 `"editor.wrappingColumn": 0`，该设置在 VS Code 1.10 起被 `editor.wordWrap` 取代。

## 2016-03-19

### 在 CentOS 7 上安装 ASP.NET Core 1.0（RC 版）

> **时效说明**：DNVM / DNX / DNU 是 ASP.NET Core RC1 时期的工具，已经被 [.NET CLI](https://dotnet.microsoft.com/)（`dotnet` 命令）取代，以下内容仅作历史记录。

与 Node.js 生态类比：

| .NET | Node.js | 说明 |
| --- | --- | --- |
| dnvm | nvm | 版本管理器，管理不同版本的 dnx |
| dnx | node | 运行时，每个版本有 mono 和 core 两种类型 |
| dnu | npm | 包管理 |

参考：[Installing on CentOS 7](https://docs.asp.net/en/latest/getting-started/installing-on-linux.html#installing-on-centos-7)

**1. 安装 .NET Version Manager（DNVM）**

```bash
sudo yum install unzip
curl -sSL https://raw.githubusercontent.com/aspnet/Home/dev/dnvminstall.sh | DNX_BRANCH=dev sh && source ~/.dnx/dnvm/dnvm.sh
dnvm list
```

**2. 安装 .NET Execution Environment（DNX）**

DNX 用于构建和运行 .NET 项目。当时 CentOS、Fedora 及其衍生版还不支持 .NET Core 版本的 DNX，只能安装 Mono 版本。

先安装 Mono：

```bash
rpm --import "http://keyserver.ubuntu.com/pks/lookup?op=get&search=0x3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF"
# 找不到 yum-config-manager 时，先执行 yum -y install yum-utils
yum-config-manager --add-repo http://download.mono-project.com/repo/centos/
yum -y install mono-complete.x86_64
# 确认安装成功
mono -V
```

再用 DNVM 安装 Mono 版本的 DNX：

```bash
dnvm upgrade -r mono
```

**3. 安装 libuv**

libuv 是一个跨平台的异步 IO 库，Kestrel（跨平台的 ASP.NET HTTP 服务器）依赖它：

```bash
sudo yum install automake libtool wget
wget http://dist.libuv.org/dist/v1.8.0/libuv-v1.8.0.tar.gz
tar -zxf libuv-v1.8.0.tar.gz
cd libuv-v1.8.0
sudo sh autogen.sh
sudo ./configure
sudo make
sudo make check
sudo make install
sudo ln -s /usr/lib64/libdl.so.2 /usr/lib64/libdl
sudo ln -s /usr/local/lib/libuv.so.1.0.0 /usr/lib64/libuv.so
```

**4. 运行示例**

```bash
git clone https://github.com/aspnet/Home.git
cd Home/<示例目录>
dnu restore      # 还原示例所需的包
dnx run          # 控制台应用
dnx kestrel      # Web 应用
```

控制台应用会直接输出结果，Web 应用启动后在浏览器访问 `http://localhost:5004`。

### Linux 下创建 ASP.NET Core Web 项目

```bash
npm install -g yo generator-aspnet gulp bower
yo aspnet            # 按提示选择 Web Application
cd WebApplication
dnu restore          # 安装运行所需的 NuGet 包
```

在 VS Code 中也可以通过命令面板执行 `dnx: Restore Packages`。

## 2016-03-18

### Git 的 SSH 与 HTTPS 方式

- 获取代码有 SSH 和 HTTP(S) 两种方式，远程地址的协议决定了之后 pull/push 使用哪种方式。
- 使用 HTTPS 方式时，每次 `git pull` 等操作都要输入用户名和密码。可以用 `credential.helper` 记住凭据，就不用每次都输入了：

  ```bash
  git config --global credential.helper store
  ```

  `store` 会把凭据**明文**保存在 `~/.git-credentials` 中。更安全的做法是用 `cache`（只保存在内存中一段时间），或使用系统的凭据管理器。

- 使用 SSH 方式需要先生成并添加 SSH key。

从 HTTPS 切换到 SSH 方式，只需要修改远程地址：

```bash
git remote set-url origin git@github.com:yourId/repoName.git
# 等价于
git remote rm origin
git remote add origin git@github.com:yourId/repoName.git

git push -u origin master
```

### 多个 SSH key 共存

存在多个 key 时，可能导致程序无法连接到目标主机。例如 VS Code 的 git 插件无法 pull，提示权限问题（permission denied）。

解决办法：在 `~/.ssh` 目录下新建 `config` 文件（`touch ~/.ssh/config`），添加：

```text
Host gitlab.com
    HostName gitlab.com
    PreferredAuthentications publickey
    IdentityFile ~/.ssh/id_rsa

Host github.com
    HostName github.com
    PreferredAuthentications publickey
    IdentityFile ~/.ssh/id_rsa_github
```

### VS Code 中 git 无法 pull

重新 clone 后默认在 master 分支。在 checkout 其他分支之前，先 pull 或 fetch master，再在命令行中 pull 或 fetch 所有分支。

## 2016-03-12

### nvm、nrm、bower、npm

Node.js 版本管理用 nvm，npm 源管理用 nrm，前端包管理用 bower，后端包管理用 npm。

**安装 nvm**（[教程](https://github.com/creationix/nvm)）：

```bash
cd ~
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.31.0/install.sh | bash
# 激活 nvm
. ~/.nvm/nvm.sh
```

如果是手动安装，需要在 `~/.bashrc`、`~/.profile` 或 `~/.zshrc` 中添加下面的内容，登录时自动激活 nvm（用 curl 脚本安装时会自动添加）：

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"  # This loads nvm
```

常用命令：

```bash
nvm ls                      # 列出已安装的版本
nvm ls-remote               # 列出可安装的版本
nvm install v5.8            # 安装指定版本
nvm use v5.8                # 切换版本
nvm alias default 0.10      # 设置登录时默认使用的版本
```

**安装 nrm**：

```bash
npm install -g nrm
nrm ls        # 列出可用的源
nrm use taobao
```

**安装 bower**：

```bash
npm install -g bower
bower init
bower install <package>
```

建议在项目目录下添加 `.bowerrc` 文件，自定义包的下载目录：

```json
{
  "directory": "public/lib"
}
```

### licode 运行环境搭建

参考：[licode 安装教程](http://lynckia.com/licode/install.html)。以下所有操作都在 Ubuntu 12.04 desktop/server（非 Docker 镜像）下执行，包括 git clone。

> **Node 版本**：安装前要先确定 licode 需要的 Node 版本，版本太高或太低都会有兼容问题。最终确定使用 v0.10.37，并设置合适的 npm 镜像源，建议用 nvm 管理 Node 版本。问题主要出在 `installErizo.sh`，其中 gyp 编译需要 v0.10.37；安装编译成功后，可以切换到更高版本的 Node 运行程序。安装报错不要慌，一般都是依赖版本问题或缺少依赖，冷静逐个解决。

```bash
sudo apt-get install git
git clone https://github.com/ging/licode.git

# 以下建议使用 sudo 执行
./licode/scripts/installUbuntuDeps.sh
./licode/scripts/installErizo.sh
./licode/scripts/installNuve.sh
./licode/scripts/installBasicExample.sh
./licode/scripts/initLicode.sh
./licode/scripts/initBasicExample.sh
```

现在可以访问 `localhost:3001` 测试视频会议示例了。

```bash
sudo netstat -anp | grep node   # 查看进程
sudo pkill node                 # 关闭所有 node 进程
```

**HTTPS 注意事项**：

- Chrome 47 之后调整了 WebRTC 的安全策略，WebRTC 接口必须在 HTTPS 页面中使用。本机访问可以用 HTTP 或 HTTPS，其他机器必须用 HTTPS。
- 测试网站（`licode/extras/basic_example/basicServer.js`）开了两个端口：3001（HTTP）和 3004（HTTPS）。本机可以通过 3001 或 3004 访问，其他机器通过 3004 访问。
- 要支持 HTTPS，在执行 `./licode/scripts/initLicode.sh` 之前，先编辑 `licode/licode_config.js`：

  ```js
  config.erizoController.ssl = true;
  config.erizoController.listen_ssl = true;
  ```

### Ubuntu 挂载光盘

现在的 Ubuntu 用命令挂载光驱，已经不用像以前那样加一堆参数了。先找出光驱的设备名：

```bash
ls /dev | grep cdrom
```

然后直接用这个设备名挂载。例如找到的设备是 `cdrom1`，就把它挂载到 `/media/cdrom`（目录不存在时先手动创建）：

```bash
sudo mkdir -p /media/cdrom
sudo mount /dev/cdrom1 /media/cdrom
```
