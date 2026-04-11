# ── Build ─────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ── Serve ─────────────────────────────────────────────────────────────────────
# Caddy serves the static bundle and reverse-proxies /api/* to the backend
# over Railway's private network (no public backend URL needed).
FROM caddy:2-alpine
COPY --from=builder /app/dist /srv
COPY Caddyfile /etc/caddy/Caddyfile
