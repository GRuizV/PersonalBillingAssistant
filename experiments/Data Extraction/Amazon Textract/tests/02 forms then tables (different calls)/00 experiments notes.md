# Results

**Experiment:** 01 exp_extract_form_then_tables
**Date:** 2025-07-31



## Working with KV Pairs from Textract FORMS – Key Lessons

### Why the initial parsing missed data
- Textract output is **page-oriented**, returning an array of pages, each containing its own blocks.
- In the first parsing attempt, we iterated **page by page**, building a fresh `block_map` for each page and only processing `KEY_VALUE_SET` blocks within that subset.
- Some `KEY_VALUE_SET` blocks rely on relationships that can span across other blocks or require the **global block map** to resolve properly.
- Result: **some KV pairs (like the repeated `ESTADO DE CUENTA EN:` entries) were skipped** because they weren’t fully captured when processing page by page.

### Correct approach to parse KV pairs
1. **Build one global `block_map`**:  
   - Combine all blocks from all pages into a single dictionary keyed by `Id`.  
   - This ensures every relationship reference (e.g., VALUE → WORD) can be resolved.

2. **Process all `KEY_VALUE_SET` blocks globally**:
   - Loop through every block in the global map.
   - Identify those with:
     ```python
     block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block.get("EntityTypes", [])
     ```
   - For each, retrieve:
     - **Key text** → Traverse its `CHILD` relationships.
     - **Value text** → Follow `VALUE` relationship(s) to the corresponding VALUE block(s) and traverse their children.
     - **Position** → Use `block["Geometry"]["BoundingBox"]` (Top & Left normalized coordinates).
     - **Page** → Use `block["Page"]` to know which page the KV pair belongs to.

3. **Save results with all attributes**:
   - Store key, value, position, page, and an optional `"source": "KV"` tag.
   - Example structure:
     ```json
     {
       "key": "ESTADO DE CUENTA EN:",
       "value": "DOLARES",
       "position": {"top": 0.0212, "left": 0.5306},
       "page": 1,
       "source": "KV"
     }
     ```

### Why this works better
- By using a **global map**, all relationships between blocks can be resolved regardless of how Textract groups them internally.
- It avoids partial parsing that can miss KV pairs repeated across pages or linked in non-standard layouts.
- It produces a **complete, page-aware, position-aware** dataset, essential for downstream logic like linking currency markers to tables.

### Key takeaway
**Always build one global block map and process all `KEY_VALUE_SET` blocks globally when extracting key-value pairs from Textract FORMS output.**  
This guarantees completeness and consistency, especially for documents with repeating keys or multi-page templates.

---

## Final Agreed Outcome Schema

{
    "bill_owner": "string | null",
    "product_id": "string | null",
    "bill_date": "string | null",
    "currency_markers": {
        "page_number": "string"
    },
    "tables": [
        {
            "page": "integer",
            "content": [
                ["string", "string", "..."],
                ["string", "string", "..."]
            ]
        }
    ]
}


---


## Final form of how the data flows to the parsing 
┌─────────────────────────────┐
│    Textract FORMS JSON      │
└─────────────┬───────────────┘
              │
              ▼
   ┌────────────────────┐
   │ extract_forms_data │
   └─────────┬──────────┘
             │
             │ Extracts:
             │  - bill_owner (best SEÑOR(A) variant)
             │  - product_id (TARJETA + network detection)
             │  - bill_date (Hasta)
             │  - currency_markers { page -> value }
             ▼
       ┌─────────────┐
       │ forms_data  │
       └─────┬───────┘
             │
┌────────────┴──────────────┐
│   Textract TABLES JSON    │
└─────────────┬─────────────┘
              ▼
   ┌────────────────────┐
   │ extract_tables_data│
   └─────────┬──────────┘
             │
             │ Extracts:
             │  - tables [ { page, content[][] }, ... ]
             ▼
       ┌─────────────┐
       │ tables_data │
       └─────┬───────┘
             │
             ▼
   ┌───────────────────────────┐
   │  build_unified_payload    │
   └─────────────┬─────────────┘
                 │
                 ▼
   ┌──────────────────────────────────────────────┐
   │ Final Payload:                               │
   │ {                                            │
   │   bill_owner,                                │
   │   product_id,                                │
   │   bill_date,                                 │
   │   currency_markers { page -> value },        │
   │   tables [ { page, content[][] }, ... ]      │
   │ }                                            │
   └──────────────────────────────────────────────┘