# AI 编程下驾驭 Rust 的最佳实践

出发点只有一条：**让 AI 负责写代码，让编译器和工具链负责验证，让人负责定架构和约束。** Rust 的优势要靠一条严格的自动反馈链才能发挥出来，所以大部分实践都在加固这条链。

## 一、核心原则：把约束写进类型，让编译器替你审 AI

这是整套实践里最重要的一条。**你能用类型表达的约束越多，AI 犯错时被编译器当场拦下的概率就越大。**

| 做法 | 例子 | 能拦住 AI 的哪类错误 |
|---|---|---|
| ID 用新类型包装 | `struct UserId(Uuid)`、`struct OrderId(Uuid)` | 参数顺序传反、ID 混用 |
| 解析而不是校验 | `Email::parse(s) -> Result<Email, _>`，内部只接收 `Email` | 忘记校验、重复校验 |
| 状态机用 enum 表达 | `enum Order { Pending{..}, Paid{..}, Shipped{..} }` | 非法状态转换、漏处理某个状态（`match` 必须穷尽） |
| 类型状态（typestate） | `Connection<Unauthed>` → `Connection<Authed>` | 跳过鉴权步骤直接调用 |
| 区分领域错误 | 每个模块一个 `thiserror` 错误 enum | 错误被吞掉、错误类型笼统 |

**架构师的主要工作，就是设计这些类型和 trait 的边界。** AI 往里面填实现。

## 二、工程底座：搭一条又快又严的反馈链

### 1. 统一工具链

```toml
# rust-toolchain.toml：全团队和 CI 用同一个版本，AI 生成的代码行为可复现
[toolchain]
channel = "1.xx.0"          # 锁定具体版本，按季度统一升级
components = ["rustfmt", "clippy"]
```

所有 crate 统一使用 `edition = "2024"`。

### 2. 在 workspace 层面统一 lint，把 AI 常见的坏习惯变成编译错误

```toml
# 根 Cargo.toml
[workspace.lints.rust]
unsafe_code = "forbid"            # 业务代码禁止 unsafe；确实需要的 crate 单独放开并重点审查
missing_docs = "warn"

[workspace.lints.clippy]
unwrap_used = "deny"              # AI 最爱用 unwrap
expect_used = "warn"
panic = "deny"
todo = "deny"                     # 防止 AI 留下 todo!() 就说完成了
dbg_macro = "deny"
await_holding_lock = "deny"       # 持有锁跨越 .await
large_futures = "warn"
clone_on_ref_ptr = "warn"
```

每个成员 crate 加上 `[lints] workspace = true`。测试代码可以通过 `#[cfg(test)]` 局部放开 `unwrap_used`。

### 3. 拆小 crate，压缩编译时间

编译慢会直接拖慢 agent 的循环。

- **按层次拆 workspace：** `domain`（纯逻辑，不含 IO 和 async）、`app`（用例编排）、`infra-*`（数据库、消息、外部 API 适配）、`api`（HTTP/gRPC 入口）、`bin`。
- **AI 改动尽量落在叶子 crate**，增量编译只重编受影响的部分。
- **开发配置：** `[profile.dev] debug = "line-tables-only"`，依赖的 `opt-level` 按需调整；Linux 上用 lld 或 mold 链接（较新的 Rust 在 x86_64 Linux 上已默认使用 lld），配合 sccache 做缓存。
- **日常反馈先跑 `cargo check`**，测试用 `cargo nextest`。

### 4. CI 门禁：AI 写的代码必须全部通过

| 检查 | 工具 | 作用 |
|---|---|---|
| 格式 | `cargo fmt --check` | 不让格式差异进入 review |
| lint | `cargo clippy --all-targets -- -D warnings` | 上面那组 lint |
| 测试 | `cargo nextest run` | 更快，失败信息更清楚 |
| 依赖安全和许可证 | `cargo deny check` | AI 会随手加依赖，必须卡住 |
| 未用依赖 | `cargo machete` | 清理 AI 加了又没用的依赖 |
| 测试质量 | `cargo mutants`（定期或针对改动） | **检验 AI 写的测试是否真的能发现 bug**，防止"测试全绿但什么都没测" |
| unsafe 代码 | `cargo miri test`（针对含 unsafe 的 crate） | 检测未定义行为 |
| 库的 API 兼容 | `cargo semver-checks`（内部共享库） | 防止 AI 无意中破坏接口 |

### 5. 让 agent 在本地就闭环

在 `CLAUDE.md` / `AGENTS.md` 里写死"完成标准"，再用 hook 在每次改动后自动跑 `cargo check`：

```markdown
## 完成标准（缺一不可）
1. `cargo fmt` 无改动
2. `cargo clippy --all-targets -- -D warnings` 通过
3. `cargo nextest run` 通过，新增逻辑有对应测试
4. 不允许用 `#[allow(...)]` 消除警告，除非在注释里说明原因并经人确认
5. 不允许新增依赖，除非在说明中给出理由
```

## 三、架构约束：人来定，写成文档让 AI 遵守

### 1. 锁定技术栈

不锁定的话，AI 会混用功能重叠的库（比如同时引入两个异步运行时、两套错误处理）。一个常见的后端组合：

| 领域 | 选型 |
|---|---|
| 异步运行时 | tokio |
| HTTP | axum + tower / tower-http |
| gRPC | tonic |
| 数据库 | sqlx（编译期检查 SQL）或 SeaORM |
| 序列化 | serde |
| 错误 | 库代码用 thiserror，二进制入口用 anyhow |
| 日志、追踪 | tracing + OpenTelemetry |
| 配置 | figment 或 config |
| HTTP 客户端 | reqwest |
| 测试 | nextest、proptest（属性测试）、insta（快照测试） |

**版本也要锁定并写进文档。** AI 的训练数据混着各个版本的 API。典型例子：axum 0.8 把路由路径参数从 `/:id` 改成了 `/{id}`，AI 经常写出旧语法。要求 AI 以 `Cargo.lock` 里的版本为准，看 docs.rs 或本地 `cargo doc` 的文档，不要凭记忆写。

### 2. 所有权设计的默认规则

AI 在借用检查器面前最容易出的问题是"能编译但设计很差"。默认规则：

- **跨层边界传有所有权的数据**（`String`、`Vec<T>`、自定义结构体），**不要在公开结构体里放带生命周期的引用**；
- **共享状态统一用 `Arc<T>`**，需要可变时用 `Arc<RwLock<T>>`、`Arc<Mutex<T>>`，或者改用 actor 加 channel；
- **禁止为了通过编译到处 `.clone()`**：热路径上的 clone 必须说明理由；
- **禁止用 `Rc<RefCell>` 搭业务对象图**，图结构统一用 arena + slotmap（参见博客文章中图结构一节）；
- **泛型不要超过两层**，能用 enum 就不用 trait object，能用具体类型就不用泛型。AI 喜欢过度抽象，生成的泛型类型很难 review。

### 3. 异步代码的规则

这里是 Rust 后端线上事故的高发区，编译器只能拦住一部分：

- **async 里不做阻塞操作**：CPU 密集或阻塞 IO 放到 `spawn_blocking`；
- **不持有 `std::sync::Mutex` 跨越 `.await`**（上面的 lint 能拦住一部分），需要跨 await 时用 `tokio::sync::Mutex`，或者重新设计；
- **所有外部调用都设超时**：`tokio::time::timeout` 或 tower 的 timeout 层；
- **channel 一律有界**，防止内存无限增长；
- **`tokio::select!` 的每个分支都要考虑取消安全**（cancellation safety），文档里明确哪些函数不是取消安全的；
- **任务生命周期结构化管理**：用 `JoinSet`、`CancellationToken`（tokio-util），不要随手 `tokio::spawn` 了就不管。

### 4. 错误处理

- 每个 crate 定义自己的错误 enum（thiserror），通过 `#[from]` 转换；
- 只在 `api` 层统一把错误映射成 HTTP 状态码和响应体；
- 生产代码路径不允许 `unwrap`、`panic`；panic 只用来表达"程序逻辑上不可能发生"的情况。

## 四、AI 协作流程

### 1. 先定接口，再让 AI 填实现

```
需求 → 人（或 AI 起草、人审核）定义：类型、trait、函数签名、错误 enum
     → AI 实现 + 写测试
     → 工具链闭环（check / clippy / test）
     → 人 review
```

**人 review 的重点是签名和边界，不是每一行实现。** 签名对了，编译器会替你检查大部分实现细节。

### 2. 任务粒度

一次只让 AI 改一个 crate 或一个模块，改动控制在能一次 review 完的范围。粒度越小，编译越快，出错越容易定位。

### 3. AI 在 Rust 里的典型坏习惯，review 时重点看

| 坏习惯 | 表现 | 应对 |
|---|---|---|
| 用 clone 绕过借用检查 | 到处 `.clone()`，包括大对象 | 要求说明理由，或者重新设计所有权 |
| 用 `'static` 或 `Box::leak` 糊弄生命周期 | 为了让 spawn 编译通过，直接泄漏内存 | 禁止 `Box::leak`；改用 `Arc` 或 move 有所有权的数据 |
| 用 `unsafe` 绕过编译器 | "这里我确定安全" | lint 层面 forbid，例外必须由人批准 |
| 消除警告而不是修复 | `#[allow(clippy::...)]`、`let _ = result;` | 规则里禁止，CI 统计 `allow` 的数量 |
| 吞掉错误 | `.ok()`、`unwrap_or_default()` 滥用 | review 时看所有错误路径 |
| 用旧版本 API | 旧的 axum 路由语法、过时的 tokio 写法 | 锁版本，要求查本地文档 |
| 过度抽象 | 三四层泛型、trait 套 trait | 规则里限制泛型层数 |
| 测试只覆盖正常路径 | 测试全绿，但没测错误分支 | 用 cargo-mutants 检验，用 proptest 补边界 |

### 4. 测试策略

AI 写测试几乎没有成本，关键在于**保证测试有效**：

- **单元测试**放在 `domain` 层，纯逻辑，跑得最快；
- **属性测试（proptest）** 用来验证不变量，比如"序列化后再反序列化等于原值"、"金额计算永远不为负"；
- **快照测试（insta）** 用于 API 响应、生成的 SQL 和配置；
- **集成测试**用 `sqlx::test` 或 testcontainers 起真实数据库；
- **变异测试（cargo-mutants）** 定期跑，确认测试真的能发现被篡改的逻辑。

## 五、可观测性：让 AI 排查线上问题有数据可用

AI 排查问题的效果取决于能拿到多少数据。上线前就要建好：

- **日志和追踪：** `tracing` + `tracing-subscriber`，关键函数加 `#[instrument]`，通过 OpenTelemetry 接入 trace 平台；全部使用结构化日志；
- **指标：** `metrics` 或 `prometheus` crate，HTTP 层用 tower 中间件统一埋点；
- **panic：** 设置 panic hook，把 panic 信息和 backtrace 写进日志；
- **异步运行时诊断：** 在预发环境开启 tokio-console，查看任务卡在哪里；
- **性能剖析：** CPU 用 `perf` 加火焰图，或者 pprof-rs；内存用 jemalloc（tikv-jemallocator）的堆剖析功能；
- **把这些数据的查询入口提供给 AI**：日志查询、trace 查询、指标查询都通过 MCP 或 CLI 工具暴露出来，AI 排查时能直接拿数据，而不是靠猜。

## 六、架构师自己的学习路线

**目标不是写得比 AI 快，而是能设计边界、能判断 AI 写的代码对不对。** 详细的执行计划见 [architect-learning-plan.md](architect-learning-plan.md)。

| 阶段 | 内容 | 资料 |
|---|---|---|
| 基础 | 所有权、借用、生命周期、trait、错误处理 | 《The Rust Programming Language》 |
| 进阶 | trait 设计、泛型与 trait object 的取舍、API 设计、unsafe 的边界 | 《Rust for Rustaceans》 |
| 并发 | 原子操作、内存序、锁的实现 | 《Rust Atomics and Locks》（Mara Bos） |
| 异步 | Future、Pin、Send/Sync、tokio 运行时模型、取消安全 | tokio 官方教程、《Asynchronous Programming in Rust》 |
| 后端实战 | 完整后端服务的工程化：测试、追踪、部署 | 《Zero To Production in Rust》 |
| 所有权的极限 | 链表和图结构为什么难，怎么解决 | 《Learn Rust With Entirely Too Many Linked Lists》 |

## 七、团队落地路线

| 阶段 | 时间 | 内容 |
|---|---|---|
| 底座 | 第 1 个月 | 建一个模板仓库：workspace 结构、lint 配置、CI 门禁、`CLAUDE.md`、可观测性接入。之后所有新服务都从模板开始 |
| 试点 | 第 2～3 个月 | 选 1～2 个新的非核心服务，完全按这套实践开发 |
| 推广 | 第 4～6 个月 | 根据试点数据修订规范，推广到所有新服务；存量服务遇到重构时再迁移 |

**团队分工：**

- **所有人**都要能**读懂** Rust 并 review，不要求都能熟练手写；
- **少数核心成员**负责 unsafe 代码、性能关键路径、底层公共库，以及维护模板和规范。

**试点期要量化的指标：**

- AI 首次提交就能编译通过的比例，以及达到全部检查通过平均需要几轮；
- 增量编译时间、CI 总时长；
- review 平均耗时；
- 上线后的缺陷数和事故数，与原技术栈对比。

用数据判断这套实践要怎么调整，而不是凭感觉。
