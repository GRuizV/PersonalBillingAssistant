# Pytest Migration Plan – PBA Project

## Purpose
Migrate the current ad-hoc test scripts into a structured, maintainable, and CI/CD-ready Pytest test suite.

---

## Completed
- **Pytest framework setup:**
  - Installed `pytest` and `pytest-cov`.
  - Added `pytest.ini` for discovery and consistent output.
- **Shared fixtures file (`conftest.py`)** created with:
  - `ground_truth_data()`: Loads ground truth JSON for validation.
  - `sample_tables()`: Loads parsed Textract tables.
- **`test_upload.py` migrated**:
  - Uses Pytest structure.
  - Runs a real integration test to upload a file and confirm presence in S3.
  - Maintains manual runner for IDE testing.

---

## Pending Migration Steps
1. **`test_parser.py` (Textract parsing tests)**
   - Use `sample_tables` fixture.
   - Validate:
     - Output structure is `list[list]`.
     - Table headers and rows are correctly extracted.

2. **`test_extract_expenses.py` (Expense transformation tests)**
   - Most extensive migration:
     - Validate:
       - Safe-case **English** keys.
       - Date normalization (`yyyy-mm-dd`).
       - Exclusion of payment rows.
     - Use parametrization for multiple sample bills when available.
     - Update or add new fixtures if needed for multiple input scenarios.

3. **`test_validation_expenses.py` (Precision & recall metrics)**
   - Convert to Pytest structure.
   - Add controlled sample with expected TP/FP/FN counts.
   - Evaluate if fuzzy matching tolerance (e.g., description similarity) needs a separate test.

4. **`test_textract.py` (Textract trigger)**
   - Currently requires AWS integration.
   - Decide between:
     - Keeping it as a real integration test (requires credentials and real S3 data).
     - Mocking AWS calls using libraries like `moto` for isolated testing.

5. **New Fixtures**
   - Split fixtures for:
     - **Ground truth (per bill)**.
     - **Multiple sample bills** (once added).
   - Document fixtures with docstrings for future project map generation.

---

## Recommendations for a Robust Test Suite
- **Organize Tests by Module**
  - Keep one test file per module (`test_<module>.py`).
  - Add docstring to each test file describing its scope.

- **Use Fixtures for Common Data**
  - Avoid repeating file loads or setup logic inside each test.
  - Centralize sample data setup in `conftest.py`.

- **Parametrize Tests**
  - Example: test date parsing for multiple formats.
  - Example: run transformation tests on multiple bills.

- **Separate Unit and Integration Tests**
  - Unit tests: Run by default (fast, isolated).
  - Integration tests: Marked with `@pytest.mark.integration`, run manually or in specific CI jobs.

- **Coverage Tracking**
  - Run:
    ```bash
    pytest --cov=src tests/
    ```
  - Target initial **70%+ coverage**, increase as features stabilize.

- **Documentation**
  - Add a short README in `/tests` to describe:
    - How to run all tests.
    - How to run only integration tests.
    - Test data sources.

---

## Next Checkpoint
- Re-engage on Pytest migration after **Phase 1 Development Plan** is complete.
- Start migration with **`test_parser.py`** as it’s the least complex and verifies fixture structure before migrating heavier tests.