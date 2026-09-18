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

## Deployment

The project includes Vercel configuration. It builds the `frontend/` source into
static files and exposes a Python serverless API under `/api/`.

```powershell
npx vercel --prod
```

The deployed demo keeps registration drafts in the founder's browser. Connect a
database before using it for shared, permanent registration records.

### Render

`render.yaml` is included for a Render web-service deployment. Use the project
repository when creating a new Blueprint on Render; it will run
`python backend/server.py` and expose the app on Render's supplied `PORT`.
