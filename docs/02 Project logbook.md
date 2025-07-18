# 📓 Project Logbook

**Personal Billing Assistant (PBA)**  
This log tracks findings, decisions, and technical reasoning made throughout the development of the PBA system. It complements the README and serves as a memory anchor for both humans and LLM agents.

---

## June

### 📅 [2025-06-03] – Initial Architecture Defined

**Context:** Explored initial feasibility of parsing PDF bills for personal expense tracking.

**Action Taken:**  
- Drafted first architecture diagram (`docs/architecture/2025.06.03 - Draft de Arquitectura.drawio.xml`)
- Defined high-level components: ingestion, parsing, DB, notification, LLM interface


### 📅 [2025-06-04] – Ground Truth Established

**Context:** Needed a reliable way to verify Textract output accuracy.

**Action Taken:**  
- Manually extracted expected tables from multiple PDFs into Excel and JSON
- Created `data/ground_truth.json` and `ground truth total.md`

---

## July

### 📅 [2025-07-17] – Chose Amazon Textract Over Other OCR Engines

**Context:** Tested multiple tools to extract structured tables from complex PDFs.

**Options Considered:**
- Amazon Textract
- Tesseract + Pandas
- LayoutParser + PDFMiner

**Decision:** Amazon Textract (`analyzeDocument` endpoint)

**Rationale:**
- High table fidelity
- Robust against multi-column bank statements
- Native AWS integration for future Lambda triggers


### 📅 [2025-07-18] – Finalized Project Structure & Defined Dev Plan and LLM Strategy

**Context:** 
- Repo had grown organically during PoCs and needed restructuring.
- Prepared for full pipeline buildout.

**Action Taken:**
- Moved all PoCs into `experiments/`
- Created modular `src/` structure for production logic
- Created `tests/`, `docs/`, `data/`, and `config/` folders
- Created `PBA_Development_Plan.md` for phased implementation
- Confirmed WhatsApp + LLM interface as end-user layer (no frontend)
- Documented LLM expectations and interaction patterns in `PROJECT_OVERVIEW.md`

---
