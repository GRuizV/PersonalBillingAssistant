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


### 📅 [2025-07-22] – Switched to Async Textract API for PDF Compatibility

**Context:**  
Encountered `UnsupportedDocumentException` when calling `analyze_document()` on PDF files stored in S3.

**Investigation Outcome:**  
- AWS Textract requires the **async API (`start_document_analysis`)** for PDFs and TIFFs in S3.
- The synchronous `analyze_document()` only works with images (JPEG, PNG) passed via byte streams.
- The same document succeeded via AWS Console, confirming the format was valid.

**Action Taken:**  
- Rewrote `trigger_textract.py` to use the async API.
- Implemented polling loop with `get_document_analysis()`.
- Problem resolved and raw Textract output now retrieved as JSON.

### 📅 [2025-07-23] – Template Adapter System & Extended Transformer for Bancolombia Bills

**Context:**  
The expense extraction process initially focused on simple row normalization, assuming a stable and known bill structure.  
However:
- Different card issuers (and even updates from the same issuer) may change the structure of credit card statements.
- Bancolombia bills, while consistent now, cannot be guaranteed to keep the same format long-term.
- Bills often include payments, adjustments, and installment information that impact totals and must be handled correctly.

**Decisions:**  
- Introduced an **adapter-based transformer** using a JSON configuration file (`bill_templates.json`) to define:
  - Header patterns for table detection
  - Currency split rules (foreign (USD) vs domestic (COP))
  - Fields to extract and normalize
  - Excluded descriptions (e.g., `"ABONO SUCURSAL VIRTUAL"`) since it belongs to payments and those won't be part of this Use Case.
- Added a flexible architecture so that future card issuers or new Bancolombia templates can be supported by **adding/updating a config entry** instead of rewriting core logic.
- Extended `extract_expenses.py` logic to:
  - Use table-specific currency detection (scan rows until one record provides criteria match).
  - Filter out only specific payment rows (`ABONO SUCURSAL VIRTUAL`) while retaining all other adjustments (negative values preserved as negative floats).
  - Keep the `Cuotas` (installments) field as strings instead of converting to integers, since values like `"1/1"`, `"2/5"`, `"10/36"` indicate pending installments and are relevant for reporting as-is.
- Updated the template configuration file structure to be nested under `"bill_templates"` to prepare for future configuration extensions beyond billing templates.

**Outcomes:**  
- **Extensible extraction pipeline:** Core logic is now isolated from issuer-specific details.
- **Correct financial handling:** Adjustments and negatives are preserved, payments are excluded properly, and currency classification works without unnecessary full-row scanning.
- **Future-proofing:** Any future change in Bancolombia’s bill template or adding new issuers requires only config changes, not code rewrites.
- **DB-readiness:** Normalized record structure is consistent and ready for mapping into database schemas when that step arrives.

**Notes & Learnings:**  
- Bills contain payment and adjustment records that behave differently:
  - `"ABONO SUCURSAL VIRTUAL"` payments are excluded as they don’t affect expense analysis.
  - Other adjustments (negative values) are included, as excluding them causes totals to mismatch actual statements.
- Currency detection no longer requires scanning every row; scanning until one record matches criteria is sufficient since Bancolombia never mixes currencies in a single table.
- Template file naming and nesting (`bill_templates.json` under `bill_templates` key) improves long-term maintainability and separates future configurations.
- Although installments could be converted into pending counts (`"1/1" → 0 pending"`, `"2/5" → 3 pending"`), they are kept as raw strings for now to preserve full reporting context.

---

### 📅 [2025-07-28] – Standardized Output Keys and Date Format

**Context:**  
The extracted data from credit card bills contained:
- Headers with accented characters and spaces (e.g., `"Número de Autorización"`)
- Dates formatted according to issuer locale (`dd/mm/yyyy`)

These could create interoperability issues for database storage, APIs, and downstream systems.
Additionally, the project’s codebase and documentation are already in English, and this project 
is planned for open-source release, where English is the industry norm.

**Action Taken:**  
- Modified `bill_templates.json` to explicitly define field mappings:
  - `"original"` → `"english"` (e.g., `"Número de Autorización"` → `"authorization_number"`).
- Updated `extract_expenses_from_tables()` to output records with **English, snake_case** keys.
- Preserved date normalization (`dd/mm/yyyy` → ISO-8601 `yyyy-mm-dd`) to ensure:
  - Unambiguous, consistent date representation
  - Compatibility with SQL databases and external APIs
- Updated function documentation to reflect these changes.

**Impact:**  
- Output now consistently uses **English, ASCII, snake_case keys** 
  (`authorization_number`, `transaction_date`, `description`, etc.).
- Dates are stored in **ISO-8601** format (`yyyy-mm-dd`), ready for database DATE/TIMESTAMP fields.
- Simplifies integration with databases, APIs, and future multilingual issuers.
- Original PDF headers are still used internally for table detection and template matching.

**Next Steps:**  
- Update downstream modules (DB insert, reporting) to expect English safe-case keys and ISO dates.
- Add Pytest tests to validate correct field mapping and date normalization behavior.


### 📅 [2025-07-29] – Unified Expense Data Model

**Context:**  
The original expense extraction output separated expenses by currency into two buckets 
(`usd_expenses` and `cop_expenses`).  
This design ensured currencies were not accidentally mixed when aggregating values but made 
downstream storage and analytics more complex, particularly when integrating with 
a relational database and preparing for LLM-based natural language queries.

**Decision:**  
* Move from two currency-specific buckets to a **unified expense list** where each record includes 
  a `currency` field.
* Introduce separate **bill-level metadata** to capture issuer, billing period, and upload information.

New Expense Record Data Model:
```json
{
  "user_id": "<user reference>",
  "bill_id": "<bill reference>",
  "currency": "USD" | "COP",
  "authorization_number": "T05372",
  "transaction_date": "2025-02-25",
  "description": "APPLE.COM/BILL VR MONEDA ORIG 27800.0 USA",
  "original_amount": 6.82,
  "charges_and_credits": 0.19,
  "deferred_balance": 6.63,
  "installments": "1/36"
}
```

Bill Metadata:
```json
{
  "bill_id": "<bill reference>",
  "user_id": "<user reference>",
  "issuer": "Bancolombia",
  "period_start": "2025-02-01",
  "period_end": "2025-02-28",
  "upload_date": "2025-03-05T10:15:00"
}
```

**Rationale:**
* Simplifies database schema (single expenses table instead of one table per currency).
* Enables easier sorting, filtering, and aggregations while still preventing accidental currency mixing by enforcing explicit currency filtering.
* Aligns with industry practices in financial data warehousing and analytics, where multi-currency data is stored in one table with a currency code column.
* Simplifies future LLM prompt design by avoiding special-case logic for multiple tables.


**Impact:**
* Transformer output format changes (no more usd_expenses and cop_expenses keys).
* Tests and downstream modules must be updated to handle the unified format.
* LLM prompt templates and analytics queries will need explicit currency filtering.


**Next Steps:**
* Refactor extract_expenses_from_tables() to output a unified list with a currency field.
* Update unit tests to reflect the new data model.
* Adjust any prototype DB insertion logic to target the unified schema.
* Document LLM prompt adjustments to request or assume a currency context for natural queries.


### 📅 [2025-07-30] – Currency Identification & Textract Job Strategy (Combines "TABLES" & "FORMS" failure)

**Context:**  
We needed to validate whether a single Textract call using both `TABLES` and `FORMS` could deliver all required bill data:
- Currency markers (`ESTADO DE CUENTA EN: DOLARES` / `ESTADO DE CUENTA EN: PESOS`)
- Bill owner and product ID
- Billing period
- Expenses table

**Experiments & Results:**  
1. **Combined `TABLES+FORMS` call**  
   - Correctly extracted non-tabular metadata (currency markers, bill owner, product ID, billing dates) via `FORMS`.  
   - **However**, expense tables were corrupted:  
    - Some cells were split into `LINE` blocks.  
    - One table was partially reconstructed, mixing tabular and line-level data.

2. **Raw JSON table reconstruction from combined job**  
  - Attempted to rebuild tables directly from `TABLE` blocks only.  
  - **Confirmed the corruption persisted**; tables were **incomplete** compared to the ground truth.

**Key Learnings:**  
- **Currency markers and metadata** are reliably extracted with `FORMS`.  
- **Expense tables must be parsed separately** using a dedicated `TABLES`-only Textract call to preserve table integrity.  
- To associate expenses with their currency:
  - Use bounding box positions from the `FORMS` run for `"ESTADO DE CUENTA EN: DOLARES|PESOS"` markers.
  - Infer currency context for each table from its vertical position relative to these markers.

**Filename Parsing Consideration:**  
- While the bill filename (`Extracto_774507892_202501_TARJETA_MASTERCARD_3667.pdf`) contains useful elements:
  - Bill ID → `774507892`
  - Billing period → `202501`
  - Product ID → `TARJETA_MASTERCARD_3667`
- Relying on filename parsing introduces **tight coupling** to Bancolombia’s current naming conventions.  
- If the bank changes its naming policy, parsing logic would break and require refactoring.  
- **Decision:** Avoid filename-based parsing for critical data and use Textract outputs (`FORMS`) for:
  - Bill owner
  - Product ID
  - Billing period
  - **Bill ID** → Will be built later when storing the bill in the DB as a combination of `Bill Owner` + `Product ID` + `Billing Period`
  - Original File Name will still be saved as additional field in the Bill Data Model.
  Filename parsing may remain as a **fallback**, but not as the primary data source.

**Decisions:**  
- Implement two independent Textract jobs:  
  1. **FORMS job** → Collect metadata and currency markers (with position).  
  2. **TABLES job** → Collect raw expense tables with guaranteed structure.  
- Add a post-processing step to join both outputs by page and bounding box position, ensuring each expense table is tagged with the correct currency.

**Next Steps:**  
- Write join logic to map tables from the `TABLES` job to the nearest preceding currency marker from the `FORMS` job.  
- Document and validate the final currency assignment heuristic with additional ground truth cases.  


### 📅 [2025-07-31] – Finalized Two-Call Textract Strategy and Unified Parser (02 exp)

**Executive Summary:**  
A single Textract call with `["FORMS","TABLES"]` corrupted table detection.

We split processing into two separate calls and built dedicated parsers, producing a clean unified schema and improving data accuracy by fixing KV parsing logic (global block map approach).

---

**Context:**  
Following previous findings that combining Textract `["FORMS","TABLES"]` in one call corrupts table detection, we designed and implemented a two-step approach:
1. `FORMS` job → Extract metadata (bill owner, card product ID, billing period, currency markers).  
2. `TABLES` job → Extract clean expense tables.

**Experiments & Results:**  
- Built and tested independent parsers:

/

**FORMS parser**:
  - Extracts:
    - `bill_owner`: Filters out address-containing variants of `SEÑOR (A):` and picks the most frequent name-only value.
    - `product_id`: Uses KV pairs for the last 4 digits and detects the card network (VISA, MASTERCARD, AMERICAN EXPRESS, DISCOVER) from all text blocks, appending it to the product ID.
    - `bill_date`: Extracted from the `Hasta:` field.
    - `currency_markers`: Converted to dictionary `{ page -> marker }`, reflecting one currency per page.
      
**TABLES parser**:
  - Reconstructs all tables into normalized 2D arrays, each tagged with its page.

/

- Implemented a **unified payload builder** that merges FORMS and TABLES data into one schema:
```json
{
  "bill_owner": "string",
  "product_id": "string",
  "bill_date": "string",
  "currency_markers": { "page": "currency" },
  "tables": [ { "page": int, "content": [[...]] } ]
}
```

**Key Learnings:**

* Splitting Textract calls by function (FORMS vs TABLES) ensures table integrity while retaining KV-based metadata.
* currency_markers as a dictionary simplifies mapping currencies to tables (page-to-page mapping).
* An heuristic cleanup is required:
  * To avoid address noise in bill_owner.
  * To recover card network information that may not appear in KV pairs.

**Decisions:**

* Continue using two separate Textract jobs and dedicated parsers.
* Maintain the final unified schema for all downstream integrations.
* Document and keep the card network and owner name heuristics as part of production logic (subject to template changes).

--- 

  #### Working with KV Pairs from Textract FORMS – Key Lessons

  **Broader Summary:** When parsing data from textract in "FORMS" job, rebuild the block globally, not per page because it leaves out KV-pairs not bound to a specific page. 

  ---

  **Decision Rationale:**

  We initially tried parsing FORMS data page by page, but discovered that relationships can span across page block sets, causing missing KV pairs. The solution was to build one global block map and process KV pairs across all pages.

  **Why the initial parsing missed data?**

  - Textract output is page-oriented, returning an array of pages, each containing its own blocks.

  - In the first parsing attempt, we iterated page by page, building a fresh **block_map** for each page and only processing **KEY_VALUE_SET** blocks within that subset.

  - Some **KEY_VALUE_SET** blocks rely on relationships that can span across other blocks or require the global block map to resolve properly.

  **Result:** some KV pairs (like the repeated **"ESTADO DE CUENTA EN:"** entries) were skipped because they weren’t fully captured when processing page by page.

  /

  **Correct approach to parse KV pairs**

  * Build one global block_map:
    * Combine all blocks from all pages into a single dictionary keyed by Id.
    * This ensures every relationship reference (e.g., VALUE → WORD) can be resolved.

  * Process all KEY_VALUE_SET blocks globally: 
    * loop through every block in the global map.

  * Identify those with:
  ```python
    block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block.get("EntityTypes", [])
  ```

  * For each, retrieve:

    * Key text → Traverse its CHILD relationships.
    * Value text → Follow VALUE relationship(s) to the corresponding VALUE block(s) and traverse their children.
    * Page → Use block["Page"] to know which page the KV pair belongs to.

  * Save results with all attributes:

    * Store key, value, page, and an optional "source": "KV" tag.
  /

  * Example structure:
  ```json
  {
    "key": "ESTADO DE CUENTA EN:",
    "value": "DOLARES",
    "page": 1,
    "source": "KV"
  }
  ```

  #### Why this works better

  - By using a global map, all relationships between blocks can be resolved regardless of how Textract groups them internally.
  - It avoids partial parsing that can miss KV pairs repeated across pages or linked in non-standard layouts.
  - It produces a complete, page-aware dataset, essential for downstream logic like linking currency markers to tables.

  **Key takeaway:** Always build one global block map and process all KEY_VALUE_SET blocks globally when extracting key-value pairs from Textract FORMS output.

  This guarantees completeness and consistency, especially for documents with repeating keys or multi-page templates.

.



## August


### 📅 [2025-08-05] – Package Setup & Import Path Fix

**Context:** Historically, running test files directly (via python tests/test_*.py or IDE F5) 

required adding manual path hacks:

```python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```
This was due to Python not automatically recognizing the src/ folder as a package root.

**Action Taken:**
- Restructured project to introduce a dedicated namespace package:

```
 src/
    └── pba/
        ├── ingestion/
        ├── core/
        ├── textract/
        └── ...
```

Added minimal setup.cfg and pyproject.toml to enable editable install.

- Installed package with:
```bash
pip install -e .
```

- Removed tests/__init__.py to ensure tests/ is not treated as a package.

- Updated imports to use the package name:
```python
from pba.ingestion.upload_to_s3 import upload_file
```

- Verified tests run without any sys.path.append or $PYTHONPATH hacks.


**Impact:** 

- Clean, maintainable imports across all scripts and IDE runs.
- Scales for future modules without extra setup.
- Simplifies team onboarding and potential CI/CD integration.









