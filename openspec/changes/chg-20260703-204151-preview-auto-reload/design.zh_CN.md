## Context

当前 preview 工作流刻意保持简单：`scripts/preview.sh` 只执行一次 `npm run build:site`，打印 preview URL，然后让 `scripts/preview_server.py` 直接服务 `public/`。这让 assembled site 的边界很清晰，但也意味着 preview 没有常驻的构建循环，也没有浏览器自动刷新通道。

这次变更会同时触及多个层面：

- `scripts/preview.sh` 中的 shell 启动编排
- `scripts/preview_server.py` 中的静态服务行为
- 一个新的 preview watch 脚本中的 assembled-site 重建编排
- preview 相关校验脚本

仓库已经把 `public/` 视为唯一的已装配输出树，因此方案应保持这一模型，而不是再引入第二套 dev server 或独立的 preview 构建格式。

## Goals / Non-Goals

**Goals:**
- 保持 `npm run preview` 作为唯一的本地预览入口。
- 在会影响渲染的源码变更后自动重建 assembled site。
- 在成功重建后自动刷新已打开的 preview 页面。
- 当平台自带工具足够时，不增加额外的 watch 或 websocket 依赖。
- 保持现有启动 URL、路由结构和生产构建输出不变。

**Non-Goals:**
- 在刷新时保留浏览器内的 UI 状态。
- 引入真正的模块级 HMR。
- 用局部构建或按路由构建替换 `build:site`。
- 把 preview 刷新代码写入磁盘上的生产产物。

## Decisions

### Decision: 新增一个基于 Node 的 preview watcher
Preview 命令应启动一个专门的 Node 脚本，监听 `assets/`、`config/`、`editions/`、`scripts/` 和 `theme/` 这类稳定的渲染相关根目录。文件变化后，它应继续执行现有的 assembled-site 构建命令，而不是再发明一套新的构建管线。

这样可以让 preview 始终围绕用户已经在检查的 `public/` 输出运行，也能避免高风险地迁移到 Vite/Webpack，或者拆成 `mdbook serve` 加 landing-page 代理的双服务结构。

Alternative considered:
- 通过多个 dev server 和代理重新拼装 preview。拒绝，因为这会让路由归属更复杂，并复制现有 assembled-site 工作流。

### Decision: 通过 debounce 和 rerun 标志串行化重建
Watcher 应对一组连续文件事件做 debounce，并保证同一时间只运行一个重建进程。如果重建进行期间又有新的变更到来，只记录“还需要再跑一次”，待当前构建结束后最多补跑一次。

这样可以避免多个 `build:site` 进程同时写 `public/`，并在编辑器一次保存产生多个文件系统事件时保持行为可预测。

Alternative considered:
- 每个事件都立刻启动一次新的构建。拒绝，因为并发的全站构建会在同一输出树上竞争。

### Decision: 使用共享 reload token 文件配合 preview-only 轮询
Watcher 和 server 之间通过一个共享的 reload token 文件通信。Watcher 只在成功重建后更新 token。Preview server 通过一个仅用于 preview 的 endpoint 暴露当前 token，并向 HTML 响应注入一段浏览器端预览脚本，轮询该 endpoint，在 token 变化时触发 `location.reload()`。

这种设计让跨进程协调保持简单，不需要 websocket 依赖，而且书页和 landing page 都能使用同一套机制。

Alternative considered:
- 在 Python server 中加入 websocket 推送。拒绝，因为对整页刷新来说，它显著增加了协议和进程复杂度，却没有实际收益。

### Decision: 在服务时注入 preview client，而不是在构建时注入
当配置了 reload token 文件时，preview server 只应在它返回的 HTML 响应中注入轮询脚本。`public/` 目录中的 HTML 文件本身不应被改写。

这样可以保持生产产物契约不变，并把 preview-only 行为隔离在 preview server 的响应路径中。

Alternative considered:
- 让各个页面生成器和主题模板按条件输出 preview 刷新代码。拒绝，因为这会把 preview-only 逻辑分散到多个产物生成源里。

## Risks / Trade-offs

- [全站重建仍然会比真正的 HMR 慢] -> 接受，因为这次需求的核心是避免手动重启，而现有 assembled-site 构建仍是最稳定的正确性边界。
- [不同编辑器产生的文件监听事件可能很嘈杂或被合并] -> 监听稳定的顶层目录、对事件做 debounce，并在构建中最多排队一次补跑。
- [构建失败时浏览器可能继续显示旧内容] -> 构建失败时不推进 reload token；继续提供上一次成功的输出，并把错误打印到 stderr。
- [preview-only HTML 注入可能意外泄露到发布产物] -> 只在带有 reload token 标志的 Python server 响应路径中注入，绝不把修改后的 HTML 写回磁盘。

## Migration Plan

1. 为 preview 自动刷新补齐 OpenSpec proposal、design、tasks 和 capability spec。
2. 先更新 preview 相关测试和源码级断言，描述新的 watch / reload 契约。
3. 实现 preview watcher 和 reload token 协调。
4. 扩展 preview server，使其支持 preview-only HTML 注入和 reload token endpoint。
5. 把 watcher 接入 `scripts/preview.sh`，同时保持现有局域网启动输出和清理行为。
6. 验证 preview 专项测试，以及最小必要的 assembled-site 检查。
