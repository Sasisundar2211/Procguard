# 🚀 Vercel Deployment Guide for ProcGuard MVP

This guide details how to deploy your **Full-Stack Application** (Next.js Frontend + FastAPI Backend) to Vercel as a single monorepo.

## 1. Prerequisites

1.  **GitHub Repository**: Push this entire codebase to a GitHub repository.
2.  **Vercel Account**: Sign up at [vercel.com](https://vercel.com).
3.  **Cloud Database**: Vercel does not host databases. You need a PostgreSQL database accessible from the internet.
    *   **Recommended**: [Neon](https://neon.tech), [Supabase](https://supabase.com), or [Azure PostgreSQL](https://azure.microsoft.com).
    *   **Connection String**: You will need the `postgresql://...` URL.

## 2. Project Structure Verification

Ensure your project matches this structure (already configured):
*   `/vercel.json` (Configuration file created for you)
*   `/app/main.py` (Backend Entrypoint, configured with `root_path="/api"`)
*   `/procguard-ui/` (Frontend)

## 3. Deployment Steps

### Step A: Import Project in Vercel
1.  Go to **Vercel Dashboard** > **Add New...** > **Project**.
2.  Import your GitHub Repository.
3.  **IMPORTANT**: Leave "Root Directory" as `./` (the default). Do **NOT** select `procguard-ui`. We are deploying the whole repo.

### Step B: Configure Build Settings
Vercel reads `vercel.json`, so it generally knows what to do. However, verify:
*   **Framework Preset**: Select "Other" or leave default (Next.js might be auto-detected, but we are overriding via `vercel.json`).
*   **Root Directory**: `.`

### Step C: Environment Variables (CRITICAL)
Add the following variables in the Vercel Project Settings:

| Variable Name | Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://user:pass@host:port/dbname` | Your Cloud Postgres Connection String |
| `NEXT_PUBLIC_API_URL` | `/api` | **CRITICAL**: Use relative path so Frontend calls Backend via Vercel Rewrites |
| `VERCEL` | `1` | Triggers the `root_path="/api"` logic in FastAPI (Vercel sets this automatically usually, but good to add if unsure) |
| `PYTHON_VERSION` | `3.9` | Ensure compatible Python runtime |

### Step D: Ignite Deployment
Click **Deploy**.

## 4. How it Works (Under the Hood)

1.  **Routing**: The `vercel.json` file tells Vercel:
    *   Send any request starting with `/api` -> `app/main.py` (Python Serverless Function).
    *   Send everything else -> `procguard-ui` (Next.js Static/Edge).
2.  **Frontend**: The Next.js app builds and serves the UI.
3.  **Backend**: The FastAPI app spins up as a Lambda function on demand.
4.  **CORS**: Since both live on the same domain (e.g., `procguard.vercel.app`), **CORS is not an issue**. Calls to `/api/...` are same-origin.

## 5. Troubleshooting "Backend Offline"

If the app says "Backend Offline" after deployment:
1.  Check **Vercel Function Logs** (Under "Logs" tab).
2.  Ensure `DATABASE_URL` is correct and allows connections from Vercel IPs (0.0.0.0/0 whitelist often needed for Serverless).
3.  Verify `NEXT_PUBLIC_API_URL` is set to `/api`.

## 6. Local Development vs. Production

*   **Local**: continue using `npm run dev` and `uvicorn`. API URL is `http://127.0.0.1:8000`.
*   **Production (Vercel)**: API URL is `/api`.

This setup gives you the best of both worlds: Full-Stack Vercel experience with Python and React.
