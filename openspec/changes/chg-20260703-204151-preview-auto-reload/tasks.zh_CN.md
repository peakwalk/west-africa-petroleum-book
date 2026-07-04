## 1. OpenSpec artifacts

- [x] 1.1 为 preview 自动刷新补齐 proposal、design、tasks 和 capability spec
- [x] 1.2 为本次 change 中的每个持久化 OpenSpec 文档补齐简体中文配套文件

## 2. Preview watch and reload contract

- [x] 2.1 更新 preview 相关测试和源码级断言，使其描述“常驻 preview watcher + 浏览器自动刷新”的契约
- [x] 2.2 增加一个 preview watch 脚本，用于监听渲染相关源码根目录、串行化重建，并且只在成功构建后推进 reload token
- [x] 2.3 扩展 preview server，使 preview HTML 响应能够暴露并消费 reload token，同时不修改磁盘上的已构建文件
- [x] 2.4 把 watcher 和 reload token 路径接入 `scripts/preview.sh`，同时保持现有启动输出和清理行为

## 3. Verification

- [x] 3.1 运行 `sh scripts/test-preview-build.sh`
- [x] 3.2 运行 `sh scripts/test-preview-watch.sh`
- [x] 3.3 运行 `sh scripts/test-preview-cache.sh`
- [x] 3.4 运行 `npm run test:site`
