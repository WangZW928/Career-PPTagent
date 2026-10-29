# 绘图 Skills

这些 Skill 与 PPTAgent 一样，放在项目 `.agents/skills/`，供从本项目启动的 Codex 和 Kimi Code 共用。

| Skill | 适合的任务 | 当前状态 |
| --- | --- | --- |
| `colorfigures` | 手绘等距物体、机器原理、可旋转和可操作的 HTML 插图 | 作者官方 Skill 已保留；Linux HTML 构建和 PNG 导出已验证 |
| `agentdraw` | 流程图、架构图、机制图和可编辑说明图 | 官方 Skill 已保留；Linux CLI `0.1.28` 已恢复，可编辑画板、SVG 和 PNG 导出已验证 |
| `paper2any` | 论文生成科研图、技术路线图和幻灯片 | 本项目接入 Skill 已安装；待配置 Paper2Any 后端和模型 |
| `opendiagram` | 架构图、流程图、时序图、ER 图 | 项目接入 skill；固定版本本地引擎，Linux Excalidraw / SVG / PNG 导出已验证 |
| `comfyui` | 使用节点工作流生成或处理配图 | 本项目接入 Skill 已安装；待配置 ComfyUI 服务和模型 |

Paper2Any、ComfyUI 目前提供接入层，尚未部署后端或下载模型；未对真实模型执行生图验证。
接入层的鉴权、JSON 请求、二进制下载、重定向处理与失败时不重复提交，已用本机测试服务验证。

## 调用

下一轮可加载新增 Skill；未发现时，重新打开项目会话。

| 工具 | 示例 |
| --- | --- |
| Codex | `$colorfigures`、`$agentdraw`、`$paper2any`、`$opendiagram`、`$comfyui` |
| Kimi Code | `/skill:colorfigures`、`/skill:agentdraw`、`/skill:paper2any`、`/skill:opendiagram`、`/skill:comfyui` |

可以直接描述任务，例如“用 AgentDraw 画一张系统架构图，导出 SVG 和 PNG，放入 PPT 素材目录”。
整份 PPT 仍使用 `pptagent`；绘图 Skill 生成单张插图和可复用素材。

## 插图放入 PPT

AgentDraw 先保留 `.agentdraw.json` 可编辑画板，再导出 SVG 或 PNG：

```bash
./bin/agentdraw export outputs/figures/board.agentdraw.json --format png --scale 2 --out outputs/figures/board.png --json
```

Colorfigures 先生成独立 HTML，再捕获指定角度的 PNG。使用已经安装的项目 Chromium：

```bash
./bin/render-illustration outputs/figures/object.html --out outputs/figures/object.png --width 900 --height 800 --scale 2 --selector '#fig' --query 'free=1&yaw=45' --hide-selector '.actions,.vset,.zchip,.ctl,.stats,.toast,.kpad,.lgd'
```

`--query` 可选择角度、剖视或交互状态；需要显示内部结构时可追加 `xr=1&labels=1`。
捕获命令仅加载本地 HTML/SVG 和内联资源，外部资源需先保存到本地。
复制选中的素材到 PPT 任务自己的 `assets/` 目录，并使用相对路径。
保留 HTML / SVG / 画板作为源文件。PNG 在 PPT 中是静态图片；Colorfigures 的交互保留在 HTML 中。

## 首次连接 Paper2Any / ComfyUI

将 `illustration-services.env.example` 复制为 `.env.illustrations`，填写实际服务地址和所需凭据。
已有的同名 shell 环境变量优先。真实配置文件已被 Git 忽略。

```bash
./bin/illustration-services paper2any doctor
./bin/illustration-services comfyui doctor
```

未填写地址时返回 `status: not_configured` 和退出码 `2`；这表示服务待配置。
连通后，`api_available` 仅表示 API 可访问。模型是否就绪需在实际运行工作流时验证。

Paper2Any 接入目标是 OpenDCAI 的开源 FastAPI 版本；其当前托管后继产品 Nexus Office 使用另一套实现。
通过 `/openapi.json` 读取实际端点和字段后再发任务，避免硬编码过期 API。
接入工具支持 JSON 请求与二进制下载；multipart 上传或 SSE 流应按服务 schema 另选对应客户端。

ComfyUI 接入目标是自托管 API，地址通常形如 `http://127.0.0.1:8188`。
先查询 `/object_info` 和可用模型，使用导出的 API 格式工作流，再提交 `/prompt`，查询 `/history/{prompt_id}`，从 `/view` 下载完成的图片。
Comfy Cloud 的接入按其独立官方 API 配置。

## 安装来源和依赖重建

- Colorfigures：作者 [April Zhu 官网](https://april-zhu.com/colorfigures) 的 [官方安装包](https://april-zhu.com/colorfigures/colorfigures.zip)，保留 MIT 许可证。下载包 SHA-256：`bb4d0116f1b0647cde5a492fdf6d54e03c769b02ef12dcf564f697cce411253a`。本地缩短了发现描述，并补充项目浏览器和 PPT 导出说明。
- AgentDraw：[官方仓库](https://github.com/agentdraw/agentdraw/tree/main/skills/agentdraw) 的 Skill 与 npm `@aidraw/agentdraw@0.1.28`，保留 MIT 许可证。本地补充项目 CLI 路径。
- Paper2Any 接入依据：[官方项目](https://github.com/OpenDCAI/Paper2Any) 的后端及其部署时提供的 OpenAPI schema。
- ComfyUI 接入依据：[官方服务 API 路由](https://docs.comfy.org/development/comfyui-server/comms_routes)。

恢复 AgentDraw 本地命令行依赖：

```bash
./scripts/setup-illustrations.sh
```

依赖版本由 `tools/illustrations/package-lock.json` 锁定，按平台安装到 `.runtime/<平台>/illustrations/`。
PNG 捕获复用 PPTAgent 的 Python 和 Chromium；它们的恢复方法见 `DEPLOYMENT.md`。
各平台的渲染检查文件统一放在本地 `outputs/` 中，不随 Git 保存；公开仓库不依赖这些临时验证产物。

## OpenDiagram 本地绘图引擎

来源：[Itz-Agasta/OpenDiagram](https://github.com/Itz-Agasta/OpenDiagram)，固定提交见 `tools/opendiagram/source.json`，上游许可证保留在运行目录。此处的 `opendiagram` skill 是项目自编适配说明，并非上游官方 skill。

安装：`bash scripts/setup-opendiagram.sh`。已有 Colorfigures / AgentDraw / Paper2Any skill 予以保留，不覆盖其官方正文或现有配置。

```bash
./bin/opendiagram render .agents/skills/opendiagram/references/spec-example.json --out outputs/figures/optimization-flow
```

输出 `.spec.json`、`.excalidraw`、`.svg`、`.png` 和含警告的 `.report.json`。语义 JSON 由当前助手编写，布局和绘制使用上游引擎；浏览器导出使用上游的 Excalidraw 转换方法。支持 `--theme classic` / `sketch`。本地模式没有云图标包，需省略 `icon` 字段。

PPT 使用 SVG/PNG；编辑保留 Excalidraw 和语义源。完整 OpenDiagram 网站的账号、数据库、AI 聊天功能不属于本地引擎安装，未部署。

## 跨平台使用

所有 `bin/` 入口自动识别 Linux/macOS 和 CPU 架构，图形渲染共用当前平台的 PPTAgent Chromium。安装步骤见 `DEPLOYMENT.md`。Colorfigures 的 HTML 构建仅需 Python 标准库；PNG 导出需要浏览器。Paper2Any 连接器的 `not_configured` 表示 skill 已安装但后端未连接，不等于生图测试通过。

OpenDiagram 适配层使用 Node.js 与 ELK 自带的进程内 Worker，适配上游原本依赖 Bun Worker 的代码；不修改上游布局实现。浏览器字体从本地依赖读取。
