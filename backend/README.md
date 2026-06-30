# Teplolux AI CRM Assistant

> Enterprise, multi-channel CRM platform for **Teplolux**. Telegram is the first
> communication channel; the architecture is built to grow into amoCRM, an AI
> assistant, product catalog, SAP/1C, analytics, WhatsApp, Instagram, Facebook
> Messenger and website live chat.

Built with **NestJS + TypeScript** on **Node.js 22**, **PostgreSQL** (via
**Prisma**), **Redis**, **Winston**, **Zod** and **Swagger** — following Clean
Architecture, Domain-Driven Design, SOLID, the Repository pattern and
Dependency Injection.

---

## Table of contents

- [Architecture](#architecture)
- [Folder structure](#folder-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Environment](#environment)
- [Database](#database)
- [Running locally](#running-locally)
- [Docker](#docker)
- [Telegram & webhook](#telegram--webhook)
- [Health check](#health-check)
- [API documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Future modules](#future-modules)

---

## Architecture

The application is a modular monolith designed for a clean future split into
microservices. Each concern is isolated:

- **Infrastructure modules** (global): configuration, logging, database, cache.
- **Operational modules**: health checks.
- **Channel/feature modules**: `telegram` (active), with `amocrm`, `users`,
  `chat`, `auth` prepared as architecture placeholders.

Key principles applied:

| Principle               | Where                                                                 |
| ----------------------- | --------------------------------------------------------------------- |
| Clean Architecture      | Controllers → services → repositories; framework kept at the edges.   |
| Repository pattern      | `*.repository.ts` encapsulate all Prisma access.                      |
| Dependency Injection    | Everything is a provider; abstractions injected via tokens.           |
| Open/Closed             | Command handlers register via the `COMMAND_HANDLERS` token — no `switch`. |
| Dependency Inversion    | `AmoCrmPort` defines the integration contract before the adapter exists. |
| Config validation       | Zod validates every env var at boot; invalid config aborts startup.   |
| Centralised errors/logs | Global exception filter + named `LogEvent` constants.                 |

### Request flow (Telegram)

```
Telegram → POST /webhook/telegram
         → TelegramWebhookGuard (secret-token, constant-time compare)
         → ZodValidationPipe (update shape)
         → Controller acknowledges 200 OK immediately
         → TelegramUpdateService (dispatcher)
             ├── upsert TelegramUser            (TelegramUserService → repository)
             ├── persist inbound ChatMessage    (ChatMessageRepository)
             ├── route command → CommandHandler (Map lookup)
             └── route callback → TelegramCallbackService
         → TelegramResponderService sends reply + persists outbound ChatMessage
```

---

## Folder structure

```
backend/
├── prisma/
│   └── schema.prisma            # TelegramUser, ChatMessage, Conversation
├── src/
│   ├── main.ts                  # Bootstrap: helmet, CORS, Swagger, prefix, shutdown
│   ├── app.module.ts            # Composition root
│   ├── config/                  # Zod env validation + typed AppConfigService
│   ├── logger/                  # Winston setup + named LogEvent constants
│   ├── database/                # PrismaModule + PrismaService
│   ├── redis/                   # RedisModule + RedisService
│   ├── health/                  # GET /health (db, redis, version, uptime)
│   ├── common/
│   │   ├── constants/           # App name/version
│   │   ├── exceptions/          # DomainException + typed errors
│   │   ├── filters/             # Global AllExceptionsFilter
│   │   ├── guards/              # TelegramWebhookGuard
│   │   ├── interceptors/        # LoggingInterceptor
│   │   └── pipes/               # ZodValidationPipe
│   └── modules/
│       ├── telegram/            # Active channel (controllers/services/handlers/...)
│       ├── amocrm/              # Placeholder + AmoCrmPort
│       ├── users/  chat/  auth/ # Placeholders
├── test/                        # e2e tests
├── docker/                      # entrypoint.sh
├── Dockerfile                   # Multi-stage production image
├── docker-compose.yml           # backend + postgres + redis
└── .env.example
```

---

## Requirements

- **Node.js ≥ 22** and npm
- **PostgreSQL 14+**
- **Redis 6+**
- (optional) **Docker** & **Docker Compose**

---

## Installation

```bash
cd backend
npm install            # also runs `prisma generate`
cp .env.example .env   # then edit values
```

---

## Environment

All configuration lives in `.env` and is **validated with Zod at startup** — the
application refuses to boot if anything is missing or malformed. See
[`.env.example`](./.env.example) for the full, documented list. Highlights:

| Variable                  | Description                                            |
| ------------------------- | ------------------------------------------------------ |
| `DATABASE_URL`            | PostgreSQL connection string (Prisma).                 |
| `REDIS_HOST` / `REDIS_PORT` | Redis connection.                                    |
| `TELEGRAM_BOT_TOKEN`      | Bot token from @BotFather.                              |
| `TELEGRAM_WEBHOOK_SECRET` | Secret token validated on every webhook call.          |
| `APP_BASE_URL`            | Public URL used to register the webhook.               |
| `JWT_SECRET`              | ≥ 32 chars; reserved for the future admin/dealer auth. |

---

## Database

```bash
# Create & apply a migration in development
npm run prisma:migrate

# Apply migrations in production / CI
npm run prisma:deploy

# Inspect data
npm run prisma:studio
```

The schema models `TelegramUser`, `ChatMessage` and a channel-aware
`Conversation` table, ready for the unified multi-channel inbox.

---

## Running locally

```bash
npm run start:dev      # watch mode
npm run start:prod     # after `npm run build`
```

The server listens on `PORT` (default `3000`).

---

## Docker

```bash
cd backend
cp .env.example .env   # fill in TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_SECRET, ...
docker compose up --build
```

This starts three containers — **backend**, **postgres**, **redis** — with
healthchecks, named volumes and ordered startup. The backend entrypoint runs
`prisma migrate deploy` before launching.

---

## Telegram & webhook

The bot is **webhook-only** (never polling).

- Endpoint: `POST /webhook/telegram`
- Authenticated via the `X-Telegram-Bot-Api-Secret-Token` header
  (`TELEGRAM_WEBHOOK_SECRET`), compared in constant time.

**Register the webhook** either automatically or manually:

- Automatic: set `TELEGRAM_SET_WEBHOOK_ON_STARTUP=true` and ensure
  `APP_BASE_URL` + `TELEGRAM_WEBHOOK_PATH` are correct.
- Manual:

  ```bash
  curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
    -H 'Content-Type: application/json' \
    -d '{
      "url": "https://your-domain/webhook/telegram",
      "secret_token": "<TELEGRAM_WEBHOOK_SECRET>",
      "allowed_updates": ["message", "edited_message", "callback_query"]
    }'
  ```

On startup, when `TELEGRAM_SET_WEBHOOK_ON_STARTUP=true`, the app automatically
(1) registers the webhook, (2) publishes the command menu (`setMyCommands`) and
(3) **verifies reachability** by reading `getWebhookInfo` back from Telegram —
logging the registered URL, the pending-update backlog and any last delivery
error. A failure here is logged, never fatal.

**Supported commands:** `/start`, `/help`, `/catalog`, `/service`, `/dealer`,
`/operator`, `/contact`, `/location` — each with its own handler. `/start`
greets the user and shows the inline menu (🏠 Boilers, 🔥 Radiators,
♨️ Floor Heating, 🛠 Service, 🤝 Become Dealer, 👨 Contact Operator, plus
📞 Contact / 📍 Location). Pressing any inline button **edits the current
message in place** (no new messages), and **⬅️ Back to menu** restores the
personalised main menu.

### Local testing

Telegram only delivers webhooks to a public HTTPS URL, so expose your local
server through a tunnel:

```bash
# 1) Start infra + app
docker compose up -d postgres redis
npm run prisma:migrate         # first run only
npm run start:dev

# 2) In another terminal, open an HTTPS tunnel to port 3000
ngrok http 3000                # or: cloudflared tunnel --url http://localhost:3000

# 3) Put the tunnel URL into .env and let the app self-register on boot
#    APP_BASE_URL=https://<your-tunnel>.ngrok-free.app
#    TELEGRAM_SET_WEBHOOK_ON_STARTUP=true
#    TELEGRAM_BOT_TOKEN=...        (from @BotFather)
#    TELEGRAM_WEBHOOK_SECRET=...   (any A-Z a-z 0-9 _- string)

# 4) Restart the app — watch the logs for:
#    "Webhook Registered", "Bot Commands Published", "Webhook Verified"
```

Then open your bot in Telegram and send `/start`. Watch the server logs for
`Incoming Update`, `Command Handled`, `Callback Query Received` and
`Message Edited` as you interact with the menu.

---

## Internationalisation (i18n)

The bot is fully multilingual. Two languages are supported today — **Uzbek**
(`uz`) and **Russian** (`ru`); English is intentionally not implemented yet.

- **Translation files** live in [`src/i18n/locales`](./src/i18n/locales)
  (`uz.json`, `ru.json`) — there are no user-facing hardcoded strings. Both
  catalogs are validated for key parity on boot.
- **First `/start`** shows a language selection screen
  (🇺🇿 O'zbekcha / 🇷🇺 Русский). The choice is persisted on the
  `TelegramUser.language` column, so the selection step is **skipped** on
  subsequent starts.
- Every message and inline button is rendered through `I18nService` in the
  user's locale; a **🌐 Change Language** button inside the main menu lets the
  user switch at any time.

Adding a key: add it to **both** `uz.json` and `ru.json`, then reference it via
a constant in [`src/i18n/i18n.keys.ts`](./src/i18n/i18n.keys.ts) (`TKey.*`),
which is compile-time checked against the catalog shape.

---

## Health check

```
GET /health
```

Returns database status, Redis status, application version and uptime in the
standard Terminus envelope:

```json
{
  "status": "ok",
  "info": {
    "database": { "status": "up" },
    "redis": { "status": "up" },
    "application": { "status": "up", "version": "1.0.0", "uptimeSeconds": 123 }
  },
  "details": { "...": "..." }
}
```

---

## API documentation

Swagger UI is served at:

```
GET /docs
```

---

## Testing

```bash
npm test            # unit tests
npm run test:cov    # coverage
npm run test:e2e    # end-to-end (infra mocked)
```

Covered: configuration validation, the webhook controller, the webhook guard,
the Telegram dispatcher/command routing, a command handler, the health check
and an application-level e2e (health + webhook auth).

---

## Deployment

1. Provision PostgreSQL and Redis.
2. Set production environment variables (validated on boot).
3. Build the image: `docker build -t teplolux-crm ./backend`.
4. Run with `prisma migrate deploy` applied automatically by the entrypoint.
5. Put the service behind TLS (the webhook secret protects the endpoint; HTTPS
   is required by Telegram).
6. Register the webhook (see above).

A GitHub Actions workflow (`.github/workflows/backend-ci.yml`) lints, builds and
tests on every push/PR.

---

## Future modules

The following are **architecturally prepared but intentionally not implemented**:
amoCRM integration, AI agent, knowledge base, product catalog, order system,
dealer portal, analytics dashboard, notification service, queue system,
background jobs, file storage, voice/image recognition, multi-language and
multi-channel messaging. Each will slot in as its own module behind a clear
port/abstraction (see `modules/amocrm/amocrm.port.ts` for the pattern).
