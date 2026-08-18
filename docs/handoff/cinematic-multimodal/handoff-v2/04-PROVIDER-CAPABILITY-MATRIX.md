# 04 — PROVIDER/CAPABILITY MATRIX

This is a routing-design document. It is not a claim that every provider is currently configured or that every model supports every capability.

## Language/reasoning providers

### Gemini
Variable:
`GEMINI_API_KEY`
Roles:
- conversation
- general reasoning
- multimodal understanding
- planning
- coding
- supported image/video capabilities depending on enabled Google APIs/models
Fallback candidates:
- OpenAI
- Anthropic
- OpenRouter
- Groq

### Groq
Variable:
`GROQ_API_KEY`
Roles:
- fast inference
- classification
- fast conversation
- coding/reasoning when supported by selected model
Fallback candidates:
- OpenRouter
- Gemini
- OpenAI

### OpenRouter
Variable:
`OPENROUTER_API_KEY`
Roles:
- multi-model gateway
- model diversity
- fallback
- task-specific model selection
Fallback candidates:
- directly configured providers

### OpenAI
Variable:
`OPENAI_API_KEY`
Roles:
- conversation
- reasoning
- coding
- multimodal
- structured output
- speech/image capabilities where enabled
Status at latest report:
unconfigured in live Render verification

### Anthropic
Variable:
`ANTHROPIC_API_KEY`
Roles:
- reasoning
- coding
- planning
- long-context
Status:
unconfigured in live Render verification

### Hugging Face
Variable commonly discussed:
`HUGGINGFACE_API_KEY`
Roles:
- specialized models
- embeddings/inference depending on selected service
Status:
credential was previously said to exist, but exact live backend configuration must be verified

### Cloudflare AI
Variable commonly discussed:
`CLOUDFLARE_API_KEY`
Roles:
- AI inference
- infrastructure-adjacent model access
Status:
credential was previously said to exist; verify current backend usage

### Cerebras
Variable:
`CEREBRAS_API_KEY`
Roles:
- fast inference
- reasoning/coding where supported
Status:
credential was previously said to exist; verify current backend usage

### SambaNova
Variable:
`SAMBANOVA_API_KEY`
Roles:
- fast inference
- reasoning/coding where supported
Status:
credential was previously said to exist; verify current backend usage

### xAI / Grok
Variable commonly discussed:
`XAI_API_KEY`
Roles:
- reasoning/general AI
Status:
discussed; current credential status requires verification

## Memory/embeddings

### Voyage AI
Variable:
`VOYAGE_API_KEY`
Roles:
- embeddings/semantic retrieval
Status:
unconfigured in latest AI Core live report

## Voice

### ElevenLabs
Variable:
`ELEVENLABS_API_KEY`
Roles:
- text-to-speech
- voice generation
- voice workflows
Status:
unconfigured in latest AI Core live report

## Video

### Runway
Variable:
`RUNWAY_API_KEY`
Roles:
- video generation
- video/creative workflows
Status:
unconfigured in latest AI Core live report, although user later stated a Runway key had been collected; reconcile against current Render configuration.

### Luma
Variable often proposed:
`LUMA_API_KEY`
Roles:
- video/image generation
Status:
user later said no Luma key at that moment; if a new key is created, verify and add it.

### Other video providers
Vidu/Vid0, Kling, Sora, Seedance and similar providers were discussed, but user explicitly clarified that some did not have keys. Do NOT configure them unless credentials are genuinely supplied.

## Website/UI

### v0/Vercel v0
Variable often proposed:
`V0_API_KEY`
Role:
- AI UI/website generation
Status:
unconfigured in latest AI Core report; credential status must be verified.

### Vercel platform
Variable often proposed:
`VERCEL_API_TOKEN`
Role:
- project/deployment management
Status:
credential status must be verified.

## Maps

### Google Maps
Variable:
`GOOGLE_MAPS_API_KEY`
Roles:
- maps
- places
- location
- routing/geocoding where enabled
Status:
unconfigured in latest AI Core report

## Weather

### OpenWeather
Variable:
`OPENWEATHER_API_KEY`
Roles:
- current weather
- forecasts
Status:
previously discussed/collected; verify live configuration

## Payments

### Paystack
Variables:
`PAYSTACK_PUBLIC_KEY`
`PAYSTACK_SECRET_KEY`
Roles:
- payment workflows
- transaction status
Status:
user previously confirmed public + secret keys obtained

## External account integrations

### YouTube / Google
Credential types:
- OAuth client ID
- OAuth client secret
- redirect URI
APIs:
- YouTube Data API v3
- YouTube Analytics API
Status:
OAuth app/client setup completed; production redirect URLs were dependent on deployed URLs.

### TikTok
Credential types:
- app/client key
- app/client secret
- redirect URI
Products:
- Login Kit
- Content Posting API
Status:
app/products configured; production redirect URL/review still dependent on final deployment configuration.

### GitHub
Credential types:
- token or GitHub App credentials
Role:
- repositories
- branches
- commits
- PRs
- issues
- workflow/status
Status:
integration exists in backend; credential specifics must be verified.

### Supabase
Credential types:
- project URL
- anon/publishable key as applicable
- service role secret for backend
Role:
- PostgreSQL
- storage
- persistence
Status:
successfully integrated in prior project work.

### Render
Credential type:
- Render API key/token if provider integration is used
Role:
- deployment/service management
Status:
latest AI Core report listed Render provider credentials as unconfigured.

### Manus
Variable:
`MANUS_API_KEY` (exact name must be verified against Manus integration)
Role:
- agentic task execution
- complex multi-step workflows
- coding/build/research/project operations
Status:
user stated they have a Manus API key; integrate only using the official API contract and secure secret storage.
