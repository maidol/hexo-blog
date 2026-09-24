---
title: DrSG Harness Kit 设计与使用指南
date: 2026-09-23 18:30:00
tags:
  - AI Agent
  - Code Graph
  - DrSG
  - Claude Code
categories:
  - AI & Tools
---

在将大语言模型（LLM）引入复杂工程实践的过程中，几乎所有开发者都会遇到两大核心瓶颈：**智能体上下文记忆的断裂**以及**对大型代码库结构理解的粗糙与失真**。

面对数百个源文件和复杂的依赖网络，基于纯文本匹配（`grep` / `rg`）的搜索方式不仅容易产生大量误报，更无法回答「改动这个函数会影响哪些调用方」、「类型依赖如何逐级传递」等深度问题。与此同时，随着会话被压缩（compact）或结束，智能体上一轮踩坑沉淀下来的关键结论往往随之蒸发，导致跨会话甚至跨项目的经验无法流转。

**DrSG Harness Kit** 正是为此而生的智能体侧基础设施工具套件。它为以 Claude Code 为代表的智能体提供了集中式支撑：**为每个代码仓库提供精准的增量代码图（Code Plane），并为多智能体环境提供全局共享的长期记忆层（Memory Plane）**。

本文将全面拆解 DrSG Harness Kit 的双平面架构设计、工作机制、核心动词规范以及在生产环境中的实战部署与使用方法。

项目仓库：[maidol/drsg-harness-kit](https://github.com/maidol/drsg-harness-kit)

---

## 一、双平面架构设计与核心原理

DrSG Harness Kit 最核心的架构特征在于**「代码图」与「记忆层」的双平面彻底隔离与拓扑正交**。

![一台机器上的部署拓扑：记忆层一个全局 daemon，代码图每仓一个](../images/drsg-harness-kit/daemon-topology.svg)

两边是**方向相反**的：记忆层聚合（一个 daemon、一个库，按 `p.path` 分项目），代码图独立（一仓一端口、一仓一库）。两个 daemon 都不开机自启，按需启动。

### 1.1 两个平面的本质差异

| 维度 | 代码图 (Code Plane) | 记忆层 (Memory Plane) |
|---|---|---|
| **核心数据** | 语言插件从 AST 解析出的符号、类型与调用边 | 结构化事实（Fact）、会话记录（Session）、跨项目待办（Event） |
| **写入机制** | `drsg serve watch` 增量监听 git commit 自动折叠 | Hooks 自动上报元数据 + 模型按契约协议主动写入 |
| **部署粒度** | **一仓一个独立 Daemon**、独立端口、独立数据库 | **全机唯一单例 Daemon**，通过 `Project.path` 逻辑隔离 |
| **物理存储** | `<repo>/graph.drsg`（Native 目录锁） | `~/.drsg-memory/memory.drsg` |
| **核心用途** | 回答「符号是什么、调用链路、变更爆炸半径」 | 回答「过去得出过什么结论、别的任务需要注意什么」 |

为什么不将所有仓库的代码图和记忆层塞入同一个进程？
这是由于底层 Native 存储引擎对**单库多进程排他锁**的严格约束（同一时刻一个数据库只允许一个进程持有文件锁）。将生命周期完全不同的各仓代码图与全局记忆解耦，避免了单点崩溃带来的级联影响。

### 1.2 代码图如何构建与增量同步

代码图并不是全量扫描生成后就一成不变的，它的构建依赖 `drsg serve watch` 进程：
1. **监听提交**：每次本地工作区产生新的 Git commit，内置的 WebAssembly (wasm) 语言插件会重新解析变动代码。
2. **符号与边折叠**：将源码抽取为 `Function`, `Method`, `Struct`, `Trait`, `Module`, `File` 等实体节点，并建立 `CALLS`, `REFERENCES`, `USES_TYPE`, `IMPORTS` 等关系边。
3. **标记解析边界**：对于动态语言特性或跨模块未确定的引用，明确记录为 `UnresolvedRef` 节点——**能够明确指出「未解析」而不是凭空猜测，是代码图敢于返回「不存在」的前提**。
4. **性能表现**：首次载入 wasm 插件约耗时 13 秒，但之后的每次增量提交折叠仅需 1~2 秒左右。

![代码图的工作原理：源码树经 wasm 插件折进 plane，动词从 plane 读，snippet 还要读文件树](../images/drsg-harness-kit/code-plane-architecture.svg)

图中那条区别对待的线值得重点关注：**结构类动词（`context` / `impact` / `trace` / `describe`）只查 plane，因此跨仓可用；而 `grep` 和 `snippet` 要读文件树，文件树是进程级的（由 `--dir` 指定），与调用时传的 `plane` 无关**。这意味着跨仓问结构没问题，但跨仓要源码必须找该仓库自己的 daemon。

---

## 二、Codegraph Router：多仓代码图的统一入口

在多项目开发中，如果智能体每切换一个仓库都需要重新配置一套 MCP 地址与 Token，协作体验将非常割裂。此外，模型很容易传错 `plane` 参数（默认的 `startup` 是空平面，返回 `no symbol matches`，使模型误以为符号不存在）。

为此，Kit 提供了 `codegraph-router.py`，实现 MCP-to-MCP 的透明路由分发：

![router 的结构：registry 只存路径，地址与 token 现读各仓自己的 .mcp.json](../images/drsg-harness-kit/codegraph-router-architecture.svg)

```text
智能体在任意工作区提出请求：
"查一下 drsg-harness-kit 里的 searches 函数定义"
                       │
                       ▼
             [ Codegraph Router ]
                       │
      读取 ~/.drsg-memory/graphs (仓库注册表)
                       │
       目标: /data/projects/maidol/drsg-harness-kit
                       │
     读取目标仓库的 .mcp.json (地址与 Bearer Token)
                       │
           目标 Daemon 是否存活？
             ├── 是: 直接转发请求
             └── 否: 懒启动目标 daemon (codegraph.sh start --dir ...)
                       │
                       ▼
            目标仓库 Code Graph Daemon
    (执行解析并返回：codegraph-usage.searches Function)
```

**Router 的核心优势**：
- **Token 零冗余存储**：Router 本身不保留各仓库的 Token，仅在转发时即时读取目标仓库受保护的 `.mcp.json`。
- **自动懒启动（Lazy Start）**：平时不常用的仓库 daemon 不需要常驻内存，首次调用自动拉起。
- **严格防御伪造**：若目标路径未注册或 daemon 启动失败，Router 会直接返回路由异常，严禁返回空匹配，杜绝模型产生幻觉。

---

## 三、代码图实操：七大核心动词与生产铁律

在智能体的系统提示词中，我们定义了明确的七大核心动词以取代传统的低效文本工具：

### 3.1 核心动词矩阵

| 动词 | 适用问题 | 返回内容与特点 |
|---|---|---|
| `context` | 这个符号是什么？谁在调用它？ | 包含符号定义、参数签名、一跳（1-hop）直接调用者与被调用者 |
| `impact` | **修改/删除这个符号会破坏什么？** | 沿着入边方向进行深度爆炸半径扫描，**按跳数距离分组计数** |
| `trace` | 符号 A 如何通过调用链到达符号 B？ | 最短调用路径（Shortest CALLS Path），逐跳打印调用轨迹 |
| `describe` | 查看符号签名与定义位置 | 极低 token 消耗，返回数百字符的精简签名 |
| `snippet` | 获取特定符号或文件区间的源码 | 按行号或符号返回具体代码实现 |
| `grep` | 日志文本、注释、配置等图未建模的内容 | 源码树字面搜索，且每个搜索结果都会标记属于哪个代码图符号 |
| `describe_plane`| 探查图谱元数据与同步状态 | 包含当前节点数、边类型清单以及已对齐的 Git commit hash |

### 3.2 真实案例：代码图调用路径 vs 纯文本 grep

当智能体被要求查看 `searches` 函数的具体实现时：

- **传统纯文本方式**：
  ```bash
  rg -n --glob '*.py' '^def searches\(' .
  sed -n '131,142p' tools/codegraph-usage.py
  # 若想找调用方，还必须再次 grep 并人工剔除误报：
  rg -n '\bsearches\s*\(' tools
  ```
- **代码图精准定位链路**：
  1. `context(name="searches", plane="...")` $\rightarrow$ 解析出规范符号键 `codegraph-usage.searches`，明确是 Function，并直接列出上游调用方 `codegraph-usage.main`；
  2. `snippet(name="tools/codegraph-usage.py:131-142", plane="...")` $\rightarrow$ 精准提取源码正文。

### 3.3 生产环境严防踩坑的两条铁律

1. **`impact` 的遍历深度必须加到某一层返回空**：
   - 默认深度为 3 跳。如果第 3 跳依然有节点返回，说明影响链路未截断，所得结果仅是「前三跳」，不是完整的爆炸半径！
   - 正确做法：必须将 `depth` 逐级提升（最大支持 6 跳），直到某一层出现 0 个新增节点。
2. **歧义候选超过 20 条时严禁随意猜测**：
   - 当按模糊名称查询遇到大量同名候选时，返回列表会被截断至 20 条且**不按相关性加权**。
   - 此时切忌盲目猜测，应当使用 `模块::方法` 或 `类::方法`（如 `codegraph-usage::searches`）进行精确收窄。

---

## 四、长期记忆层机制：Fact、Event 与生命周期 Hooks

记忆层建立在 `~/.drsg-memory/memory.drsg` 数据库之上，核心围绕以下图谱模型运转：

```text
[Project] <────BELONGS_TO──── [Session] (单次交互会话元数据)
   │
   ├─────ABOUT──────────────> [Fact]    (高价值工程结论、踩坑教训、规则约束)
   │
   └─────NOTIFY─────────────> [Event]   (待办提醒、跨项目协作交接通知)
```

### 4.1 会话全生命周期流程

```text
1. 会话启动 (SessionStart Hook)
   ├── 注册 / 恢复 Session 节点
   ├── 计算本项目所有 Fact，生成常驻精炼简报 (Briefing)
   ├── 查询关联的未处理 Event (最多 3 条跨项目待办)
   └── 将常驻记忆注入智能体上下文

2. 提示词提交 (UserPromptSubmit Hook)
   ├── 对用户输入提取 N-gram + IDF 关键词
   ├── 语义召回高度相关的历史 Fact (最多 4 条，支持跨项目命中)
   └── 记录命中遥测至 recall.jsonl (用于后续分析召回质量)

3. 会话压缩 (compact)
   └── 会话触发上下文截断时，重新触发简报重注入，确保全局认知不丢失

4. 会话结束 (SessionEnd Hook)
   └── 记录会话耗时，从 transcript 中统计工具调用成败与命令表现
```

![一次会话的完整流程：启动注入、每轮召回、会话内写入、收尾，六条泳道](../images/drsg-harness-kit/memory-sharing-flow.svg)

整个会话生命周期清晰划分为：启动注入、每轮召回、会话内写入与收尾。其中遥测（`recall.jsonl`）不论命中与否都会记录一行，这是后续评估召回质量的量化基础；跨项目待办（Event）独立于评分排序，直接由终端提示给人看，避免干扰模型的常规上下文。

### 4.2 跨项目 Event 闭环机制

当我们在仓库 A 完成了某项基础库改造，需要提醒仓库 B 进行适配时，只需写入一条目标为仓库 B 路径的 `Event` 节点：
- 智能体切入仓库 B 开启下一次会话时，`SessionStart` 会在终端界面以 `systemMessage` 形式展现此待办；
- 配合 `events_seen.json` 机制，保证同一条待办在单个会话中仅提示一次，处理完成后原子关闭。

---

## 五、环境部署与使用指引

> **系统要求**：当前仅支持 **Linux** 环境。因为守护进程的健康探测强依赖 `/proc/<pid>/fd` 查找排他锁持有者，这是目前唯一可靠确认 daemon 真实存活的无竞争判定手段。

### 5.1 一键构建与分发

在 `drsg-harness-kit` 源码目录下：

```bash
# 1. 运行打包脚本，生成归档包
./pack.sh
# 生成 dist/drsg-harness-kit-<version>.tar.gz

# 2. 在目标机器解包并执行初始化
tar -xzf dist/drsg-harness-kit-*.tar.gz -C /tmp/
/tmp/drsg-harness-kit-*/setup.sh \
  --project /path/to/my-project \
  --repo /path/to/my-project
```

`setup.sh` 具备完全的幂等性：
- 安装共享 tools 到 `~/.drsg-memory/tools/`；
- 为指定项目复制并配置 `.claude/hooks/` 和 `.drsg/env`（权限 `chmod 600`）；
- 自动注册本地代码图服务至 `.mcp.json` 并执行连通性自检。

![装完之后的样子：项目里只有配置与遥测，daemon 和库全机唯一一份](../images/drsg-harness-kit/memory-sharing-architecture.svg)

从图中清晰可见：**留在项目里的只有 `.drsg/env`（Token 配置，权限 600，已加入 gitignore）、Hooks 脚本和 `.drsg/recall.jsonl`**；而 Daemon 进程与数据库 `memory.drsg` 全机只有一份。因此新增一个项目不会额外增加 Daemon 开销，删除一个项目也绝不会破坏其他项目的持久记忆。

### 5.2 日常健康检查

在遇到任何智能体工具异常或配置变更后，可通过以下三条命令完成快速体检：

```bash
# 1. 检查全局共享记忆层状态 (Daemon 是否运行、端口、DB 文件位置)
~/.drsg-memory/tools/serve.sh status

# 2. 检查特定仓库代码图状态 (同步状态、最新折叠 Commit、规则守护状态)
~/.drsg-memory/tools/codegraph.sh doctor --dir /path/to/repo

# 3. 检查项目 Hooks 与最新模板的一致性 (检测配置漂移)
~/.drsg-memory/tools/install.sh --check
```

---

## 六、总结

在智能体主导的软件研发工作流中，**代码图提供了空间维度的确定性**（精准的结构网络、无遗漏的依赖关系），而**记忆层提供了时间维度的延续性**（跨会话经验沉淀、跨项目任务协同）。

通过 DrSG Harness Kit：
1. 我们让智能体摆脱了在庞大源码库中漫无目的的 `grep` 猜想，直接以图谱结构穿透代码本质；
2. 彻底终结了「新开一个 Session 智能体就把历史坑再踩一遍」的恼人体验；
3. 构建了一个具备自检、幂等、无缝热更新的现代化智能体辅助工程基座。
