---
title: Hexo + GitHub Pages 搭建博客
date: 2016-07-06 22:37:00
categories: 工具
tags:
  - hexo
  - deploy
  - git
---

[Hexo](https://github.com/hexojs/hexo) 是一款基于 Node.js 的静态博客框架。本文记录用 Hexo 搭建博客并部署到 GitHub Pages 的完整步骤。

<!-- more -->

## 1. 准备环境

先安装好 [Node.js](https://nodejs.org/) 和 [Git](https://git-scm.com/)。

## 2. 安装 Hexo 并初始化博客

```bash
# 安装 Hexo 命令行工具（Hexo 3.x 起，全局只需安装 hexo-cli）
npm install -g hexo-cli

# 初始化博客目录（会自动安装依赖）
hexo init blog
cd blog
npm install

# 生成静态页面
hexo generate   # 简写：hexo g

# 启动本地预览服务
hexo server     # 简写：hexo s
```

启动后在浏览器中打开 [http://localhost:4000](http://localhost:4000) 即可预览。

## 3. 部署到 GitHub Pages

### 3.1 创建仓库

登录 GitHub，新建一个与你的用户名对应的仓库，仓库名必须是 `<your_user_name>.github.io`。

### 3.2 配置部署信息

编辑博客根目录下的 `_config.yml`，翻到文件末尾，按如下方式修改：

```yaml
deploy:
  type: git
  repo: https://github.com/maidol/maidol.github.io.git
  branch: master
```

> **注意**：YAML 对缩进敏感，冒号后面必须有一个空格，并且只能用空格缩进、不能用 Tab。

### 3.3 安装部署插件

```bash
npm install hexo-deployer-git --save
```

### 3.4 配置 Git 用户信息

```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

### 3.5 部署

```bash
hexo deploy     # 简写：hexo d
```

部署完成后访问 [http://maidol.github.io/](http://maidol.github.io/) 即可看到博客。

以后每次更新博客，依次执行：

```bash
hexo clean && hexo generate && hexo deploy
```

## Hexo 常用命令

| 命令 | 简写 | 说明 |
| --- | --- | --- |
| `hexo new "postName"` | `hexo n` | 新建文章 |
| `hexo new page "pageName"` | | 新建页面 |
| `hexo new draft "draftName"` | | 新建草稿（存放在 `source/_drafts`） |
| `hexo publish "draftName"` | | 把草稿发布为正式文章 |
| `hexo generate` | `hexo g` | 生成静态页面到 `public` 目录 |
| `hexo server` | `hexo s` | 启动本地预览服务（默认端口 4000） |
| `hexo deploy` | `hexo d` | 部署（git 部署会用到 `.deploy_git` 目录） |
| `hexo clean` | | 清除缓存文件 `db.json` 和已生成的 `public` 目录 |
