# Bill Template Development Guide

## Purpose
This document explains how to add and maintain bill templates for the Personal Billing Assistant (PBA).  
Templates define how to extract **metadata** (e.g., bill owner, product ID, billing date) and **expense tables** from Textract outputs.

These templates are used by:
- **Parser** → Reads Textract FORMS and TABLES outputs and builds a unified structured payload.
- **Transformer** → Uses that payload to normalize expense rows and metadata for downstream processing.

---

## Purpose of `bill_templates.json`
The file `config/bill_templates.json` stores all template definitions.  
Each key (e.g., `bancolombia_v1`) represents one supported bill format.

A template has two main sections:
1. **forms_to_extract** → Defines which key-value pairs to capture from the FORMS Textract response.
2. **tables_extraction** → Defines how to detect and process the expense tables.

---

## Template JSON Schema
```json
{
  "bill_templates": {
    "<template_name>": {
      "forms_to_extract": {
        "bill_owner": "<Key text for account owner>",
        "product_id": "<Key text for product id>",
        "bill_date": "<Key text for billing date>",
        "currency_markers": "<Key text for per-page currency marker>"
      },
      "tables_extraction": {
        "headers": [
          "<header 1>",
          "<header 2>",
          "... more headers"
        ],
        "fields_to_extract": [
          { "original": "<Column Header>", "english": "<Normalized field name>" }
        ],
        "exclude_descriptions": [
          "<transaction descriptions to ignore>"
        ]
      }
    }
  }
}
```


---

## Example: Adding a new template for bankx_v1

```json
{
  "bill_templates": {
    "bankx_v1": {
      "forms_to_extract": {
        "bill_owner": "CLIENTE:",
        "product_id": "PRODUCTO:",
        "bill_date": "Fecha de Corte:",
        "currency_markers": "MONEDA DE CUENTA:"
      },
      "tables_extraction": {
        "headers": [
          "Autorización",
          "Fecha",
          "Detalle",
          "Monto",
          "Cargos y Abonos"
        ],
        "fields_to_extract": [
          { "original": "Autorización", "english": "authorization_number" },
          { "original": "Fecha", "english": "transaction_date" },
          { "original": "Detalle", "english": "description" },
          { "original": "Monto", "english": "amount" },
          { "original": "Cargos y Abonos", "english": "charges_and_credits" }
        ],
        "exclude_descriptions": [
          "PAGO WEB",
          "ABONO AUTOMATICO"
        ]
      }
    }
  }
}
```

### Steps to Add a New Template

1. Identify the keys and headers in the bill’s PDF output from Textract (FORMS & TABLES).
2. Fill out forms_to_extract with the appropriate keys for metadata.
3. Define the table headers, map columns in fields_to_extract, and list descriptions to ignore.
4. Add the new entry to config/bill_templates.json.
5. Test using sample bills and validate output with the parser and transformer.


---

## Notes

* Keep template names descriptive and versioned (e.g., bancolombia_v1).
* Document any template-specific quirks in the project logbook.
* When in doubt, run Textract manually and check raw JSON to confirm keys and headers.