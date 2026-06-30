# syntax=docker/dockerfile:1

# ============================================================================
# Teplolux AI CRM Assistant — production Docker image (multi-stage)
# ============================================================================

# ---- Stage 1: dependencies -------------------------------------------------
FROM node:22-alpine AS deps
WORKDIR /app
# Prisma needs OpenSSL at install/generate time.
RUN apk add --no-cache openssl
COPY package*.json ./
COPY prisma ./prisma
# Install all deps (incl. dev) for building; postinstall runs `prisma generate`.
RUN npm ci

# ---- Stage 2: build --------------------------------------------------------
FROM node:22-alpine AS build
WORKDIR /app
RUN apk add --no-cache openssl
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run prisma:generate \
  && npm run build \
  && npm prune --omit=dev

# ---- Stage 3: runtime ------------------------------------------------------
FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
RUN apk add --no-cache openssl wget \
  && addgroup -S nodejs && adduser -S nodejs -G nodejs

# Production artefacts only.
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY --from=build /app/prisma ./prisma
COPY --from=build /app/package.json ./package.json
COPY docker/entrypoint.sh ./docker/entrypoint.sh
RUN chmod +x ./docker/entrypoint.sh && mkdir -p logs && chown -R nodejs:nodejs /app

USER nodejs
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:3000/health || exit 1

ENTRYPOINT ["./docker/entrypoint.sh"]
CMD ["node", "dist/main.js"]
