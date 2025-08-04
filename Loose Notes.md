# Loose Notes


## Next:

- Correct the parsing logic.
    * Review upstream how the recent learning change the current modules process.
        - The bill should be uploaded with its regular name, and when updating, if already in existance, it should validates whether replace it or work with the current.
    * Build the test for the extraction → The pytest fixture is the `unified_bill_payload.json` from the '02 ... different calls' experiment.
    * Adjust the extraction logic accordingly.






# PBA Refactor Plan – Multi-Stage Textract + Metadata Extraction
*(Updated with duplicate policy & audit retention)*

---

## Step 1 – `upload_to_s3.py` Review & Testing
**Why:** Ensures proper file naming, duplicate handling, and sets the foundation for pipeline consistency.

### Tasks
1. **Code Review & Enhancements**
   - Confirm S3 naming convention (prefix/folder structure).
   - Implement **duplicate handling policy**:
     - If identical file exists:
       - Prompt user via CLI:
         - Option 1 → **Ignore** (exit process)
         - Option 2 → **Replace & re-run pipeline**
       - Future integration: replace CLI prompt with UI confirmation.
   - Ensure return of `bill_original_name`.

2. **Testing**
   - Pytest:
     - Upload new file → confirm S3 key.
     - Upload duplicate → confirm prompt/handling.
   - Manual runner kept for quick debugging.

---

## Step 2 – `trigger_textract.py` Dual-Job Call
### Tasks
1. Call two separate Textract jobs:
   - `FORMS` → metadata & page-level currency.
   - `TABLES` → expense tables.
2. Return combined response:
   ```python
   {
     "forms_json": <FORMS raw JSON>,
     "tables_json": <TABLES raw JSON>
   }
   ```
3. Pytest with boto3 Stubber to validate both calls.

---

## Step 3 – bancolombia_v1.json Template Update
### Changes
* Add FORMS field mapping:

```json
"forms_to_extract": {
  "bill_owner": "Nombre del Titular",
  "product_id": "Número de Producto",
  "bill_date": "Fecha de Corte"
}
```
Other mappings (headers, fields_to_extract, currency_split) remain unchanged.

---

## Step 4 – parse_textract_output.py Refactor
### Tasks

1. Parse FORMS JSON using template instructions:

    * Extract bill_owner, product_id, bill_date.
    * Build currency_markers (page → currency).

2. Parse TABLES JSON:

    * Extract tables and link to page numbers.

3. Return unified payload:

```json
{
  "bill_original_name": "...",
  "bill_owner": "...",
  "product_id": "...",
  "bill_date": "...",
  "currency_markers": { "1": "USD", "2": "COP" },
  "tables": [{ "page": 1, "content": [...] }]
}
```

4. Pytest:

    * Fixture with sample Textract JSON.
    * Assert metadata and tables populated.

---

## Step 5 – extract_expenses.py Refactor
### Tasks

1. Input → unified payload from parser.

2. Normalization:

    * Assign currency using currency_markers[table.page].
    * Add user_owner = "<placeholder>".
    * Build bill_id = bill_owner + product_id + bill_date.

3. Output:

```json
{
  "user_owner": "<placeholder>",
  "bill_id": "...",
  "bill_original_name": "...",
  "bill_date": "...",
  "bill_owner": "...",
  "product_id": "...",
  "expenses": [ {...normalized expense...} ]
}
```

4. Fail fast if bill_owner, product_id, or bill_date missing.

5. Pytest:

    * Fixture with known payload → validate expenses and metadata.

---

## Step 6 – Ground Truth & Tests
### Tasks

1. Update ground truth to unified model (with metadata).

2. Update validate_expenses.py:

    * Check metadata fields exist.
    * Validate currency assignment and counts.

3. Keep manual runner for debugging.
---

## Step 7 – Audit Payload Retention (90 Days)
### Approach

* Retention Policy: keep unified extracted payloads (not raw Textract JSON) for 90 days.

* mplementation:

    1. Store payload JSON in an audit/ S3 folder (or DB JSON column).

    2. Add timestamp metadata to each payload.

    3. Implement scheduled cleanup:
        * Delete files older than 90 days (AWS Lambda or periodic cron job).

* **pytest:** mock audit save & cleanup trigger.

---

## Deliverables Summary

* Updated upload_to_s3.py (duplicate policy with CLI prompt + Pytest).
* Dual-job trigger_textract.py with tests.
* Updated bancolombia_v1.json template.
* Refactored parse_textract_output.py with template-driven metadata * parsing.
* Refactored extract_expenses.py with normalized output.
* Updated ground truth + validate_expenses.py.
* Audit payload retention mechanism (90 days).




















- Work on the E-R Diagram and the Data model.

- Work on the JSON retention policy: How to make sure we erase the JSON after the CC Bill is added to the DB?
    * Never actually save them in the first place. It is being saved now because it's necessary to test separately that the modules are running,
    but in the orchestration logic, there is no need to save them, only having them in memory while the data is parsed.

- Move everything to pytesting. → After Phase 1 is finished.





## _Up for discussion_

- ...






## To solve later
- Implement an Authentication system.
- Implement a PDF Unlocker.
- Nima's Legal constitution.







---



## DB Unified Data Schema

2. What Storage Approach Works Best?
Option A – PostgreSQL (Relational)
Why?

Structured data (users, bills, expenses).

Easy to join, filter, aggregate (e.g., “how much in February 2025?”).

Well supported by analytics tools and LLM connectors.

Suggested Schema:

Users table (user_id, name, contact info)

Bills table (bill_id, user_id, issuer, period_start, period_end, upload_date)

Expenses table (expense_id, bill_id, currency, authorization_number, transaction_date, description, original_amount, charges_and_credits, deferred_balance, installments)

Option B – Document Database (e.g., MongoDB)
Why?

Flexible if bill structures vary a lot.

Can store one big document per bill (like your current JSON).

Drawbacks:

Complex for SQL-style analytics.

Many LLM integrations expect relational DBs (SQL-friendly).

Harder to run joins across users, bills, and expenses.

Option C – Hybrid (PostgreSQL + JSON Column)
Store the normalized columns (bill_id, user_id, dates, totals) in relational tables.

Store the full raw JSON (if you want full traceability) in a JSON column for reference/debugging.

LLM Query Considerations
LLM queries are typically:

“How much did I spend on X in February 2025?”

“List all expenses > $100 in March 2025.”

SQL is a natural fit:

Many LLM frameworks (LangChain, OpenAI function calling, AWS Bedrock RAG) already work with relational DBs.

You can generate embeddings or summary views for faster retrieval.

Recommendation
Use PostgreSQL with normalized tables:

users → bills → expenses (1:N relationships).

Add currency field to each expense row instead of splitting lists.

Optionally store the original raw JSON in one column for auditing.

Keep schemas flexible but avoid over-normalization (e.g., don’t break description words into tokens unless needed).


