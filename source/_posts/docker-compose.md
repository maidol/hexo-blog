---
title: docker-compose 安装与使用
date: 2016-10-03 21:37:00
categories: Docker
tags:
  - docker-compose
  - 自动化部署
---

用 docker-compose 通过一个 YAML 文件一键启动 MySQL、MongoDB、Redis、RabbitMQ 等开发环境依赖。

<!-- more -->

参考资料：

- [Docker Compose 安装](https://docs.docker.com/compose/install/)
- [Compose 文件格式](https://docs.docker.com/compose/compose-file/)
- [命令行补全](https://docs.docker.com/compose/completion/)
- [使用示例：Django](https://docs.docker.com/compose/django/)
- [docker-compose 入门（CSDN）](http://blog.csdn.net/lincyang/article/details/44588397)

> **时效说明**：本文写于 2016 年，使用的是独立的 docker-compose 1.8.0。现在的 Compose V2 以 Docker CLI 插件的形式提供，命令是 `docker compose`（中间是空格，不再有连字符）。Docker Desktop 自带；在 Linux 上可以通过 `docker-compose-plugin` 包安装。

## 安装

下载二进制文件到 `/usr/local/bin`（需要 root 权限）：

```bash
sudo -i   # 切换到 root 用户
curl -L "https://github.com/docker/compose/releases/download/1.8.0/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
exit      # 退出 root
```

如果上面的方式装不上，可以改为以容器方式运行 compose：

```bash
curl -L https://github.com/docker/compose/releases/download/1.8.0/run.sh > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

验证：

```bash
docker-compose version
```

## 编写 compose 文件

下面的 `xxx.yml` 定义了常用的几个服务（Compose 文件格式 v2）：

```yaml
version: "2"
services:
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

> 2016 年原文使用的是不带 `version` / `services` 的 v1 格式（服务直接写在顶层）。v1 格式已经废弃，不建议再使用。另外，在当前的 Compose 规范中顶层的 `version` 字段也已过时，Compose V2 会忽略它并给出警告，新写的文件可以直接从 `services:` 开始。

## 常用命令

| 命令 | 说明 |
| --- | --- |
| `docker-compose -f xxx.yml up -d` | 启动所有服务。`-f` 指定 yml 文件，`-d` 后台运行 |
| `docker-compose -f xxx.yml ps` | 查看服务状态 |
| `docker-compose -f xxx.yml logs -f` | 查看日志 |
| `docker-compose -f xxx.yml stop` | 停止服务，保留容器 |
| `docker-compose -f xxx.yml down` | 停止并**删除**容器和网络 |

> 文件名为默认的 `docker-compose.yml` 时，可以省略 `-f` 参数。
