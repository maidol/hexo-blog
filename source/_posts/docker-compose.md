---
title: docker-compose
date: 2016-10-03 21:37:00
tags: 
	- docker-compose
	- 自动化部署
---
- 安装docker-compose与使用 [参考1](http://blog.csdn.net/lincyang/article/details/44588397)[参考2](https://docs.docker.com/compose/install/)[参考3](https://docs.docker.com/compose/compose-file/)
>- `sudo -i` 进入root用户
>- 安装: `curl -L https://github.com/docker/compose/releases/download/1.8.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose` 
>- 修改权限: `chmod +x /usr/local/bin/docker-compose` , 退出root `exit` 
>- 如果以上两条命令安装不了, 则尝试 install as a container
>>- `curl -L https://github.com/docker/compose/releases/download/1.8.0/run.sh > /usr/local/bin/docker-compose` `chmod +x /usr/local/bin/docker-compose` 
>- 为bash/zsh shell 配置命令 [参考](https://docs.docker.com/compose/completion/) 
>- [使用例子-Django](https://docs.docker.com/compose/django/) 
>- 启动: `docker-compose -f xxx.yml up -d`, -f 指定yml文件, -d 后台运行 
```yml
# xxx.yml 
mysql:
    image: "mysql"
    ports:
        - "3306:3306"
    volumes:
        - ./data:/var/lib/mysql
    environment:
        - MYSQL_ROOT_PASSWORD=xxx
mongodb:
    image: "mongo"
    ports:
        - "27017:27017"
redis:
    image: "redis"
    ports:
        - "6379:6379"
rabbitmq:
    image: "rabbitmq:3-management"
    ports:
        - "15672:15672"
        - "5672:5672"
    environment:
        - RABBITMQ_DEFAULT_USER=xxx
        - RABBITMQ_DEFAULT_PASS=xxx
        - RABBITMQ_DEFAULT_VHOST=xxx
```
>- 停止: `docker-compose -f xxx.yml down` 