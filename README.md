# StartupReady AI registration

A full-stack, 12-step startup registration experience based on the supplied brief. The frontend and backend are intentionally separate.

- **Frontend:** HTML, CSS, and JavaScript
- **Backend:** Python standard library (`http.server`), with JSON auto-save API

## Run it

```powershell
cd backend
python server.py
```

Open `http://localhost:3000`. Registration progress is saved to `backend/data/registration.json` automatically.

## Render deployment

`render.yaml` deploys the project as a Python web service. Render runs
`python backend/server.py`, which serves both the frontend and API from the
same service. No generated `public/` folder or build script is required.

The deployed demo keeps registration drafts in the founder's browser. Connect a
database before using it for shared, permanent registration records.
