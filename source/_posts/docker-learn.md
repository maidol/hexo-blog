---
title: docker-learn
date: 2016-7-22 22:37:00
tags: docker
---
- 安装 docker  详细步骤
>- Docker is supported on these Ubuntu operating systems:
    Ubuntu Xenial 16.04 (LTS)
    Ubuntu Wily 15.10
    Ubuntu Trusty 14.04 (LTS)
    Ubuntu Precise 12.04 (LTS)
>- linux内核支持 `uname -r` 查看
>- 1. Update your apt sources
>>- Docker requires a 64-bit installation regardless of your Ubuntu version. Additionally, your kernel must be 3.10 at minimum 
>>- `sudo apt-get update` `sudo apt-get install apt-transport-https ca-certificates` 
>>- Add the new GPG key. `sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D` 
>>- 设置下载源entries, Open the /etc/apt/sources.list.d/docker.list file in your favorite editor, If the file doesn’t exist, create it.
>>>- `vim /etc/apt/sources.list.d/docker.list` 
>>>- Remove any existing entries. 
>>>- Add an entry for your Ubuntu operating system.
>>>>- The possible entries are:
      On Ubuntu Precise 12.04 (LTS)
         deb https://apt.dockerproject.org/repo ubuntu-precise main
      On Ubuntu Trusty 14.04 (LTS)
         deb https://apt.dockerproject.org/repo ubuntu-trusty main
      Ubuntu Wily 15.10
         deb https://apt.dockerproject.org/repo ubuntu-wily main
      Ubuntu Xenial 16.04 (LTS)
         deb https://apt.dockerproject.org/repo ubuntu-xenial main
>>>- Save and close the /etc/apt/sources.list.d/docker.list file.
>>- Update the APT package index. `sudo apt-get update` 
>>- Purge the old repo if it exists. `sudo apt-get purge lxc-docker` 
>>- Verify that APT is pulling from the right repository. `apt-cache policy docker-engine` 
>>- From now on when you run `apt-get upgrade`, APT pulls from the new repository.
>- 2. Prerequisites by Ubuntu Version
>>- Ubuntu Xenial 16.04 (LTS) / Ubuntu Wily 15.10 / Ubuntu Trusty 14.04 (LTS)
    For Ubuntu Trusty, Wily, and Xenial, it’s recommended to install the linux-image-extra kernel package. The linux-image-extra package allows you use the aufs storage driver.

    To install the linux-image-extra package for your kernel version:

    Open a terminal on your Ubuntu host.
    
>>>- Update your package manager. `sudo apt-get update` 
>>>- Install the recommended package. `sudo apt-get install linux-image-extra-$(uname -r)` 
>>>- Go ahead and install Docker.
>>- If you are installing on Ubuntu 14.04 or 12.04, apparmor is required. You can install it using: `apt-get install apparmor` 
>>- Ubuntu Precise 12.04 (LTS)
>>>- `uname -r` 查看 
>>>- For Ubuntu Precise, Docker requires the 3.13 kernel version. If your kernel version is older than 3.13, you must upgrade it. Refer to this table to see which packages are required for your environment
>>>- `sudo apt-get update` 
>>>- Install both the required and optional packages `sudo apt-get install linux-image-generic-lts-trusty` 
>>>- `sudo reboot` After your system reboots, go ahead and install Docker. 
>- 3. Install (安装和运行都需要sudo或者root)
>>- `sudo apt-get update` 
>>- `sudo apt-get install docker-engine` 
>>- `sudo service docker start` 
>>- Verify docker is installed correctly. `sudo docker run hello-world` This command downloads a test image and runs it in a container. When the container runs, it prints an informational message. Then, it exits. 
- ubuntu 14 docker安装
>- `sudo apt-get install lxc-docker` 
>- `sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9` 
>- `sudo bash -c "echo deb https://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list" ` 
>- `sudo apt-get update` 
>- `sudo apt-get install lxc-docker` 
>- `sudo service docker start` 
>- `docker version`  
- 安装 Docker 官方的最新发行版， 支持 Ubuntu 12.04 以上版本
>- `curl -sSL https://get.daocloud.io/docker | sh`  
>- `sudo service docker status` 输出 docker start/running 就表示安装成功 
- docker常用命令
>- `docker images` 列出所有镜像(images) 
>- `docker ps -a/-l`    列出正在运行的(容器)containers 
>- `docker pull ubuntu` 下载镜像 
>- `docker run -i -t ubuntu /bin/bash`  运行ubuntu镜像 
>- `docker commit 3a09b2588478 ubuntu:mynewimage`  提交你的变更，并且把容器保存成Tag为mynewimage的新的ubuntu镜像.(注意，这里提交只是提交到本地仓库，类似git) 
- Docker去sudo
>- 在Ubuntu下，在执行Docker时，每次都要输入sudo，同时输入密码，这里把当前用户执行权限添加到相应的docker用户组里面 
>- 添加一个新的docker用户组 `sudo groupadd docker` 
>- 添加当前用户到docker用户组里，注意这里的king为ubuntu登录用户名 `sudo usermod -aG docker king` 
>- 重启Docker后台监护进程 `sudo service docker restart` 
>- 重启之后，尝试一下，是否生效 `docker version` 
>- 若还未生效，则系统重启，则生效 `sudo reboot` 
>- Cannot connect to the Docker daemon. Is the docker daemon running on this host? 
>>- 出现这种错误 先尝试用sudo执行, 再尝试下面步骤 
>>>- Check that the DOCKER_HOST environment variable is not set for your shell. If it is, unset it.
>>>- 还是不行则尝试 `sudo service docker stop` `sudo rm -rf /var/lib/docker` `sudo service docker start`  `sudo docker version` 
>>>>- The above commands will not remove images, containers, volumes, or user created configuration files on your host. If you wish to delete all images, containers, and volumes run the following command:`sudo rm -rf /var/lib/docker` 
- 如何进入Docker容器进程及如何退出
>>- 如果启动了Docker容器，比如这样：`docker run -itd -p 3000:3000 --name my-web -v "$(pwd)":/webapp -w /webapp node npm start` 
>>- 我启动了一个Node Web App。如何看到终端打印的报错和日志呢？docker有命令可以让你进入（attach）和退出（detach）该进程  `docker attach my-web ` 
>>- 退出，一定不要用ctrl+c，那样就是让docker容器停止了。先按，ctrl+p 再按，ctrl+q
>>>- 只有在启动时附加参数 -it 才能 ctrl+p ctrl+q 退出  
- -d -t -i 参数 , exec 
>- `docker run -d rabbitmq`  参数运行了容器, `docker exec -it rabbitmq /bin/bash` 可以进入容器进行管理 `exit` 退出 , 对容器修改后, 可通过 `commit` 固化为images  
- 使用daocloud加速器 加速镜像下载速度
>- 需要登录daocloud [https://dashboard.daocloud.io/](https://dashboard.daocloud.io/), 选择加速器选项 -> 立即开始
>- 按照提示安装
>- 安装 Docker安装 Docker 官方的最新发行版， 支持 Ubuntu 12.04 以上版本
>>- `curl -sSL https://get.daocloud.io/docker | sh` `sudo service docker status` 输出 docker start/running 就表示安装成功 
>- 安装主机监控程序
>>- `curl -sSL https://get.daocloud.io/daomonit/install.sh | sh -s xxxxxxxxxxxxxxxxxxxxxxx`  
>- 自有主机会跟daocloud账号绑定 
>- `dao pull images` 使用dao命令拉取镜像 , 需要先登录daocloud 拉取镜像前请先尝试登录: `docker login daocloud.io` 



