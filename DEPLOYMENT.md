# 本地部署

## 支持平台

统一安装入口 `bash scripts/setup-pptagent.sh` 会自动分派到 Linux 或 macOS 安装脚本。`bin/pptagent`、`bin/libreoffice`、`bin/render-illustration`、`bin/agentdraw` 和 `bin/opendiagram` 使用相同的平台选择器。

| 项目 | Linux / WSL | macOS Apple Silicon |
| --- | --- | --- |
| 原生运行依赖 | `.runtime/linux-x86_64/`，ARM 为 `linux-arm64/` | `.runtime/macos-arm64/` |
| Python 虚拟环境 | 各平台目录下的 `venv/` | 各平台目录下的 `venv/` |
| PPT Node 依赖 | 各平台目录下的 `pptagent-node/node_modules/` | 同左，物理目录分开 |
| 浏览器 | Playwright Chromium | Playwright Chromium |
| LibreOffice | 系统 `libreoffice`，可设 `PPTAGENT_LIBREOFFICE` | 项目内应用或已安装应用 |
| 中文回退字体 | Noto Sans CJK SC / WenQuanYi Zen Hei | Heiti SC |

源文件、依赖锁文件和技能可以共用；虚拟环境、Node 依赖、浏览器和应用二进制不能跨平台复制。所有本地依赖和生成物均由 `.gitignore` 排除。

## 环境要求

- Python 3.12、uv、Node.js 和 npm。
- LibreOffice，用于实际 PPTX 导出与渲染检查。
- Linux 建议使用 Noto CJK 或文泉驿中文字体。
- macOS 使用 Apple Silicon 时，按安装脚本准备对应的 Chromium 和 LibreOffice。

Debian / Ubuntu 的系统组件示例：

```bash
sudo apt-get install libreoffice fontconfig fonts-noto-cjk
```

## 安装与检查

```bash
bash scripts/setup-pptagent.sh
bash scripts/setup-illustrations.sh
bash scripts/setup-opendiagram.sh
./bin/pptagent doctor --workspace "$PWD"
./bin/agentdraw doctor --json
./bin/opendiagram doctor
```

安装只在项目内写入运行依赖，不要求修改全局 Agent 配置。密钥放在环境变量或本地 `.env` 中，不写入演示稿、日志或交付文件。

## 在 Codex 和 Kimi Code 中使用

从仓库根目录启动编码工具，两者共用 `.agents/skills/` 下的技能。新安装或重命名 Skill 后，重新打开项目会话以刷新技能目录。

Codex 示例：

```text
$pptagent 请制作一份 8 页中文项目答辩 PPT，输出到 outputs/presentation/，逐页检查后交付可编辑 PPTX。
```

Kimi Code CLI 示例：

```text
/skill:pptagent 请制作一份 8 页中文项目答辩 PPT，输出到 outputs/presentation/，逐页检查后交付可编辑 PPTX。
```

如需默认的简洁商业风格，同时使用 `concise-business-ppt-style`：

```text
使用 pptagent 和 concise-business-ppt-style，制作一份 8 页中文项目答辩 PPT。
```

## 本地命令

创建任务并生成初始 HTML：

```bash
./bin/pptagent init --workspace "$PWD/outputs/presentation" --slides 8 --language zh
./bin/pptagent scaffold --workspace "$PWD/outputs/presentation"
```

助手编辑 HTML 后，按 PPTAgent Skill 执行 `review-slides`、逐页查看并记录检查、`build`、`review-deck`、记录导出检查和 `finalize`。最终以 `final-report.json` 的 `complete=true` 作为交付依据。

从其他任务目录调用时，使用本项目 `bin/pptagent` 的绝对路径，并传入任务目录的绝对路径。

## 验证

```bash
./bin/pptagent doctor --workspace "$PWD"
source scripts/runtime-env.sh
"$PPTAGENT_PYTHON" -m pytest tests .agents/skills/pptagent/tests
```

`runtime-env.sh` 会按当前操作系统和 CPU 架构选择运行环境，并设置浏览器与 Node 依赖路径。标准验收包括：

- PPTAgent doctor 全部通过。
- HTML 渲染、逐页视觉检查、可编辑 PPTX 构建和实际导出检查通过。
- 中文 glyphs、字体回退、换行、遮挡和页码均经过检查。
- 运行环境与连接器测试通过。
- 生成物保存在本地 `outputs/`，不作为开源仓库的必备文件提交。

## 上游来源

PPTAgent Skill 来源于 [icip-cas/PPTAgent](https://github.com/icip-cas/PPTAgent)，基准提交为 `833cda553b343be0e486a93b0b57cac962cdd566`。本仓库增加平台启动器、依赖隔离和简洁商业风格配套规则；上游许可证保留在 `.agents/skills/pptagent/LICENSE`。
