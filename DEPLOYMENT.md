# Deploying Genna to Railway

Genna is structured as a monorepo containing a `frontend/` (Vue 3/Vite) and `backend/` (FastAPI). Deploying this cleanly on Railway involves creating two separate services linked to the same GitHub repository.

## Step 1: Create the Backend Service

1. From your Railway Dashboard, click **New Project** -> **Deploy from GitHub repo**.
2. Select your `genna4` repository.
3. Once the service is created, go to **Settings** -> **Build**:
   - Set the **Root Directory** to `/backend`
   - Set the **Builder** to `Nixpacks`
   - Set the **Start Command** to `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Go to **Variables** and add the variables defined in `backend/.env.example`:
   - `OPENAI_API_KEY`
   - `OPENROUTER_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `GOOGLE_APPLICATION_CREDENTIALS` (Paste the raw JSON content of your Firebase Service Account here. Railway will securely inject it).
5. Generate a Public Domain for the backend service (e.g., `genna-backend.up.railway.app`).

## Step 2: Create the Frontend Service

1. Click **New Service** in the same project, and choose your GitHub repo again.
2. Go to **Settings** -> **Build**:
   - Set the **Root Directory** to `/frontend`
   - Set the **Builder** to `Nixpacks`
   - Build Command should natively be detected as `npm run build`
   - Set the **Start Command** to `npm run preview -- --host 0.0.0.0 --port $PORT` (Or, if you prefer NGINX, setup a static deploy).
3. Go to **Variables** and add the frontend variables from `frontend/.env.example`, including the new `VITE_API_BASE_URL` pointing to the public domain of your backend service.
   - `VITE_FIREBASE_API_KEY`
   - `VITE_FIREBASE_PROJECT_ID`
   - `VITE_API_BASE_URL=https://<your-backend-domain>`
4. Generate a Public Domain for the frontend service.

## Step 3: Firebase Auth Domains
Don't forget to add your generated Frontend Railway domain to the **Authorized Domains** list in your Firebase Console (Authentication -> Settings -> Authorized Domains) so that Google Sign-In and other auth systems work perfectly.
