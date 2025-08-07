# TreelineProxy

**Runtime AI Firewall for LLM Traffic Governance**

Treeline is a containerized sidecar system that intercepts, scores, and governs large language model (LLM) traffic at runtime. Built for security teams, platform engineers, and AI builders who need visibility and control over prompt flows — in real time.

---

## 🚀 Core Capabilities

- 🔒 **TLS MITM Proxy** using `mitmproxy`
- 📊 **Prompt Scoring API** with pluggable rule sets (`regex`, `policy.yaml`)
- ⛔ **Blocking & Enforcement**: Stop prompt injection or token abuse
- 📈 **Traffic Logging**: Scored, tagged, auditable
- 🔁 **Composable Containers**: Deploy via Docker Compose or ECS Fargate
- ✅ **Healthcheck Endpoint** for ALB integration

---

## 🧱 Architecture

```
User → Treeline Proxy (mitmproxy) → Scoring API → OpenAI / Claude / etc
                          ↓
              Score / Block / Log
```

- `sidecar/proxy`: TLS interception & request capture
- `sidecar/scorer`: FastAPI service to apply policy logic
- `score-api/`: Alternate scoring backend with YAML-based policies

---

## ⚙️ Local Dev with Docker Compose

```bash
docker-compose up --build
```

Then configure your app to use `localhost:8080` as an HTTP proxy.

---

## 🧪 Scoring Logic

- Rules defined in `policy.yaml`
- Evaluated against intercepted prompt+completion pairs
- Scoring API returns structured risk data

---

## 🏗️ ECS / Fargate

- See `ecs-task-redacted-defs/` for deployment templates
- Healthcheck container runs separately
- Use ALB with `path=/healthz` for service scaling

---

## 📦 Repo Structure

```
/sidecar
  /proxy          → mitmproxy config
  /scorer         → FastAPI-based scoring logic
/score-api        → Alternative scoring API (YAML policy)
/healthcheck      → Health check endpoint container
/infra, /helm     → Infra-as-code, optional K8s setup
/scripts, /tests  → Utility & test code
```

---

## 📍 Status

**Archived MVP.**  
Originally deployed to AWS ECS with full dual-container sidecar.  
Now preserved for reference and reuse.

---

🧠 Built by [valtirman](https://github.com/valtirman)  
MIT License