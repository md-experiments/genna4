# Deploying Genna to Railway

Genna is structured as a monorepo containing a `frontend/` (Vue 3/Vite + Caddy) and `backend/` (FastAPI). The frontend Caddy server proxies all `/api/*` requests to the backend over Railway's **private network**, so the backend never needs a public domain and does not need to be secured against the internet.

```
Browser → frontend.railway.app/api/... → Caddy (frontend service)
                                              ↓  private network
                                         backend.railway.internal
```

---

## Step 1: Create the Backend Service

1. From your Railway Dashboard, click **New Project** → **Deploy from GitHub repo**.
2. Select your `genna4` repository.
3. Go to **Settings → Build**:
   - **Root Directory**: `/backend`
   - **Builder**: `Nixpacks`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Go to **Variables** and add:
   - `FIREBASE_SERVICE_ACCOUNT` — paste the raw JSON content of your Firebase service account key
5. **Do NOT generate a public domain** for the backend. It only needs to be reachable on the private network.
6. Note the backend service's **name** in Railway (e.g. `genna-backend`) — you'll need it in Step 2.

---

## Step 2: Create the Frontend Service

1. Click **New Service** in the same project and choose the same GitHub repo.
2. Go to **Settings → Build**:
   - **Root Directory**: `/frontend`
   - **Builder**: `Dockerfile` (Railway auto-detects the `Dockerfile` in `/frontend`)
3. Go to **Variables** and add:

   | Variable | Value |
   |----------|-------|
   | `VITE_API_BASE_URL` | *(leave empty — requests are proxied at the same origin)* |
   | `BACKEND_INTERNAL_URL` | `http://<backend-service-name>.railway.internal:$PORT` |
   | `VITE_FIREBASE_API_KEY` | your Firebase web API key |
   | `VITE_FIREBASE_AUTH_DOMAIN` | `your-project.firebaseapp.com` |
   | `VITE_FIREBASE_PROJECT_ID` | your Firebase project ID |
   | `VITE_FIREBASE_STORAGE_BUCKET` | `your-project.appspot.com` |
   | `VITE_FIREBASE_MESSAGING_SENDER_ID` | your sender ID |
   | `VITE_FIREBASE_APP_ID` | your Firebase app ID |

   > **Finding the internal URL**: In the Railway dashboard, open the backend service → **Settings → Networking → Private Networking**. The hostname is shown there (e.g. `genna-backend.railway.internal`). The port is whatever the `PORT` variable is set to in that service (Railway assigns it — check **Variables → PORT**). Example: `http://genna-backend.railway.internal:8080`

4. Generate a **Public Domain** for the frontend service.

---

## Step 3: Firebase Auth Domains

Add your frontend Railway public domain to the **Authorized Domains** list in the Firebase Console under **Authentication → Settings → Authorized Domains**.

---

## Local Development

For local development, both services run directly — no proxy needed:

```bash
# Backend
cd backend && uvicorn main:app --reload --port 8000

# Frontend (in a separate terminal)
cd frontend && npm run dev
```

The frontend defaults to `http://localhost:8000` when `VITE_API_BASE_URL` is not set, and the backend allows CORS from `localhost:5173` / `localhost:4173`.
