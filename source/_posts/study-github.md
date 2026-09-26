---
title: GitHub 新建本地仓库与远程仓库的基本用法
date: 2016-07-06 22:37:00
categories: 工具
tags:
  - deploy
  - git
  - github
---

从零新建一个本地 Git 仓库并关联到 GitHub 远程仓库，以及一个好用的 `git log` 格式。

<!-- more -->

## 新建仓库并推送到 GitHub

> **前提**：先在 GitHub 上手动创建空仓库 `https://github.com/yourId/repoName.git`（不要勾选自动生成 README，否则远程仓库已有提交，第一次推送会因为历史不一致被拒绝）。

```bash
mkdir gitRepo
cd gitRepo
git init
echo "# repoName" > README.md
git add README.md
git commit -m "first commit"
git remote add origin https://github.com/yourId/repoName.git
git push -u origin master
```

`git push -u` 会把本地 `master` 和远程 `origin/master` 关联起来，之后直接执行 `git push` / `git pull` 即可。

> 2020 年 10 月起，GitHub 新建仓库的默认分支名是 `main`。如果远程仓库使用 `main`，把上面的 `master` 换成 `main`。

## 查看提交历史

图形化、带颜色的单行提交历史：

```bash
git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative
```

可以设置成别名，以后直接用 `git lg`：

```bash
git config --global alias.lg "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative"
```
