# maidol 的博客

基于 [Hexo](https://hexo.io/) 3.x 的个人技术博客，主题为 [yilia](https://github.com/litten/hexo-theme-yilia)，部署在 GitHub Pages：<http://maidol.github.io/>。

## 目录结构

```text
.
├── _config.yml        # 站点配置
├── scaffolds/         # 新建文章 / 草稿 / 页面的模板
├── source/
│   ├── _posts/        # 已发布的文章
│   └── _drafts/       # 草稿（不会生成到站点）
└── themes/yilia/      # 主题
```

## 常用命令

```bash
npm install -g hexo-cli   # 全局安装 Hexo 命令行工具
npm install               # 安装依赖

hexo new "文章标题"        # 新建文章
hexo new draft "草稿标题"  # 新建草稿
hexo publish <草稿文件名>  # 发布草稿
hexo server               # 本地预览 http://localhost:4000
hexo clean && hexo generate && hexo deploy   # 生成并部署
```

## 写作约定

- **front matter**：`title` 用中文描述性标题；`date` 用 `YYYY-MM-DD HH:mm:ss` 格式；`tags` 用列表，**只能用空格缩进，不能用 Tab**（YAML 不允许用 Tab 缩进）。
- **摘要**：正文开头写一两句摘要，后面加 `<!-- more -->`，首页只显示摘要。
- **标题层级**：正文从 `##` 开始，按 `##` → `###` → `####` 依次使用，不要跳级。
- **代码**：命令和配置放进带语言标识的代码块（```` ```bash ````、```` ```yaml ```` 等），行内的命令、路径、参数用反引号包起来。
- **提示**：注意事项、过时说明用 `> **注意**：...` 形式的引用块。
- **敏感信息**：真实的 IP、密码、token 一律用 `your_server_ip`、`yourpassword` 这样的占位符代替。
