---
title: hexo-deploy
date: 2016-7-06 22:37:00
tags: hexo deploy git
---

HEXO+Github Deploy Blog
--------------
- hexo是一款基于Node.js的静态博客框架, [hexo github](https://github.com/hexojs/hexo)
>- 配置环境
>>- 安装Node, 安装Git
>>- 安装Hexo
>>>- `mkdir blog` `cd ./blog` `npm install-g hexo` 
>>>- 初始化`hexo init`
>>>- 生成静态页 `hexo generate` or `hexo g`
>>>- 本地启动服务 `hexo server`
>>>- 浏览器输入[http://localhost:4000](http://localhost:4000])
>>- 配置Github, 部署到Github
>>>- 登陆Github, 建立Repository
>>>>- 建立与你用户名对应的仓库，仓库名必须为【your_user_name.github.io】
>>>- 建立关联
>>>>- `cd ./blog`  `vim _config.yml` 翻到最后, 如下编辑
      deploy:
        type: git
        repo: https://github.com/maidol/maidol.github.io.git
        branch: master
>>>>- 执行命令 `npm install hexo-deployer-git --save`
>>>>- 配置github用户信息 `git config --global user.email "you@example.com"` `git config --global user.name "Your Name"`
>>>>- 执行部署命令 `hexo deploy`
>>>>- 浏览器中输入[http://maidol.github.io/](http://maidol.github.io/)
>>>>- 每次部署的步骤 `hexo clean` `hexo generate` `hexo deploy`
>- Hexo的常用命令
>>- `hexo new"postName"` #新建文章
>>- `hexo new page"pageName"` #新建页面
>>- `hexo generate` #生成静态页面至public目录
>>- `hexo server` #开启预览访问端口
>>- `hexo deploy` #将.deploy目录部署到GitHub