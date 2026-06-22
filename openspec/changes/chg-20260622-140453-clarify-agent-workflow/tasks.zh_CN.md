## 1. OpenSpec 工作流治理文档

- [x] 1.1 为代理工作流治理变更补齐 proposal、design、tasks 和 capability spec
- [x] 1.2 为本次变更中的每一份持久 OpenSpec 文档补齐简体中文对应文件

## 2. 仓库工作流契约更新

- [x] 2.1 用 MECE 的分类方式重写 `AGENTS.md` 中的 OpenSpec 与 Superpowers 章节，并补上仓库本地命令与路径规则
- [x] 2.2 更新 `AGENTS.zh_CN.md`，让中文工作流契约与英文版本保持语义一致

## 3. 验证

- [x] 3.1 确认被引用的 OpenSpec 与 Superpowers 路径存在，且新规则前后一致
- [x] 3.2 运行 `./node_modules/.bin/openspec validate chg-20260622-140453-clarify-agent-workflow --strict`
