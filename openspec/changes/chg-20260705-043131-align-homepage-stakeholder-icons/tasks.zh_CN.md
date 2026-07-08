## 1. OpenSpec 与失败优先验收

- [x] 1.1 更新 proposal、design、spec 及其中文配套文件，使本次变更记录“多候选方案 + 反复验收”的 trace rebuild 流程，而不是旧的直接导入路线。
- [x] 1.2 在修改生成器之前，先为当前 stakeholder 图标重建包补上一个聚焦且会先失败的验收测试。

## 2. 多方案重建工具链

- [x] 2.1 扩展 stakeholder 图标重建脚本，使每个失败图标都能输出来自不同重建路线的多个候选版本。
- [x] 2.2 增加候选对比产物，使 source reference、多个候选版本和最终选中的版本可以并排审阅。
- [x] 2.3 增加专用 acceptance checker，覆盖交付包完整性、SVG 语义、特殊图标规则和可量化轮廓相似度。

## 3. 重建、筛选与迭代

- [x] 3.1 为每个失败图标至少生成两套候选版本，并为每个图标选出当前最优候选。
- [x] 3.2 对仍未通过验收的图标继续细化，并重复“重建-评审-验收”循环，直到整套通过。
- [x] 3.3 刷新最终预览图、metadata 和 review notes，使其反映通过验收的最终版本，而不是中间失败包。

## 4. 验证与收口

- [x] 4.1 对最终交付包运行聚焦验收测试及相关支撑检查。
- [x] 4.2 审阅最终 compare preview 与截图参考图，确认全部图标都符合验收标准。

## 5. 分层验收标准更新

- [x] 5.1 更新验收标准和验收脚本，明确区分 baseline trace fidelity 验收与 production polish 验收。
- [x] 5.2 按新的分层标准重新出具验收结论，并记录当前图标包“baseline 通过、production polish 未通过”。

## 6. Production polish 后续工作

- [x] 6.1 手工重建最终交付 SVG，使 6 个图标全部满足 production polish gate，而不只是满足 baseline gate。
- [x] 6.2 在把这套图标视为最终精修交付前，重新运行 production polish 验收。
