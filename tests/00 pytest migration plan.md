# Pytest Migration Plan – PBA Project

## Purpose
Migrate the current ad-hoc test scripts into a structured, maintainable, and CI/CD-ready Pytest test suite.

---

- **Documentation**
  - Add a short README in `/tests` to describe:
    - How to run all tests.
    - How to run only integration tests.
    - Test data sources.


---


## How this test section should looks like

tests/
├── unit/              # Pure unit tests (isolated, fast, mock-heavy)
│   └── test_parser.py
├── integration/       # Real inputs, test full pipeline, slower
│   └── test_parser_live.py
├── manual/            # Developer-run ad hoc runners
│   └── test_parse_manual.py
├── conftest.py        # Shared fixtures
└── fixtures/          # Frozen test JSONs or templates
    └── textract_response.json