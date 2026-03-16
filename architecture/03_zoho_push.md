# SOP-03: Zoho Push
**Tool:** `tools/zoho_push.py`

## Goal
Push a parsed invoice record to Zoho Books. Returns zoho_invoice_id.

## Flow
1. Get fresh access token via refresh token
2. Lookup or create customer "Generic" in Zoho Contacts
3. For each line item: lookup item by name → create if not found
4. POST invoice with customer_id + line_items
5. Return invoice_id

## API Calls
| Step | Method | Endpoint |
|------|--------|----------|
| Token | POST | `https://accounts.zoho.{region}/oauth/v2/token` |
| Find customer | GET | `/contacts?search_text=Generic` |
| Create customer | POST | `/contacts` |
| Find item | GET | `/items?search_text={name}` |
| Create item | POST | `/items` |
| Create invoice | POST | `/invoices` |

## Item Create Payload
```json
{ "name": "item_name", "rate": 1.00, "unit": "KG" }
```

## Invoice Create Payload
```json
{
  "customer_id": "xxx",
  "date": "YYYY-MM-DD",
  "line_items": [
    { "item_id": "xxx", "name": "xxx", "quantity": 1.0, "unit": "KG", "rate": 1.00 }
  ]
}
```

## Error Handling
- Item create fails (e.g., invalid unit): retry without unit field
- Customer not found and create fails: raise exception — do not create orphan invoice
- Invoice create fails: raise exception — DB status set to 'error' by orchestrator
