---
title: docker-learn
date: 2016-7-22 22:37:00
tags: docker
---
- docker安装
>- `sudo apt-get install lxc-docker` 
>- `sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9` 
>- `sudo bash -c "echo deb https://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list" ` 
>- `sudo apt-get update` 
>- `sudo apt-get install lxc-docker` 
>- `sudo service docker start` 
>- `docker version`  
- docker常用命令
>- `docker images` 列出所有镜像(images) 
>- `docker ps `    列出正在运行的(容器)containers 
>- `docker pull ubuntu` 下载镜像 
>- `docker run -i -t ubuntu /bin/bash`  运行ubuntu镜像 
>- `docker commit 3a09b2588478 ubuntu:mynewimage`  提交你的变更，并且把容器保存成Tag为mynewimage的新的ubuntu镜像.(注意，这里提交只是提交到本地仓库，类似git) 
- Docker去sudo
>- 在Ubuntu下，在执行Docker时，每次都要输入sudo，同时输入密码，这里把当前用户执行权限添加到相应的docker用户组里面 
>- 添加一个新的docker用户组 `sudo groupadd docker` 
>- 添加当前用户到docker用户组里，注意这里的king为ubuntu登录用户名 `sudo gpasswd -a king docker` 
>- 重启Docker后台监护进程 `sudo service docker restart` 
>- 重启之后，尝试一下，是否生效 `docker version` 
>- 若还未生效，则系统重启，则生效 `sudo reboot` 
>- Cannot connect to the Docker daemon. Is the docker daemon running on this host? 
>>- 出现这种错误 尝试下面步骤 
>>>- `sudo service docker stop` `sudo rm -rf /var/lib/docker` `sudo service docker start`  `sudo docker version` 



