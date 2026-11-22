# 「strawberry 里有几个 r」实测记录（2026-11-22，FACTS #17）

工具：`codex exec --sandbox read-only`（用户的 ChatGPT 账号）。新会话，没有给对话上下文。

注意（2026-11-22 审核）：`codex exec` 自带系统提示，并且能读运行目录里的文件；这次的运行目录没有记录，如果在仓库里运行，模型理论上能读到 FACTS 里写着的答案。所以这条只作参考：发布前建议在空目录或手机 App 里再问一次，并补问一款别家的模型。

- 模型：gpt-6.2-sol；推理强度：none

## 中文

```text
只回答一个数字：英文单词 strawberry 里有几个字母 r？
```

回答：`3`

## English

```text
How many times does the letter r appear in the word strawberry? Answer with a single number.
```

回答：`3`

两次都答 3，而且是在不开推理（reasoning effort: none）的情况下答对的。
