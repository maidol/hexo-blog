---
title: tmux-learn
date: 2016-7-23 22:37:00
tags: tmux
---
- 基本的使用
> - 一个tmux session 可以包含多个window，一个window包含多个pane，一个pane对应一个终端session 
> - 安装`apt-get install tmux` 
> - 列出当前所有会话`tmux ls` 
> - 新建会话`tmux new -s @session` 
> - 接入指定会话`tmux a -t @session` 
> - 临时断开会话(在会话窗口执行) `tmux detach`  -> 先按组合Ctrl+b 再按 d 
> - 关闭服务(所有会话)`tmux kill-server`  
> - 关闭会话`tmux kill-session -t @session` 
> - 关闭窗口`tmux kill-window -t @name` 
> - 关闭会话`tmux kill-pane -t @name` 