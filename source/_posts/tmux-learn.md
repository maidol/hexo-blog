---
title: tmux 使用入门
date: 2016-07-23 22:37:00
categories: 工具
tags:
  - tmux
---

tmux 是一个终端复用工具，可以在一个终端里管理多个会话、窗口和窗格，并且在 SSH 断线后保留工作现场。

<!-- more -->

## 基本概念

一个 tmux 会话（**session**）可以包含多个窗口（**window**），一个窗口可以包含多个窗格（**pane**），每个窗格对应一个终端。

```text
session
└── window
    └── pane
```

## 安装

```bash
sudo apt-get install tmux
```

## 常用命令

| 用途 | 命令 |
| --- | --- |
| 列出所有会话 | `tmux ls` |
| 新建会话 | `tmux new -s <session>` |
| 接入指定会话 | `tmux a -t <session>` |
| 断开当前会话（在会话内执行） | `tmux detach`，或快捷键 `Ctrl+b` 然后按 `d` |
| 关闭指定会话 | `tmux kill-session -t <session>` |
| 关闭指定窗口 | `tmux kill-window -t <window>` |
| 关闭指定窗格 | `tmux kill-pane -t <pane>` |
| 关闭服务（所有会话） | `tmux kill-server` |

> 断开（detach）会话后，会话里的程序会继续在后台运行，之后可以用 `tmux a -t <session>` 重新接入。

## 常用快捷键

先按前缀键 `Ctrl+b`，松开后再按下表中的键：

| 按键 | 作用 |
| --- | --- |
| `?` | 查看帮助 |
| `d` | 断开当前会话 |
| `s` | 列出所有会话 |
| `c` | 新建窗口 |
| `n` / `p` | 切换到下一个 / 上一个窗口 |
| `%` | 左右分割出新窗格 |
| `"` | 上下分割出新窗格 |
| 方向键 | 在窗格之间移动光标 |
| `z` | 最大化 / 还原当前窗格（tmux 1.8 及以上） |
| `[` | 进入复制模式，可以滚屏 |

更完整的快捷键列表见 [学习笔记](/2016/06/27/study-note/) 中的 tmux 部分。
