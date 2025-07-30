# Results

**Experiment:** 01 exp_extract_tables_and_forms_combined_texjob
**Date:** 2025-07-30

- The "FORMS" calling from Textract does solves collecting:

    - "ESTADO DE CUENTA EN: DOLARES" → Textract "FORMS". -> Two lines:
        - [line] ESTADO DE CUENTA EN:
        - [line] DOLARES

    - "ESTADO DE CUENTA EN: PESOS" → Textract "FORMS". -> Two lines:
        - [line] ESTADO DE CUENTA EN:
        - [line] PESOS

    - "bill_owner" → Textract "FORMS". -> [line] SEÑOR (A): JUAN SEBASTIAN RUIZ VILLA

    - "product_id" → Textract "FORMS". -> Two lines:
        - [line] TARJETA:
        - [line] 3667
           
    - "bill_date" → Textract "FORMS". -> [line] Hasta: 30/01/2025


- Calling both "TABLES" and "FORMS" in the same Textrack job messed up badly the tables reconstruction. 


---


**Experiment:** 02 exp_extract_only_tables_from_combined_texjob
**Date:** 2025-07-30

- When reconstructing only the tables from the raw_json in the combined "TABLES" and "FORMS" it was demonstrated that it corrupts expenses tables.

    So the best call is to make two separated callings to textract, one for the "TABLES" to secure expenses extraction and another for "FORMS", probably first, to collect some important data and the absolute position of "ESTADO DE CUENTA EN: DOLARES" to correct the currency assignment heuristics.