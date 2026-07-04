# Deployment Guide (Vercel + Render)

## Important limitation first

Once the backend runs on Render (in the cloud), `kubectl` inside it can only reach
Kubernetes clusters whose API server is reachable from the internet — e.g. a
managed cluster (EKS/GKE/AKS/DigitalOcean) with a public/allowed endpoint.

It will **not** be able to reach your local `kind-broken-demo` or
`kind-kubernetes-demo-cluster` clusters, since those only exist inside Docker on
your own machine. To investigate a real cluster from the deployed app, you'll
need to give the deployed backend a kubeconfig for a cloud-reachable cluster
(see "Adding a kubeconfig" below).

---

## 1. Deploy the backend to Render

1. Go to https://dashboard.render.com
2. Click **New +** → **Blueprint**
3. Connect your GitHub account if you haven't, then select the
   `ShreyaSaha18/AI-Kubernetes-Agent` repo
4. Render will detect `render.yaml` at the repo root and propose one service:
   `ai-kubernetes-agent-backend`
5. When prompted, set the **OPENROUTER_API_KEY** secret to your OpenRouter key
   (`OPENROUTER_MODEL` already defaults to `openrouter/auto`)
6. Click **Apply** / **Deploy**
7. Once live, copy the service URL, e.g. `https://ai-kubernetes-agent-backend.onrender.com`
8. Verify it's up: open `<that URL>/health` — should return `{"status":"healthy",...}`

Note: Render's free tier spins the service down after inactivity, so the first
request after idling can take ~30-60s to respond.

## 2. Deploy the frontend to Vercel

1. Go to https://vercel.com/shreya-sahas-projects
2. Click **Add New** → **Project**
3. Import `ShreyaSaha18/AI-Kubernetes-Agent`
4. Set **Root Directory** to `frontend` (important — this is a monorepo)
5. Framework preset should auto-detect as **Next.js**
6. Add an Environment Variable:
   - `NEXT_PUBLIC_API_BASE_URL` = the Render backend URL from step 1.7 above
     (no trailing slash, e.g. `https://ai-kubernetes-agent-backend.onrender.com`)
7. Click **Deploy**
8. Once live, Vercel gives you a URL like `https://ai-kubernetes-agent.vercel.app`

## 3. Smoke test

1. Open the Vercel URL
2. Sign up for an account
3. You should see the dashboard load (cluster list will be empty/error unless
   you've added a kubeconfig to the Render backend — see below)

---

## Adding a kubeconfig to the deployed backend (optional)

To let the deployed backend investigate a real cluster:

1. In Render, go to your service → **Environment** → **Secret Files**
2. Add a secret file at path `/root/.kube/config` containing the kubeconfig
   for a cluster whose API server is reachable from the internet
3. Redeploy — `entrypoint.sh` will pick it up automatically on container start

Do not put a kubeconfig for a local `kind` cluster here — it won't be reachable
from Render's network no matter what.
