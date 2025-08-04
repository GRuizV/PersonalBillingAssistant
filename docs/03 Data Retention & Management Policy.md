# Data Retention & Management Policy – Personal Billing Assistant (PBA)

---

## 1. Purpose
This document defines how data produced or consumed by the Personal Billing Assistant (PBA) 
is retained, cleaned, and managed. It ensures compliance with privacy, security, 
and operational best practices.

---

## 2. Scope
- **Applies to**: All data generated or stored by the PBA pipeline:
  - Uploaded credit card bill PDFs.
  - Extracted intermediate data (Textract raw output, unified extracted payloads).
  - Normalized expense data stored in the database.
- **Does not apply to**: Logs (covered in `/docs/logging_policy.md` if applicable).

---

## 3. Retention Rules

### 3.1 Raw Textract JSON Output
- **Description**: The raw JSON responses returned directly from Amazon Textract (FORMS and TABLES jobs).
- **Policy**: 
  - **Not stored** in production workflows.
  - Temporarily available only during development or debugging.
  - Deleted immediately after transformation into unified extracted payloads.

### 3.2 Unified Extracted Payloads
- **Description**: Normalized intermediate data containing:
  - `bill_owner`, `product_id`, `bill_date`
  - `currency_markers`
  - Parsed tables (expenses)
- **Policy**:
  - Stored in audit folder (`/audit` bucket/prefix).
  - **Retention period**: 90 days.
  - **Cleanup mechanism**: Automated (cron or AWS Lambda) job deletes all payloads older than 90 days.
  - **Purpose**: Audit and troubleshooting without needing to rerun Textract.

### 3.3 Uploaded Bill PDFs
- **Description**: Original credit card bill PDF uploaded by the user.
- **Policy**:
  - Always stored in S3 as the source of truth.
  - **Duplicate handling**:
    - If an identical file is uploaded:
      - Current behavior: CLI prompt asks whether to skip or replace and rerun pipeline.
      - **Future behavior**: Prompt delivered via WhatsApp once AWS Lambda is integrated.

### 3.4 Database Records
- **Description**: Normalized expenses and bill metadata stored in the database.
- **Policy**:
  - No automatic expiration (kept as long as the user account exists).
  - User-level deletion possible via account management (future feature).

---

## 4. Security & Access
- S3 buckets storing PDFs and audit payloads use IAM policies restricting access to PBA services.
- Data at rest encrypted using AWS-managed keys.
- Audit payloads and database data are accessible only to authorized roles.

---

## 5. Future Improvements
- **WhatsApp-based duplicate prompt** replacing CLI.
- **Middleware cleanup service** to automate 90-day retention policy.
- Optional encryption-at-rest for extracted payloads stored in audit folder.

---

_Last Updated: 2025-08-04_