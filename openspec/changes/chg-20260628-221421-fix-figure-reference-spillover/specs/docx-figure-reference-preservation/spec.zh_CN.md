## ADDED Requirements

### Requirement: 独立图注之前的 figure 引用正文必须保留为普通段落
当 DOCX 中某个正文段落引用了 figure 编号，且其后紧跟同一 figure 的独立图注段落时，语义抽取器必须把该正文段落保留为普通 body text。

#### Scenario: 章节开头的 Figure 引导句在 caption 之前被保留
- **WHEN** 某个章节正文段落用普通句子说明某个概念，并在句中以内联方式包含 `Figure 5:`
- **AND** 下一个非空段落是独立的 `Figure 5 ...` caption
- **THEN** 抽取器把这句引导句保留为 paragraph body block
- **AND** 抽取器把独立的 `Figure 5 ...` 段落输出为 caption block

### Requirement: 合成式 caption spillover 必须依赖“嵌入式图注证据”
除非混合段落中存在当前抽取器已识别的 spillover 证据，例如文本粘连、重复或其他嵌入式图注特征，否则 DOCX 语义抽取器不得从普通正文段落中合成 caption block。

#### Scenario: 包含 figure 引用的普通正文不会被截断成 caption
- **WHEN** 某个段落在 `Figure N:` 之前包含普通正文
- **AND** 该段落不满足抽取器的 spillover-caption 判定
- **THEN** 抽取器不会把该段落切分成合成 caption 碎片
