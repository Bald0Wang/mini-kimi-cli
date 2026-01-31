# 07. Todo List：把计划变成“可追踪任务”

如果你只让 Agent“说计划”，你很快会遇到一个问题：

它说得头头是道，但你不知道它现在做到哪一步了。

Todo List 解决的就是这件事。它把计划从一段文字，变成一个**可以更新、可以查看、可以回放的状态**。

---

## 本章目标（验收标准）

完成下面两条，就算通过：

1. Agent 会把计划写成 todo，并在执行过程中持续更新状态。
2. 用户能用 `/todo` 随时看到它当前在做什么。

你会明显感受到：可控感变强了。

---

## Todo 在系统里扮演什么角色

把 todo 当成一个“可视化心智模型”比较准确：
- 它告诉用户：Agent 认为什么是步骤
- 它告诉系统：Agent 现在做到哪
- 它也能约束 Agent：别随便跳步、别忘了收尾

这类“可追踪计划”已经是很多工程型 agent 的常见组件。

---

## 关键模块：两件事就够用

### 1) Todo store（持久化）

v0 版本你可以先用 json 文件或 jsonl：
- 写起来简单
- 人眼可读

等你需要更复杂的查询，再迁移到 sqlite。

关键要求只有一个：
- 重启后 todo 还能在

### 2) todo tools（todoread / todowrite）

你的工具接口建议尽量小：
- `todoread`：读当前 todo 列表
- `todowrite`：写入/更新 todo（新增、改状态、补 notes）

把它做成工具而不是“内置字符串输出”，有两个好处：
- 记录可审计（工具调用有日志）
- 便于权限控制（后面做权限系统会更顺）

---

## Todo 数据结构（最小但够用）

建议最少包含四个字段：
- `id`
- `title`
- `status`：todo / doing / done / blocked
- `notes`

一个例子：

```json
{
  "id": "T-001",
  "title": "定位入口文件并解释启动流程",
  "status": "doing",
  "notes": "已找到 main.py，下一步读 soul.py"
}
```

你不需要一次设计成 Jira。先保证这四个字段全程能跑通。

---

## 状态更新的规则（别让 todo 变成摆设）

Todo 有效的前提是：它必须跟着 loop 动。

建议你定两条硬规则：

1) 每次进入新步骤前，先把对应 todo 标记为 `doing`
2) 每次工具执行后，如果产生了新观察，就把 notes 更新一下

这样用户看 `/todo` 的时候，能读到“正在干什么 + 为什么这么干”。

---

## 本章验收脚本（直接复制）

### 验收 1：生成 todo 并展示

```text
请把这个任务拆成 todo 列表：找到项目入口并解释启动流程。
要求：输出 todo，并把它写入 todo store。
```

然后输入：

```text
/todo
```

预期：你能看到清单。

---

### 验收 2：执行过程中动态更新

```text
按你的 todo 逐项执行。每完成一项就更新状态。
要求：每轮结束后都能用 /todo 看到变化。
```

预期：
- todo 状态从 todo → doing → done
- notes 会逐步变具体

---

## 参考阅读

1. OpenAI Cookbook：Techniques to improve reliability（包含把复杂任务拆解为步骤、用结构化方式跟踪进度等实践思路）
   `https://cookbook.openai.com/`
2. OpenCode：Tools / todo（todoread/todowrite 的工具化思路与工程化约束）
   `https://opencode.ai/docs`

> 注：todo 的价值不在“写出来”，而在“执行过程中持续更新”。
