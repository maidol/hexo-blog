---
title: Docker 学习笔记
date: 2016-07-22 22:37:00
categories: Docker
tags:
  - docker
---

Docker 在 Ubuntu 上的安装、常用命令、免 sudo 配置、容器进出方式，以及国内镜像加速。

<!-- more -->

> **时效说明**：本文写于 2016 年。文中的 `docker-engine` / `lxc-docker` 包、`apt.dockerproject.org` / `get.docker.io` 软件源和 `p80.pool.sks-keyservers.net` 密钥服务器都**已经废弃**。现在请参考第一节的"当前推荐的安装方式"。第二、三节保留下来作为历史记录。

## 一、当前推荐的安装方式

最简单的方式是使用官方便捷脚本：

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 验证
sudo docker run hello-world
```

生产环境建议按 [官方文档](https://docs.docker.com/engine/install/ubuntu/) 添加 apt 软件源，安装 `docker-ce` 包。

## 二、2016 年的安装方式（Ubuntu，docker-engine）

当时 Docker 支持的 Ubuntu 版本有：

- Ubuntu Xenial 16.04 (LTS)
- Ubuntu Wily 15.10
- Ubuntu Trusty 14.04 (LTS)
- Ubuntu Precise 12.04 (LTS)

Docker 要求 **64 位**系统，并且内核版本**至少为 3.10**。可以用 `uname -r` 查看内核版本。

### 1. 更新 apt 软件源

```bash
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates

# 添加 GPG key
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 \
  --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
```

编辑 `/etc/apt/sources.list.d/docker.list`（不存在就新建），删除已有内容，按系统版本添加**一行**：

```text
# Ubuntu Precise 12.04 (LTS)
deb https://apt.dockerproject.org/repo ubuntu-precise main
# Ubuntu Trusty 14.04 (LTS)
deb https://apt.dockerproject.org/repo ubuntu-trusty main
# Ubuntu Wily 15.10
deb https://apt.dockerproject.org/repo ubuntu-wily main
# Ubuntu Xenial 16.04 (LTS)
deb https://apt.dockerproject.org/repo ubuntu-xenial main
```

保存后执行：

```bash
sudo apt-get update
# 如果装过旧的 lxc-docker，先清除
sudo apt-get purge lxc-docker
# 确认 APT 从新的软件源拉取
apt-cache policy docker-engine
```

之后执行 `apt-get upgrade` 时，APT 会从新的软件源拉取更新。

### 2. 按 Ubuntu 版本准备依赖

**Xenial 16.04 / Wily 15.10 / Trusty 14.04**

推荐安装 `linux-image-extra` 内核包，这样才能使用 `aufs` 存储驱动：

```bash
sudo apt-get update
sudo apt-get install linux-image-extra-$(uname -r)
```

Ubuntu 14.04 和 12.04 还需要安装 `apparmor`：

```bash
sudo apt-get install apparmor
```

**Precise 12.04**

Docker 需要 3.13 及以上的内核。如果内核版本低于 3.13，需要先升级：

```bash
sudo apt-get update
sudo apt-get install linux-image-generic-lts-trusty
sudo reboot
```

> 如果启动容器时报错 `apparmor failed to apply profile: no such file or directory`，执行 `sudo apt-get install apparmor` 即可。

### 3. 安装并启动（需要 sudo 或 root 权限）

```bash
sudo apt-get update
sudo apt-get install docker-engine
sudo service docker start

# 验证：会下载一个测试镜像并在容器中运行，打印一段信息后退出
sudo docker run hello-world
```

### 其他历史安装方式

Ubuntu 14 上更早的 `lxc-docker` 包：

```bash
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 \
  --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
sudo sh -c "echo deb https://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"
sudo apt-get update
sudo apt-get install lxc-docker
sudo service docker start
docker version
```

使用安装脚本（支持 Ubuntu 12.04 以上）：

```bash
curl -sSL https://get.docker.com/ | sh
# 或 DaoCloud 国内镜像
curl -sSL https://get.daocloud.io/docker | sh

# 输出 docker start/running 表示安装成功
sudo service docker status
```

### 卸载

```bash
sudo apt-get purge docker-engine
sudo apt-get autoremove --purge docker-engine
# 上面的命令不会删除镜像、容器、数据卷，如需彻底清除：
sudo rm -rf /var/lib/docker
```

## 三、常用命令

| 命令 | 说明 |
| --- | --- |
| `docker images` | 列出本地所有镜像 |
| `docker ps` | 列出正在运行的容器 |
| `docker ps -a` | 列出所有容器（包括已停止的） |
| `docker ps -l` | 列出最近创建的一个容器 |
| `docker pull ubuntu` | 下载镜像 |
| `docker run -it ubuntu /bin/bash` | 以交互方式运行 ubuntu 镜像 |
| `docker exec -it <容器> /bin/bash` | 进入正在运行的容器 |
| `docker commit <容器ID> ubuntu:mynewimage` | 把容器保存为新镜像 |

### `-i` / `-t` / `-d` 参数

- `-i`：即使没有附加到容器，也保持 STDIN 打开。无论前台还是后台（`-d`）运行，都建议加上。
- `-t`：分配一个伪终端。
- `-d`：后台运行容器。

```bash
docker run -d -i ubuntu /bin/bash
```

后台运行并保持一个 stdin。如果把 `/bin/bash` 换成脚本（例如 `/init.sh`），脚本最后必须以 `/bin/bash` 这类前台进程结尾，否则脚本执行完容器就退出了，`-i` 也不起作用。如果 `docker run -d -i ubuntu` 后面不指定命令，默认执行镜像的 `CMD`（ubuntu 镜像是 `/bin/bash`）。

### 提交容器为镜像

```bash
docker commit 3a09b2588478 ubuntu:mynewimage
```

把容器的变更保存成 tag 为 `mynewimage` 的新 ubuntu 镜像。注意这里只是提交到**本地**，类似 `git commit`，要共享给别人还需要 `docker push`。

### 后台运行 + exec 进入

```bash
docker run -d --name rabbitmq rabbitmq
docker exec -it rabbitmq /bin/bash   # 进入容器管理，exit 退出
```

对容器做了修改后，可以用 `docker commit` 固化为镜像。

## 四、免 sudo 运行 Docker

在 Ubuntu 上执行 Docker 命令每次都要输入 sudo 和密码，可以把当前用户加入 `docker` 用户组：

```bash
# 添加 docker 用户组（安装 Docker 时通常已经自动创建）
sudo groupadd docker
# 把当前用户加入 docker 组
sudo usermod -aG docker $USER
# 重启 Docker 守护进程
sudo service docker restart
```

**重新登录**（或执行 `newgrp docker`）后，执行 `docker version` 检查是否生效。还不生效的话就重启系统。

> **安全提示**：`docker` 组的成员相当于拥有 root 权限，只把可信用户加入该组。

### 报错：Cannot connect to the Docker daemon

```text
Cannot connect to the Docker daemon. Is the docker daemon running on this host?
```

按顺序排查：

1. 先用 `sudo` 执行一次，排除权限问题（见上面的免 sudo 配置）。
2. 执行 `sudo service docker status`，确认守护进程已经启动。
3. 检查当前 shell 是否设置了 `DOCKER_HOST` 环境变量，如果设置了就 `unset DOCKER_HOST`。
4. 最后的手段：清空 Docker 数据目录后重启。

```bash
sudo service docker stop
sudo rm -rf /var/lib/docker
sudo service docker start
sudo docker version
```

> **警告**：`rm -rf /var/lib/docker` 会**删除所有镜像、容器和数据卷**，执行前务必确认。

## 五、进入与退出容器

以下面这个 Node Web 应用容器为例：

```bash
docker run -itd -p 3000:3000 --name my-web -v "$(pwd)":/webapp -w /webapp node npm start
```

查看终端输出的日志和报错：

```bash
docker attach my-web   # 附加到容器主进程
docker logs -f my-web  # 只看日志，更安全
```

**退出 attach 时不要按 `Ctrl+C`**，那样会把容器停掉。应该先按 `Ctrl+P` 再按 `Ctrl+Q`。只有启动时带了 `-it` 参数，才能用 `Ctrl+P Ctrl+Q` 退出。

## 六、使用 DaoCloud 加速器

> DaoCloud 是国内的镜像源，Docker Hub 是国外的官方镜像源。以下为 2016 年的操作方式，现在一般直接在 `/etc/docker/daemon.json` 中配置 `registry-mirrors`。

1. 登录 [DaoCloud 控制台](https://dashboard.daocloud.io/)，选择"加速器" → "立即开始"，按提示安装。
2. 安装主机监控程序（`xxx` 为控制台给出的 token）。
3. 主机会和 DaoCloud 账号绑定。删除主机只适用于已经断开连接的主机，删除前先卸载监控程序。
4. 用 `dao` 命令拉取镜像：`dao pull <image>`。

```bash
# 安装主机监控程序
curl -sSL https://get.daocloud.io/daomonit/install.sh | sh -s xxxxxxxxxxxxxxxxxxxxxxx

# 卸载主机监控程序
dpkg -r daomonit   # Ubuntu/Debian
rpm -e daomonit    # CentOS/Fedora
```

登录镜像仓库：

```bash
docker login daocloud.io   # 登录 DaoCloud（需开通"我的镜像"服务）
docker login               # 登录 Docker Hub，之后可以 pull/push 自己的镜像
```
