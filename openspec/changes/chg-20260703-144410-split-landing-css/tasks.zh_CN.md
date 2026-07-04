## 1. OpenSpec 文档

- [x] 1.1 为落地页样式组织重构补齐 proposal、design、tasks 和 capability spec
- [x] 1.2 为本次变更中的每一份持久 OpenSpec 文档补齐简体中文对应文件

## 2. 落地页样式模块化

- [x] 2.1 按稳定职责把 `assets/css/landing.css` 拆成有顺序的同级模块，同时保持公开入口样式路径不变
- [x] 2.2 让每一个新的手写 landing 样式模块都落在仓库正常大小指导范围内，并保持现有资源引用不变

## 3. 验证更新

- [x] 3.1 更新 `scripts/test-site-render.sh`，让 landing CSS 断言针对展开 import 后的 CSS 内容执行
- [x] 3.2 运行 `npm run build:site`
- [x] 3.3 运行 `npm run test:site`
