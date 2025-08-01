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