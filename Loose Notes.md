# Loose Notes


## Next:

- Work on the currency identification heuristics. →  Document in the PJ Logbook.
    * "ESTADO DE CUENTA EN: DOLARES" y "ESTADO DE CUENTA EN: PESOS" para diferenciar las tablas.
    * El nombre del usuario. →  Para almacenar el modelo de datos para la entidad "EXTRACTO" definido.
    * El ID del producto. →  Para almacenar el modelo de datos para la entidad "EXTRACTO" definido.


        1. Comparar los JSON que se recibe de "TABLES" y de "DOCUMENTS" para ver si el actual de "TABLES" nos sirve para conseguir:
            - "ESTADO DE CUENTA EN: DOLARES" → Textract "FORMS".
            - "ESTADO DE CUENTA EN: PESOS" → Textract "FORMS".
            - "bill_owner" → Textract "FORMS".
            - "product_id" → Textract "FORMS".
            - "bill_date" → Textract "FORMS". 

            - ID del extracto →  Textract aún no trae un decodificador de Barcodes, el único rastro de ID del extracto es, en el nombre del documento: Para "Extracto_774507892_202501_TARJETA_MASTERCARD_3667", el ID del extracto sería "774507892".
                * Una alternativa es armar un ID de extracto con la combinación de "bill_owner"+"fecha"+"producto", para no depender de las políticas de nomenclatura de BANCOLOMBIA.
             
            - "product_id" → Textract si tiene como conseguir esto (Posiblemente con "FORMS") pero, nos podemos ahorrar ese pedazo del parsing igual que con el ID del extracto: Con en el nombre del documento: Para "Extracto_774507892_202501_TARJETA_MASTERCARD_3667", el ID del producto sería "TARJETA_MASTERCARD_3667".

            - Fecha del extracto → Textract si tiene como conseguir esto (Posiblemente con "FORMS") pero, nos podemos ahorrar ese pedazo del parsing igual que con el ID del extracto: Con en el nombre del documento: Para "Extracto_774507892_202501_TARJETA_MASTERCARD_3667", el ID del producto sería "202501" con el formato "AAAAMM".

                **Pregunta filosófica:** Ahorrarnos ahora estos pedazos del parsing puede implicar luego un dolor de cabeza, porque si BANCOLOMBIA su convención de nombres, vamos a tener que tocar el código para ahí sí hacer el parsing.


            **Bill Data Model Field Source Definition**
            - `user_owner`: The user authenticated owning it's own base → Currently will be a `<user_placeholder>` until Authentication is implemented
            - `bill_id` → Built post processing from `bill_owner` + `bill_owner`+`bill_date`
            - `bill_owner` → Textract "FORMS".
            - `product_id` → Textract "FORMS".
            - `bill_date` → Textract "FORMS".
            - `bill_original_name` → pdf file name.
            - `s3_bill_name` → is it necessary?.






- Work on the E-R Diagram and the Data model.

- Work on the JSON retention policy: How to make sure we erase the JSON after the CC Bill is added to the DB? -> Document in the PJ Logbook.

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


