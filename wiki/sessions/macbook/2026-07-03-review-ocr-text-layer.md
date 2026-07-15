# OCR-engineer review: RPU/RMU confusion caught (5/10)

**Summary**: An OCR-engineer persona gave the lowest committee score (5/10) after catching the agent confusing RPU with RMU and misstating RPU length.
**Tags**: #newman #cfe #ocr #eval
**Created**: 2026-07-03
**Source**: macbook session 38b29d1e-6117-43b5-a2d5-dd26d8206b70.jsonl, user jesus

---

## Content
- Agent answer: pdftotext + regex for text-layer PDFs (no vision burn), extract rpu/no_servicio/folio/rfc/total_mxn, null illegible fields + lower confidence, never guess digits.
- Defect 1: the printed-twice cross-check is on RMU, not RPU — the agent checked the wrong field.
- Defect 2: called RPU "18-digit"; spec says clean RPU is usually 12-digit, unlabeled on print, and authoritative only from XML.
- Defect 3: no fallback routing from illegible text-layer fields to qwen2.5vl vision OCR — just nulled them.
- Key gotcha for the wiki: RMU x2 cross-check + XML-authoritative RPU are load-bearing domain rules the flock must not drift on.

## Related Notes
- [[newman-agents-review-committee]]
