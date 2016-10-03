---
title: study-github
date: 2016-7-06 22:37:00
tags: 
  - deploy 
  - git 
  - github
---

Github新建本地仓库，远程仓库基本用法
--------------
- PS: 需要先在github手动创建[https://github.com/yourId/repoName.git](https://github.com/yourId/repoName.git)
- Create a new repository on the command line
>>- `mkdir gitRepo` `cd gitRepo`
>>- `git init `
>>- `git add README.md`
>>- `git commit -m "first commit"`
>>- `git remote add origin https://github.com/yourId/repoName.git`
- 查看commit
>- `git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative` 
