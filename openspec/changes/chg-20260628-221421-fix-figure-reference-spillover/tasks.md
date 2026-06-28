## 1. Regression coverage

- [x] 1.1 Add a failing DOCX extraction test for a chapter-opening figure reference sentence followed by a standalone `Figure 5` caption.
- [x] 1.2 Cover both `extract_docx_book` and `extract_docx_chapter_by_anchors` in that regression.

## 2. Extraction fix

- [x] 2.1 Tighten synthetic spillover-caption detection in `scripts/docx_parity/extract_docx.py` so mixed prose is only converted into a caption when actual spillover evidence exists.
- [x] 2.2 Keep existing standalone-caption and pre-heading spillover behavior intact for current test fixtures.

## 3. Verification

- [x] 3.1 Run targeted `tests/docx_parity/test_extract_docx.py` coverage for the new regression and nearby spillover cases.
- [x] 3.2 Run the narrow English Chapter 5 DOCX parity check to confirm the figure lead-in sentence is preserved.
