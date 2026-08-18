# David AI — Creative Backend

Backend for David AI's creative suite: Image, Video, Artwork, Music,
Voice, Enhancer, and Editor. One Express + MongoDB API that handles
auth, model routing, generation jobs, the Explore feed, and Templates.

## Quick start

```bash
npm install
cp .env.example .env      # then fill in MONGODB_URI and JWT_SECRET at minimum
npm run seed               # creates a demo user + sample templates/creations
npm run dev                 # starts on http://localhost:4000
```

Demo login after seeding: `demo@davidai.dev` / `demo-password`.

The app is fully usable with **zero provider API keys** — every model
falls back to a mock generator (`src/providers/nativeProvider.js`) that
returns a placeholder image/thumbnail after a short simulated delay.
That's intentional: it means the frontend can be built and demoed
end-to-end before a single real AI API is wired up.

## Wiring up real providers

Each provider adapter in `src/providers/` checks for its API key and
falls back to the mock generator if it's missing:

| Provider     | Env var             | Powers                              |
|--------------|----------------------|--------------------------------------|
| Google       | `GOOGLE_API_KEY`     | Nano Banana Pro / 2 / base           |
| OpenAI       | `OPENAI_API_KEY`     | GPT Image 2                          |
| ByteDance    | `BYTEDANCE_API_KEY`  | Seedream 5.0 / 4.5, Seedance 2.0     |
| xAI          | `XAI_API_KEY`        | Grok Pro                             |
| native       | *(none needed)*      | DaVinci Ultra/Motion/Music/Voice/Enhancer/Editor + the mock fallback for everything else |

Once you set a key, open that provider's file (e.g.
`src/providers/openaiProvider.js`) and replace the `throw` at the
bottom with a real `fetch()` call — there's a commented example in
each file. This is left as a stub rather than a guessed integration
because the real request/response shape for each vendor's API varies
and changes over time; wiring in the exact current contract from that
vendor's docs is safer than shipping code that looks connected but
was never verified against a real API.

## Adding or changing a model

Everything the "Select Model" dropdowns show comes from one file:
`src/config/modelsRegistry.js`. Add an entry there (with `id`, `name`,
`provider`, `description`, and optionally `default: true`) and it's
immediately live on `GET /api/models/:tool` — no other code changes
needed unless the provider itself is new.

## API reference

All routes are prefixed with `/api`. Routes marked 🔒 require
`Authorization: Bearer <token>` (returned from register/login).

### Auth
- `POST /auth/register` — `{ name, email, password }`
- `POST /auth/login` — `{ email, password }`
- `GET /auth/me` 🔒

### Models
- `GET /models/:tool` — `:tool` is one of `image, video, artwork, music, voice, enhancer, editor`

### Home
- `GET /home` — aggregated payload (featured models, templates, Get Inspired feed)

### Explore
- `GET /explore?tab=popular|styles&tool=image&page=1&limit=30`

### Templates
- `GET /templates?category=video|motion-library|image`

### Generation 🔒
- `POST /generate/:tool` — `{ prompt, modelId?, options?, isPublic? }` → creates and runs a generation job, returns the finished `Creation`
- `GET /creations?tool=&status=&page=&limit=` — the current user's own creations
- `GET /creations/:id` — a single creation (owner or, if public, anyone)
- `POST /creations/:id/like` — increments `likeCount`
- `PATCH /creations/:id/visibility` — `{ isPublic }`, publish/unpublish to Explore

## Data model

Every tool writes to one `Creation` collection (`tool` field
distinguishes them) rather than one table per tool — that's what lets
Explore, "Get Inspired," and each tool's "Creations" tab all query the
same collection instead of needing a union across seven tables. See
`src/models/Creation.js` for the full schema; the free-form `options`
field is where per-tool extras live (aspect ratio, quality, duration,
moodboard/style id, source asset for enhancer/editor, etc.) so adding
a new option to one tool never requires a schema migration.

## Project structure

```
src/
  server.js              Express app entry point
  config/
    db.js                 MongoDB connection
    modelsRegistry.js      source of truth for every model, per tool
  middleware/
    auth.js                 JWT verification
    errorHandler.js          404 + error responses
  models/                  Mongoose schemas: User, Creation, Template
  providers/               One adapter per AI vendor + the native/mock fallback
  controllers/             Route handler logic
  routes/                  Express routers, one per resource
  data/seed.js             Demo user + sample templates/creations
```

## Notes on scope

This is a complete, runnable backend covering auth, model routing,
generation jobs, Explore, Templates, and Home — matching the feature
set described for David AI's creative tools. A few things are
deliberately left as extension points rather than guessed at:

- **File uploads** (for Enhancer, Editor, and image-to-video source
  assets): `options.sourceAssetUrl` is where an uploaded asset's URL
  goes once you add an upload endpoint (e.g. via S3/Cloudinary/etc.) —
  no schema changes needed, just POST the resulting URL.
- **Async job queues**: generation currently awaits the provider call
  inline. The `Creation.status` field (`pending → processing →
  completed/failed`) is already shaped for a real queue (e.g. BullMQ)
  if a provider call ends up being slow enough to need one.
- **Real provider API calls**: see "Wiring up real providers" above.
