# 📘 Project Overview – Personal Billing Assistant (PBA)

---

## 🎯 Purpose

The **Personal Billing Assistant (PBA)** is a system designed to extract, structure, and analyze personal credit card bills from PDF statements. It enables monthly reporting and, in the future, will support natural language queries via WhatsApp, powered by an LLM interface. The long-term goal is to simplify financial tracking for individuals without needing a frontend, dashboards, or spreadsheets.

---

## 💡 Motivation

- PDF credit card bills are unstructured and hard to parse manually
- Bank UIs offer limited views and no long-term history or categorization
- People often don’t track their finances due to friction
- Conversational interfaces (WhatsApp + LLM) are low-friction and user-friendly
- Textract proved effective in extracting tabular data from complex PDFs

---

## 🔍 Project Goals

### Phase 1 – Core Pipeline
- Upload a PDF credit card bill
- Use **Amazon Textract** to extract tables
- Parse the tables using **Python (Pandas + Tabulate)**
- Store structured data (expenses) in a **PostgreSQL** database

### Phase 2 – Monthly Reports
- Aggregate and summarize monthly expenses per card
- Prepare reports in `.csv` or markdown format

### Phase 3 – Notifications
- Notify the user via **WhatsApp** when a new bill has been processed

### Phase 4 – LLM Query Interface
- Users will be able to ask questions like:
  - *"How much did I spend on transportation last month?"*
  - *"Compare my spending from March to May"*
- LLM will interpret, fetch, and return natural-language answers

---

## 🏗️ Architecture Summary

Incoming Email with Bill Attachment
↓
Lambda Trigger: Extract PDF and upload to S3
↓
Textract (AWS)
↓
Parsed Tables (Pandas)
↓
Cleaned Expense Data
↓
PostgreSQL Storage
↓
(Notifications via WhatsApp)
↓
(LLM answers questions on request)

No frontend is required. User interface will be **WhatsApp-based** only.

---

## 🧠 LLM Engagement

- LLMs are expected to handle:
  - Prompt-based parsing and validation of extracted reports (future)
  - Generating human-like answers to queries
  - Acting as a user-facing interface with embedded financial logic
- Future integration: **AWS Bedrock**, **OpenAI**, or similar LLM APIs

---

## 🔁 Repository Guide

- `src/`: Main source code (ingestion, Textract interface, DB logic, report generation)
- `data/`: Input PDFs, extracted JSONs, ground truth files
- `docs/`: Architecture diagrams, guides, draft notes
- `experiments/`: Past tests and prototypes, kept for traceability
- `tests/`: Unit and integration tests
- `README.md`: Quick start and setup

---

## 🔧 Tools & Dependencies

- Python 3.12+
- Pandas, Tabulate
- Amazon Textract
- PostgreSQL
- WhatsApp Business API (or mock interface)
- LLM API (future)


---

## 📌 Contributions & Usage

This project is designed to be:
- Modular: LLMs or humans can work on isolated parts (e.g., just parsing or just report generation)
- Transparent: Ground truth and test cases are tracked
- Expandable: Future plans include visualizations, comparisons, automated budgeting logic

---

*This markdown serves as the high-level blueprint and orientation file for both engineers and LLM agents joining the PBA project.*
