FROM node:20-bookworm-slim AS deps
WORKDIR /app
COPY package.json pnpm-workspace.yaml ./
COPY apps/web/package.json apps/web/package.json
RUN corepack enable && pnpm install --filter @demomotion/web --frozen-lockfile=false

FROM node:20-bookworm-slim AS builder
WORKDIR /app
# NEXT_PUBLIC_* is inlined at build time, so these must be provided here (not
# just as Cloud Run runtime env vars).
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
# Public URL prefilled as the recording target (e.g. the deployed demo-app), so
# the dashboard and /webmcp point at a page that actually renders out of the box.
ARG NEXT_PUBLIC_DEFAULT_DEMO_URL=
ENV NEXT_PUBLIC_DEFAULT_DEMO_URL=${NEXT_PUBLIC_DEFAULT_DEMO_URL}
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/apps/web/node_modules ./apps/web/node_modules
COPY . .
RUN corepack enable && pnpm --filter @demomotion/web build

FROM node:20-bookworm-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/apps/web/.next/standalone ./
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder /app/apps/web/public ./apps/web/public
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
