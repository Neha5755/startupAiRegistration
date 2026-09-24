# Channapatna Gifts

A personalised gift catalogue with 13 gift products, bold pricing, and a
custom order request form. Customers can include a message, date, and optional
image, video, or PDF when requesting a personalised product.

- **Frontend:** HTML, CSS, and JavaScript
- **Backend:** Python standard library (`http.server`) with multipart uploads

## Run it

```powershell
cd backend
python server.py
```

Open `http://localhost:3000`. Order requests and uploaded files are saved under
`backend/data/` during local development.

## Render deployment

`render.yaml` deploys the project as a Python web service. Render runs
`python backend/server.py`, which serves both the storefront and API from the
same service. Connect durable storage and email delivery before accepting real
customer orders in production.
