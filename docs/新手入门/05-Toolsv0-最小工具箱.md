# 05. Tools v0：最小工具箱（读 / 查 / 列）

你想让 Agent 真的“懂仓库”，靠的不是聪明回答，而是**能自己去看**。

Tools v0 的目标很清楚：给它一套最小工具，让它能完成基本探索。少而稳。

---

## 本章目标（验收标准）

完成下面这条，就算通过：

- 它能用工具回答两个问题：
  - 项目入口在哪？
  - 测试怎么跑？

这里的“回答”不是嘴上说说，而是你能看到：它先查，再读，再总结。

---

## 你需要的两块关键模块

### 1) Tool Registry：工具注册表（schema + handler）

你要解决的是“如何把工具交给模型理解”。最常见的做法是：
- 每个工具提供一个 JSON Schema（函数名、描述、参数）
- 运行时把这些 schema 传给模型
- 模型返回结构化调用（函数名 + 参数）

如果没有 registry，你后面会很快陷入一堆 if/else 分发。

### 2) Tool Result 标准化：统一返回结构

这是本章最重要的工程约束。

不管工具是读文件、列目录还是搜索字符串，返回结构都要统一。建议最少包含：
- `stdout`
- `stderr`
- `exit_code`
- `changed_files`

为什么要这么做：
- 模型需要稳定信号判断成功/失败（exit_code）
- 你需要知道“动了哪些文件”（changed_files）
- 你需要调试工具失败原因（stderr）

少写一点“聪明 prompt”，多写一点“稳定结构”，你会省很多时间。

---

## Tools v0 应该包含哪些能力（建议清单）

v0 版本先做只读：
- `ListDir`：列目录
- `ReadFile`：读文件（带截断）
- `Grep`：搜索关键词
- `Glob`：按模式找文件

这些工具组合起来，基本就能回答“入口在哪、测试怎么跑”。

注意：v0 不建议上来就做写文件、跑命令。那属于下一章的事情。

---

## 一个现实的“回答路径”长什么样

以“项目入口在哪？”为例，一个靠谱的路径通常是：

1. ListDir 看根目录
2. ReadFile 读 README / pyproject / package.json
3. Grep 搜关键字（比如 main、entry、cli、__main__）
4. ReadFile 打开入口文件
5. 总结：入口在哪里、怎么启动

如果你的 Agent 能走出这种路径，它就不是靠猜了。

---

## 本章验收脚本（直接复制）

把下面两条丢给你的 CLI：

### 验收 1：入口定位

```text
请只基于仓库真实内容回答：项目入口在哪？
要求：先用工具探索，再给结论。
```

### 验收 2：测试命令

```text
请只基于仓库真实内容回答：测试怎么跑？
要求：先用工具探索，再给结论。
```

验收要看什么：
- 它真的调用了 read/list/grep/glob
- 它的结论能指向具体文件（比如 README、配置文件、脚本入口）

---

## 参考阅读

1. OpenAI：Function calling / Tools（JSON schema 定义函数与参数）
   `https://platform.openai.com/docs/guides/function-calling`
2. Anthropic：Tool use overview（tools 的输入输出与回填流程）
   `https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview`
3. OpenCode：Tools / Permissions / Instructions（工具边界与权限体系）
   `https://opencode.ai/docs`

> 注：OpenCode 的权限体系之所以能工作，前提就是工具边界清晰、工具结果可被稳定消费。
