# Project Directory

📁 PBA/
├── 📄 LICENSE
├── 📄 Loose Notes.md
├── 📄 README.md
├── 📄 pytest.ini
├── 📄 requirements.txt
├── 📄 routes.txt
├── 📁 audit
│   └── 📁 logs
├── 📁 config
│   └── 📄 bill_templates.json
├── 📁 data
│   ├── 📁 ground_truth
│   │   ├── 📄 ground truth total.md
│   │   └── 📄 ground_truth.json
│   ├── 📁 input_pdfs
│   │   ├── 📁 Bancolombia
│   │   │   ├── 📁 MC
│   │   │   └── 📁 VS
│   │   ├── 📁 Locked Bancolombia
│   │   └── 📁 Unlocked Bancolombia
│   │       └── 📁 Textract Response
│   └── 📁 textract_output
│       ├── 📄 2025-07-22_1035_cb23bdf6_BC - MC - 02 - FEB-2025.pdf.json
│       └── 📄 textract parsed tables (BC - MC - 02 - FEB-2025).md
├── 📁 docs
│   ├── 📄 00 Project Overview.md
│   ├── 📄 01 Development Plan & Milestones.md
│   ├── 📄 02 Project Logbook.md
│   ├── 📄 03 Data Retention & Management Policy.md
│   ├── 📁 architecture
│   │   ├── 📁 00 preliminar files
│   │   │   ├── 📄 2025.06.03 - Draft de Arquitectura.md
│   │   │   └── 📄 2025.06.03 - First Architecture Draft.jfif
│   │   ├── 📁 architecture diagram
│   │   │   ├── 📄 2025.07.17 - Architecture Diagram.drawio.xml
│   │   │   └── 📄 2025.07.18 - Architecture Diagram.PNG
│   │   └── 📁 data model
│   │       └── 📄 preliminary data model notes.md
│   └── 📁 context_maintenance
│       ├── 📄 context_handover_model.md
│       ├── 📄 dev_partner_prompt_chatgpt.md
│       ├── 📄 files_structure_generator_v2.py
│       ├── 📄 project_map.md
│       ├── 📄 session_handover_template.md
│       └── 📁 sessions
│           └── 📄 2025-07-25_handover.md
├── 📁 experiments
│   └── 📁 data extraction
│       ├── 📁 amazon textract
│       │   ├── 📁 history
│       │   ├── 📁 tests
│       │   │   ├── 📁 00 initial tables parsing
│       │   │   ├── 📁 01 tables & forms (same call)
│       │   │   └── 📁 02 forms then tables (different calls)
│       │   └── 📁 tool usage
│       └── 📁 manual extraction
├── 📁 src
│   ├── 📁 core
│   │   └── 📄 extract_expenses.py
│   ├── 📁 db
│   ├── 📁 ingestion
│   │   └── 📄 upload_to_s3.py
│   ├── 📁 llm_interference
│   ├── 📁 notifications
│   └── 📁 textract
│       ├── 📄 parse_textract_output.py
│       └── 📄 trigger_textract.py
└── 📁 tests
    ├── 📄 00 pytest migration plan.md
    ├── 📄 conftest.py
    ├── 📁 fixtures
    │   └── 📁 extraction
    │       ├── 📄 BC - MC - 02 - FEB - 2025 - Ground Truth.xlsx
    │       ├── 📄 extraction_ground_truth.json
    │       ├── 📁 extraction_test_results
    │       │   └── 📄 extracted.json
    │       └── 📄 ground_truth_data_extraction.py
    ├── 📄 test_extract_expenses.py
    ├── 📄 test_parser.py
    ├── 📄 test_textract.py
    ├── 📄 test_upload.py
    └── 📄 test_validate_expenses.py



## Modules & Config Index


### config

- bill_templates.json: # Contains the configuration for current's Bancolombia cc bill format and future new card issuers/bill template so the app is extensive

    * schema:
        {
            "bill_templates": {
                
                "template_version": {
                    "headers": [strs],   # headers that will identify which table to collect expenses from
                    "fields_to_extract": [strs], # The columns collected from the tables of interest
                    "currency_split": {dicts}   # rules to identify which expenses currency from a captured table
                    },
                    
                    "exclude_descriptions": [strs] # Which expenses descriptions to exclude from the collection
                }
        }


### context maintenance/
- files_structure_generator_v2.py:
    * format_arg(arg) -> None  # Format argument with its type annotation if present.
    * extract_functions_and_methods(file_path) -> None  # Extract the functions, methods and their docstrings if present in the python file.
    * generate_markdown_tree(start_path, output_dir) -> None  # Creates the result markdown file with project's structure and functions description.


### src/

- extract_expenses.py:  # Extract and transforms the data collected from textract into two expenses buckets (Foreing & Domestic) for one CC Bill.

    * load_template(template_name: str) -> dict # Loads 'bill_templates.json' that contains the configuration for a specific Card-Issuer/Bill-Template.
    * normalize_value(value: str) -> str # Strips string fields collected from trailing or leading whitespaces.
    * parse_amount(value: str) -> float  # Convert amount string to float, keeping negatives as negatives.
    * parse_date(value: str) -> str # Transforms the date format into a "%Y-%m-%d" strftime.
    * header_matches(expected: list, actual: list) -> bool  # Check if actual table header contains all expected headers in order.
    * classify_currency(table: list, template: dict) -> str  # Determine if table is foreign or domestic based on template currency_split rules.
    * extract_expenses_from_tables(tables: list, template_name) -> dict  # Extract normalized expense rows from parsed tables based on template.

    **Input (tables sample)**
    [["Número de Autorización", "Fecha de Transacción", "Descripción", ...],
    ["123456", "2025-02-01", "Compra Supermercado", "123.45", ...]]

    **Output**
    {"usd_expenses": [{"Número de Autorización": "123456", ...}], "cop_expenses": [...]}

- upload_to_s3.py:  # Uploads and confirms one CC Bill storing into an S3 bucket.
    * upload_file(file_path: str, s3_key: str) -> str  # Uploads a file to the configured S3 bucket.

- parse_textract_output.py: # Reconstructs the raw JSON retrived from textract into readable tables.
    * parse_textract_tables(textract_json: dict) -> list  # Parses Textract JSON output and extracts tables as 2D lists.
    * parse_textract_file(json_file_path: str) -> list  # Load a Textract JSON file and parse its tables.

- trigger_textract.py:  # Initiates a textract asynchronous job to process one CC Bill.
    * run_textract_analysis(s3_key: str, save_to: str, poll_interval: int) -> dict  # Asynchronously analyzes a PDF in S3 using Textract's start_document_analysis.


### tests/

- ground_truth_data_extraction.py # File to manually get the verified ground truth data for testing purposes

- conftest.py: # Pytest config file
    * ground_truth_data() -> None  # Fixture: Load ground truth expense data for validation tests.
    * sample_tables() -> None  # Fixture: Load sample table data as parsed from Textract output JSON.
    * bancolombia_tables() -> None  # Fixture: Load parsed tables for a known Bancolombia CC bill (Feb 2025).

- test_extract_expenses.py # Test extract_expenses.py

- test_parser.py: # Test from parse_textract_output.py

- test_textract.py: # Tests trigger_textract.py

- test_upload.py: # Tests upload_to_s3.py

- test_validation_expenses.py: # Tests precision, recall and accuracy from the transformed data derived from extract_expenses.py vs the ground truth

