---
title: AI 时代的编程语言选型：Rust 是 AI 原生的语言
date: 2026-10-25 22:00:00
categories: 架构
tags:
  - Rust
  - AI 编程
  - 技术选型
---

AI 写代码以后，"难学、难写、难读"这些语言之间的差距大多被抹平了，选型时剩下的主要是语言本身的技术取舍。按这个标准，Rust 最接近一门"AI 原生"的语言：新的后端服务、基础设施和工具基本可以直接选它，历史包袱随时间逐步解决。

<!-- more -->

## 起点：一张对比图

网上流传一张对比 Python、Go、C++、Rust 的图，比了四项：

| | Python | Go | C++ | Rust |
|---|---|---|---|---|
| 速度 | 最慢 | 很快 | 最快 | 最快 |
| 内存安全 | 安全（靠 GC） | 安全（靠 GC） | 靠人小心 | 安全（编译器挡错） |
| 回收时停顿 | 会停一下 | 会停一下 | 不会停 | 不会停（没有 GC） |
| 多线程 | 写得出来 | 很好写 | 容易出错 | 编译器先挡数据竞争 |

这张图挑的维度对 Rust 有利。对后端来说，有几处要打折扣：

- 大多数后端是 IO 密集型，瓶颈在数据库和网络，Go 和 Rust 的速度差别通常感受不到。
- Go 从 1.5 起改为并发 GC，Go 团队 2016 年就把典型的最坏 STW 停顿降到了 100 微秒以内，绝大多数服务不在乎这点停顿（超大堆的场景另说）。
- Rust 编译器挡住的是**数据竞争**，挡不住死锁、逻辑竞态和分布式一致性问题。

图里也没列编译速度、生态成熟度、招人成本这些维度。过去 Rust 最大的问题是**难**：学习曲线陡，写起来慢，读别人的代码费劲。AI 编程时代，这一点变了。

## AI 把"工作量问题"抹平了

以前反对全面使用 Rust 的理由，大部分其实是人力成本：

| 过去的顾虑 | AI 时代 |
|---|---|
| Rust 难学、难写 | AI 来写 |
| 生命周期、复杂泛型难读 | AI 来读、来解释 |
| 线上出问题，人看不懂代码 | AI 参与排查 |
| 缺少某个 SDK 或工具 | 让 AI 用 Rust 补一个 |
| 存量系统重写成本高 | 成本大幅降低 |

这些都是工作量，不是技术约束。工作量被抹平以后，选型时剩下的就是语言本身的技术取舍。

## 为什么说 Rust 是 AI 原生的语言

AI 写代码最大的问题不是写不出来，而是**写错了自己不知道**。Rust 正好补上这一点：

1. **编译器是严格的自动验证器。** 空指针、释放后使用、数据竞争这一大类错误在编译期就暴露。agent 可以自己"改代码→编译→再改"，直到通过，不用等到线上才发现。
2. **类型和所有权把意图写进了代码。** 谁拥有数据、谁能修改、能不能跨线程，都写在类型里。AI 读代码时信息更完整，少靠猜。
3. **最大的缺点正好被 AI 抵消。** 人觉得难，机器觉得清楚。

AI 写的代码越多，"机器能不能证明代码是对的"就比"人写起来顺不顺手"越重要。Rust 是目前在实用性和编译期保证之间平衡得最好的语言。

## 一个常见疑问：复杂图结构怎么办

一个经常被拿来反对 Rust 的场景是复杂的图结构：有环、共享、可变，例如编译器、GUI 组件树、游戏场景。Rust 的所有权规则（单一所有者；共享和可变不能同时存在）和图结构天生冲突，常见的写法有三种：

- `Rc<RefCell<T>>`：引用计数，借用检查推迟到运行时；
- arena + 整数索引：rustc、rust-analyzer、petgraph、Bevy ECS 都是这么做的；
- `unsafe` 裸指针，或者引入 GC 库。

**性能上，Rust 并不吃亏。** `Rc` 的计数加减和 `RefCell` 的标记检查都很便宜；GC 语言也有写屏障、GC 周期、额外的内存占用。arena 写法内存连续、没有 GC，通常比 GC 语言更快。

**代价在于，用最简单的写法时，一部分编译期保证会退化成运行时检查。** 编译器看不清图里的引用关系：`RefCell` 的借用冲突要到运行时才 panic；arena 的索引对编译器来说只是一个整数：

```rust
let id = graph.add_node(a);   // id = 3
graph.remove_node(id);
graph.add_node(b);            // 新节点复用了位置 3
graph.nodes[id].value         // 编译通过，读到的是 b，不报错
```

但这部分保证**大多可以补回来**，代价是代码更复杂。过去人不愿意写，现在正好交给 AI：

- **类型化索引：** 每个图的索引用不同的新类型，拿 A 图的索引去查 B 图会编译报错；
- **带代数的索引（slotmap）：** 节点删掉以后，旧索引能在运行时稳定地被检查出来，不会再静默读到错误的节点；
- **GhostCell / qcell 等令牌技巧：** 用一个编译期令牌控制整个图的读写权限，把借用冲突重新变回编译错误，而且没有运行时开销；
- **Miri、模糊测试、属性测试：** 把剩下的问题尽量提前暴露。

剩下两类问题确实无法在编译期解决：**节点删除后的旧引用失效**，以及**环导致的内存泄漏**。但它们**在其他主流语言里同样没有在编译期解决**：

| 问题 | C / C++ | Java / Go / Python | Swift（ARC） | Rust |
|---|---|---|---|---|
| 删除后的旧引用 | 悬垂指针，内存损坏 | 对象被拉住不回收，静默读到旧数据 | 同左 | slotmap 能在运行时检查出来 |
| 环导致内存泄漏 | 手动管理 | 追踪式 GC 在运行时回收 | 会泄漏，要手动用 `weak` 打断 | `Rc` 写法会泄漏；arena 写法整体释放，不存在这个问题 |

"节点在业务上已被删除"是运行时状态，编译器无法静态判断。真正能在编译期证明这类性质的，只有 Idris、Lean 这类依赖类型或定理证明语言，离工程实用还很远。GC 语言也有自己的"逻辑泄漏"：对象被全局 map、缓存或事件监听器挂着，GC 照样回收不了。

所以在图结构场景里：

- **和 Rust 自己平时比：** 需要更复杂的写法，才能把编译期保证补回来；
- **和其他语言比：** Rust 没有劣势。性能通常更好，删除后的旧引用能被检查出来，用 arena 也不存在环泄漏。

这类场景同样可以直接选 Rust，只是不要停在最简单的 `Rc<RefCell>` 写法上。

## 趋势已经在发生

用 Rust 写新一代软件、逐步替换老软件，已经不只是设想：

- **开发者工具：** 很多原本用 JS、Python 写的工具，正在被用 Rust 写的新工具替代。
  - Python 生态：Astral 的 uv（包和项目管理，可替代 pip、pip-tools、pipx、poetry、pyenv 等）和 ruff（linter + formatter）；
  - 前端生态：字节跳动的 Rspack（兼容 webpack 的打包器）、Vercel 的 Turbopack（Next.js 内置的增量打包器）、Biome（Rome 的官方分支，覆盖格式化和 lint）。
- **Linux 内核：** 2023 年 12 月首批 Rust 驱动被合入，随 6.8 版本发布；2025 年 12 月的维护者峰会上，Rust 正式去掉了"实验性"标签。不过目前体量还很小：2025 年 4 月内核约有 3400 万行 C 代码，Rust 只有约 2.5 万行。
- **Android：** 据 Google 公布的数据，内存安全漏洞在 Android 全部漏洞中的占比，从 2019 年的 76% 降到 2024 年的 24%，2025 年首次低于 20%；Rust 代码的内存安全漏洞密度比 Android 的 C/C++ 代码低约 1000 倍。Android 16 中基于 6.12 内核的设备已经带上了用 Rust 写的 ashmem 驱动。
- **Windows：** 微软已把部分内核代码用 Rust 重写，Windows 11 中出现了 Rust 写的内核组件 `win32kbase_rs.sys`。但微软也明确表示，没有把整个 Windows 用 Rust 重写的计划。

这些例子的共同点是：新组件、安全敏感的组件优先用 Rust，存量代码逐步替换，而不是一次性全部重写。

AI 会加快这个过程，因为重写最大的成本（人力和理解旧代码）正在变便宜。Rust 本身也在演进，持续吸收其他语言的优点。

## 选型建议

**默认选 Rust：**

- 新的后端服务；
- 基础设施：网关、代理、消息和流处理、存储组件；
- 命令行工具、开发者工具；
- 对性能、延迟、内存敏感的组件。

**按平台和生态选：**

- 浏览器前端：JS/TS（Rust 可以通过 WASM 进入，但涉及 DOM 的部分绕不开 JS）；
- iOS / Android 原生 UI：Swift / Kotlin；
- 模型训练和数据探索：Python（推理服务和底层算子可以用 Rust）。

**存量系统：**

- 不为重写而重写；
- 遇到性能瓶颈、安全问题或大版本重构时，顺势换成 Rust。

**工程上要注意的：**

- 大型 Rust 项目编译慢，会拖慢 agent 的迭代循环。可以拆小 crate、配置增量编译、换更快的链接器；
- 线上可观测性提前建设：`tracing`、metrics、tokio-console 等。

## 小结

AI 编程时代，语言之间"好不好写"的差距基本被抹平，剩下的是技术取舍。在这些取舍里，Rust 用编译器替 AI 兜底，最适合"AI 写、机器验证"的开发方式。除了平台和生态绑定的领域，新项目基本可以直接选 Rust；历史包袱，交给时间和 AI 慢慢消化。

更长远看，真正在收敛的是一种开发方式：让机器尽可能多地证明代码是对的。Rust 是这个方向目前最成熟的代表。

## 参考资料

- Google 安全博客：[Memory Safe Languages in Android 13](https://security.googleblog.com/2022/12/memory-safe-languages-in-android-13.html)（2022）
- Google 安全博客：[Eliminating Memory Safety Vulnerabilities at the Source](https://security.googleblog.com/2024/09/eliminating-memory-safety-vulnerabilities-Android.html)（2024）
- Google 安全博客：[Rust in Android: move fast and fix things](https://security.googleblog.com/2025/11/rust-in-android-move-fast-fix-things.html)（2025）
- Wikipedia：[Rust for Linux](https://en.wikipedia.org/wiki/Rust_for_Linux)
- DevClass：[Rust boosted by permanent adoption for Linux kernel code](https://devclass.com/2025/12/15/rust-boosted-by-permanent-adoption-for-linux-kernel-code/)（2025）
- Thurrott：[First Rust Code Shows Up in the Windows 11 Kernel](https://www.thurrott.com/windows/windows-11/282995/first-rust-code-shows-up-in-the-windows-11-kernel)
- The New Stack：[Microsoft's Rust Bet: From Blue Screens to Safer Code](https://thenewstack.io/microsofts-rust-bet-from-blue-screens-to-safer-code/)
- Astral：[uv 文档](https://docs.astral.sh/uv/)、[uv: Python packaging in Rust](https://astral.sh/blog/uv)
- Rspack：[Introduction](https://rspack.rs/guide/start/introduction)
- Next.js：[Turbopack](https://nextjs.org/docs/app/api-reference/turbopack)
- Biome：[官网](https://biomejs.dev/)、[Announcing Biome](https://biomejs.dev/blog/announcing-biome/)
- golang-dev：[Sub-millisecond GC pauses](https://groups.google.com/g/golang-dev/c/Ab1sFeoZg_8/m/_DaL0E8fAwAJ)（2016）
