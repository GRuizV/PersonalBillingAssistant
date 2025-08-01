

**Bill Data Model Field Source Definition**

- `user_owner`: The user authenticated owning it's own base → Currently will be a `<user_placeholder>` until Authentication is implemented
- `bill_original_name` → pdf file name.
- `s3_bill_name` → is it necessary?.
- `bill_id` → Built post processing from `bill_owner`+`bill_owner`+`bill_date`
- `bill_owner` → Textract "FORMS".
- `product_id` → Textract "FORMS".
- `bill_date` → Textract "FORMS".
- 








