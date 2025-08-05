# Personal Billing Assistant (PBA)

The **Personal Billing Assistant (PBA)** is a CLI-based system that extracts, structures, and analyzes credit card bills from PDFs. The goal is to simplify personal financial tracking with no need for frontends or spreadsheets, and eventually enable natural language queries via WhatsApp using an LLM.



## 🚀 Project Purpose

Most people don’t track their expenses because the friction is too high — scattered PDFs, clunky UIs, no long-term summaries. PBA automates this by:

- Extracting expense tables from PDF bills
- Structuring and storing the data
- Generating monthly reports
- (Planned) Notifying users via WhatsApp
- (Planned) Answering questions like _"How much did I spend on food last month?"_ via LLMs


## 🏗️ Architecture Overview

    PDF Email Attachment
    ↓
    Upload to S3
    ↓
    Textract (TABLES)
    ↓
    Table Parsing (Pandas)
    ↓
    Cleaned Expenses
    ↓
    PostgreSQL Storage
    ↓
    (Notifications / LLM Query Layer)


## 🧱 Current Development Status

We are currently working on:

### ✅ Phase 0: Groundwork
- Project structured into modular folders
- Textract selected as the parsing engine
- `.env` and secrets management scaffolded

### 🧩 Phase 1: Core Pipeline (WIP)
- Upload PDF to S3 [`upload_to_s3.py`] ✅
- Trigger Textract on uploaded files [`trigger_textract.py`] ✅
- Parse JSON output to extract expense tables ✅
- Transform and clean expense records ✅
- Store in PostgreSQL 🔜
- Run orchestrator script end-to-end
- Validate against ground truth for 3 known PDFs



## 🧠 LLM Integration (Planned)

Later phases will add:
- LLM-based natural query resolution
- Answering user questions via WhatsApp
- MCP-based access to stored structured data

LLMs will handle:
- Summarization
- Classification
- Contextual queries
- Financial insight generation



## 📁 Repo Structure

    📁 PBA/
    ├── 📁 audit        # ephemeral pipeline outputs
    │   └── 📁 logs
    ├── 📁 config
    ├── 📁 data     # static reference data
    ├── 📁 docs
    │   ├── 📁 architecture
    │   └── 📁 context_maintenance      # Methodology to work with AI asistance en mantain context
    ├── 📁 experiments      # To dry run hypothesis and functionalities
    ├── 📁 src      # main app code
    │   └── 📁 pba           # importable package (`from pba.* import ...`)
    │       ├── 📁 core
    │       ├── 📁 db
    │       ├── 📁 ingestion
    │       ├── 📁 llm_interference
    │       ├── 📁 notifications
    │       └── 📁 textract
    └── 📁 tests        # test code and fixtures


## ⚙️ Tech Stack

- Python 3.12+
- AWS Textract (`analyzeDocument`)
- PostgreSQL
- Pandas, Tabulate
- WhatsApp Business API (planned)
- OpenAI / Bedrock (planned)



## 📌 How to Run (Prototype)

```bash
# Install dependencies
pip install -r requirements.txt

# Enable local imports (once per environment)
pip install -e .

# Load .env with AWS credentials and bucket
export $(cat .env | xargs)

# Run a test file (example)
python tests/test_upload.py
```


## Adding New Bill Templates

The application supports parsing multiple bill formats using template configurations.  
To add a new template, see [docs/templates.md](docs/templates.md) for schema documentation and step-by-step instructions.



---

## ✍️ Contributions & Philosophy
This repo is designed to support both human engineers and LLM agents in parallel:

* Modular + testable
* Ground truth–driven validation
* Ready for LLM-based automation

_This README is provisional and will evolve with the project. For full vision and progress, refer to the logbook and dev plan._


