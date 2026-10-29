# PPTAgent · 简洁商业风格 Skills

一套面向中文技术汇报、项目答辩和商业演示的本地 Skills 与工作流。仓库只保留通用技能、风格规则和运行工具，不包含个人 PPT、个人资料或具体项目数据。

## 来源与定位

本项目的 PPTAgent 来源于 [icip-cas/PPTAgent](https://github.com/icip-cas/PPTAgent) 的 Skill 版本，上游基准提交为 [`833cda553b343be0e486a93b0b57cac962cdd566`](https://github.com/icip-cas/PPTAgent/tree/833cda553b343be0e486a93b0b57cac962cdd566/skills/pptagent)。它不是上游官方发行版，也不是另起一个 PPT 生成模型，而是在上游能力之上做了两类特化：

- **本地工作流特化**：统一 Linux / macOS 启动入口，隔离不同平台的运行依赖，保留 HTML 源稿、可编辑 PPTX、逐页渲染检查、导出复查和 finalize 验收流程。
- **简洁商业风格特化**：通过配套的 `concise-business-ppt-style` skill，将默认设计收敛为白底深蓝、单行摘要标题、少量字号层级、规整对齐和真实证据图，减少宣传式口号与装饰。

上游 PPTAgent 的原始说明和 MIT 许可证保留在 [`.agents/skills/pptagent/`](.agents/skills/pptagent/)。其他第三方技能的许可证与说明位于各自目录。

## 风格特点

- 白底、深蓝标题、浅灰蓝说明栏和细分隔线。
- 中文微软雅黑，英文与数字 Times New Roman；每页通常只有两到三个字号层级。
- 标题直接写清对象、动作或结果，不堆口号和副标题。
- 机制用流程图，结果用真实曲线、表格、云图或代码，不用插画填充空白。
- 保留数据口径、个人贡献边界和实验限制，不为了版面整齐删减关键条件。
- 主线简洁，公式、代码和补充实验放入技术备份。

完整规则见 [简洁商业风格 skill](.agents/skills/concise-business-ppt-style/SKILL.md) 和 [版式参考](.agents/skills/concise-business-ppt-style/references/style-reference.md)。

## 快速开始

环境要求与依赖重建见 [DEPLOYMENT.md](DEPLOYMENT.md)。

```bash
bash scripts/setup-pptagent.sh
./bin/pptagent doctor --workspace "$PWD"
```

创建一个 8 页中文任务：

```bash
./bin/pptagent init --workspace "$PWD/outputs/presentation" --slides 8 --language zh
./bin/pptagent scaffold --workspace "$PWD/outputs/presentation"
```

随后由宿主 Agent 编辑 HTML，执行逐页检查、构建、导出复查和 finalize。也可以直接对编码助手说：

```text
使用 pptagent 和 concise-business-ppt-style，制作一份 8 页中文项目答辩 PPT。
```

## 仓库结构

```text
.agents/skills/pptagent/                 上游 PPTAgent Skill 与本地工作流
.agents/skills/concise-business-ppt-style/ 简洁商业风格规则
.agents/skills/humanizer-zh/             中文文案自然化复核
.agents/skills/agentdraw/                可编辑视觉图解
.agents/skills/opendiagram/              架构、流程、时序和 ER 图
.agents/skills/colorfigures/             交互式机制插画
.agents/skills/comfyui/                  ComfyUI 图像生成连接
.agents/skills/paper2any/                Paper2Any 工作流连接
.agents/skills/agent-reach/              只读内容检索
bin/                                   跨平台统一启动入口
scripts/                               通用安装、运行和绘图脚本
tests/                                 运行环境与连接器测试
```

绘图能力的用途和配置方法见 [ILLUSTRATIONS.md](ILLUSTRATIONS.md)。运行依赖、生成稿、密钥和本地输出不进入版本控制。
