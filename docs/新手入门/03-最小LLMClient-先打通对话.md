# 03. 最小 LLM Client：先打通“对话”，再考虑工具

这一章的目标非常单纯：**先把“稳定对话”打通，再谈工具调用**。

很多人一上来就想做工具系统，结果卡在最底层：调用模型这一步不稳、接口不统一、换个 provider 就全崩。

所以我们先把“地基”打好。

---

## 本章目标（验收标准）

完成这两条，就算通过：
- 输入一句话，模型能稳定回一句（先不调用工具）
- 能切换模型 / key / provider，而不需要改 agent loop

---

## 这一章真正要解决的问题

不是“怎么调 API”，而是“怎么把 API 变成稳定的系统接口”。

你需要两层抽象：
- Provider 抽象：对上层暴露一致接口
- Client 实现：负责发请求、处理响应（可选 stream）

---

## 为什么一定要先做 Provider 抽象

因为不同模型服务商虽然“长得像”，但细节差异很大。

最典型的是消息结构与工具协议：
- 以 Anthropic Messages API 为例，它要求输入是 `messages`（每条包含 `role` 和 `content`），并允许通过 `tools` 提供工具定义，模型再返回结构化的工具调用块。换句话说，“messages + tools”是它明确支持的一等能力。citeturn0search0turn0search6

这类差异如果泄漏到上层（比如泄漏到 agent loop），你后面每换一次 provider 就要重写一遍核心逻辑。

工程上更稳的做法是：**把差异压在 provider 层，给上层一个稳定接口**。

---

## 推荐的最小统一接口（够用且能扩展）

先不要设计得太花，下面这个接口就很实用：

```text
chat(messages, options) -> response
```

其中：
- `messages`：统一消息结构（system / user / assistant / tool）
- `options`：模型名、温度、最大 token、是否流式等
- `response`：至少要能拿到 `content`（后续再扩展工具调用）

关键点只有一个：**上层不要知道 provider 的细节形状**。

---

## 一份“最小但专业”的实现蓝图（直接照着做）

### Step 1：先把 messages 结构定死

强烈建议你在项目内统一消息结构（哪怕 provider 内部要做转换）：
- `role`
- `content`
- `timestamp`（可选但建议）
- `metadata`（可选但建议）

这会让后面的：
- 会话恢复
- 工具写回
- 上下文压缩

全部更自然。

---

### Step 2：做一个 provider-agnostic 的 client 壳

建议你把上层调用收敛到一个类，比如：
- `LLMClient.chat(messages, options)`

这个类内部再根据配置选择 provider：
- anthropic provider
- openai-compatible provider
- 其他 provider

对上层来说，调用方式永远一样。

---

### Step 3：先追求“稳定返回”，不要急着 stream

流式输出很酷，但在入门阶段是干扰项。

优先级建议是：
1. 非流式稳定返回
2. 错误处理清晰（超时 / 鉴权 / 网络错误）
3. 再考虑 stream

---

## 本章验收脚本（你可以直接用来验证）

建议用这三条最小验收：

### 验收 1：最小对话

```text
你好，请用两句话介绍你自己。
```

预期：稳定返回文本。

---

### 验收 2：切换模型参数但不动上层逻辑

操作方式：
- 只改配置里的 model / key / provider
- 不改 agent loop 的代码

预期：仍能稳定对话。

---

### 验收 3：错误可解释

故意制造一个错误（例如：
- key 置空
- model 写错
）

预期：
- 报错信息能指向原因
- 不会把上层循环搞崩

---

## 本章小结（你现在真正获得的能力）

- 你不只是“能调 API”，而是拥有了一个“可替换模型底座”。
- 从这一章开始，你的系统才具备“换 provider 不重写核心逻辑”的资格。
- 下一章（Agent Loop）会直接建立在这个底座之上。

建议下一步阅读：
- `docs/新手入门/02-REPL与会话-把聊天框做成系统.md`
- （或继续按大纲）Agent Loop v0
