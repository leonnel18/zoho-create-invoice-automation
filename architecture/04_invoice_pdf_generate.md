# SOP-04: Invoice PDF Generate
**Tool:** `tools/generate_pdf.py`

## Goal
Download the generated invoice PDF from Zoho Books and save to OUTPUT_FOLDER.

## API Call
`GET /invoices/{invoice_id}?organization_id={org_id}&accept=pdf`
Response: binary PDF content (Content-Type: application/pdf)

## Output Filename
`{source_file}_ZohoInvoice_{invoice_date}.pdf`

## Error Handling
- Non-200 response: raise exception — orchestrator logs to DB
- Empty response body: raise ValueError
- OUTPUT_FOLDER does not exist: create it automatically
