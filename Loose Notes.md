# Loose Notes


## Next:

- Correct the parsing logic.
    * Review upstream how the recent learning change the current modules process.
        - The bill should be uploaded with its regular name, and when updating, if already in existance, it should validates whether replace it or work with the current.
    * Build the test for the extraction → The pytest fixture is the `unified_bill_payload.json` from the '02 ... different calls' experiment.
    * Adjust the extraction logic accordingly.

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


