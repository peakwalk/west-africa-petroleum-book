## 1. 创建对称的 edition 工作区

- [x] 1.1 建立 `editions/en/` 与 `editions/fr/` 的目标目录结构，包含 `book.toml`、`locale.json`、`site/` 与 `content/`，并在迁移期间暂时保留旧路径。
- [x] 1.2 将英文和法文的语言自有输入复制到新的 edition 根目录下，包括 landing 源内容、legal 源内容、Markdown 章节、figure 资源和 figure manifest。
- [x] 1.3 新增或更新结构测试，断言两个 edition 根目录都具备相同的必需工作区形状，并确认法文 figure root 仍然是实体目录。

## 2. 重构 edition registry 与路径加载器

- [x] 2.1 简化 `config/editions.json`，让每个语言只声明 `editionRoot`、`routePrefix`、manuscript alias，以及可选的 figure text replacement map。
- [x] 2.2 更新 `scripts/shared/site-editions.mjs`，让它从 `editionRoot` 派生 book、site、content、legal、locale catalog、chapter、figure root 和 figure manifest 路径。
- [x] 2.3 更新 `scripts/edition_config.py` 以及依赖它的 Python 校验辅助逻辑，使其与 Node loader 使用同一套派生路径契约。
- [x] 2.4 更新 registry 相关测试，保证 Node 与 Python 的路径解析始终一致。

## 3. 迁移生成器与 mdBook 入口

- [x] 3.1 将英文和法文 mdBook 配置迁移到 `editions/en/book.toml` 与 `editions/fr/book.toml`，并更新站点装配器，将它们分别构建到 `public/book` 与 `public/fr/book`。
- [x] 3.2 将 landing、legal 和 chapter-library 的源输入迁移到 `editions/*/site/`，并更新生成器从这些 edition-local 路径读取内容。
- [x] 3.3 为 landing、legal 与 chapter-library 生成器增加 output-root 支持，使其能够按 route prefix 直接写入 `public/`。
- [x] 3.4 更新 `package.json` 中的 build 与 preview 入口，使 `build:site` 成为唯一标准的 assembled-site 工作流。

## 4. 将校验切换为只面向 public 发布产物

- [x] 4.1 更新 `tests/test_public_editions.py`，让它从 `public/` 或受控临时输出目录验证 landing/legal/chapter 输出，而不再依赖根目录受控 HTML。
- [x] 4.2 更新 `tests/test_book_editions.py`、`scripts/test-site-render.sh` 和 preview 相关检查，使 `public/` 成为唯一发布产物树。
- [x] 4.3 运行与新拓扑最相关的项目校验，包括 `npm run build:site`、`npm run test:site`、`npm run check:docx-parity:all` 和 `npm run check:docx-figures:all`，并修复所有路径回归。

## 5. 删除旧拓扑与兼容层

- [x] 5.1 在 direct-to-`public/` 流程验证通过后，删除 `public/` 之外受版本控制的 landing/legal/chapter 生成 HTML，包括根目录静态页面和根级 `fr/` 目录树。
- [x] 5.2 删除不再需要的旧语言源码根与接线层，包括 `src/`、`src-fr/`、`books/fr/`、根 `book.toml` 以及旧 locale catalog 路径。
- [x] 5.3 全面清理脚本、测试和贡献者文档中的旧路径引用，使 `editions/<locale>/` 与 `public/` 成为唯一被记录的源码/产物模型。
