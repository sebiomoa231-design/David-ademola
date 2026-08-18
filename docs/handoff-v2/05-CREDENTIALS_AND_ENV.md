# 05 — CREDENTIALS, ENVIRONMENT VARIABLES, AND SECRET POLICY

## Critical rule

Never place real secrets in:
- chat prompts
- GitHub source
- commits
- frontend bundles
- `.env` committed files
- logs
- documentation
- memory records
- test fixtures

If a secret was pasted into chat, treat it as potentially exposed and regenerate/revoke it.

## User-confirmed / previously discussed credentials

The user stated they have/had credentials for several providers, including:
- Gemini
- Groq
- Hugging Face
- OpenRouter
- Cloudflare
- Cerebras
- SambaNova
- Runway
- ElevenLabs
- Google Maps
- OpenWeather
- Paystack
- Manus

However, the latest live AI Core report showed a smaller subset actually configured in Render:
- Gemini
- Groq
- OpenRouter

Therefore:
PROVIDER-OWNERSHIP != LIVE-RENDER-CONFIGURATION.

## Variables commonly used/recommended

```text
GEMINI_API_KEY
GROQ_API_KEY
OPENROUTER_API_KEY
OPENAI_API_KEY
ANTHROPIC_API_KEY
VOYAGE_API_KEY
HUGGINGFACE_API_KEY
CLOUDFLARE_API_KEY
CEREBRAS_API_KEY
SAMBANOVA_API_KEY
XAI_API_KEY
ELEVENLABS_API_KEY
RUNWAY_API_KEY
LUMA_API_KEY
V0_API_KEY
VERCEL_API_TOKEN
GOOGLE_MAPS_API_KEY
OPENWEATHER_API_KEY
PAYSTACK_PUBLIC_KEY
PAYSTACK_SECRET_KEY
GITHUB_TOKEN
SUPABASE_URL
SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
RENDER_API_KEY
MANUS_API_KEY
```

For YouTube/Google/TikTok, actual variables may be:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`
- `YOUTUBE_REDIRECT_URI`
- `TIKTOK_CLIENT_KEY`
- `TIKTOK_CLIENT_SECRET`
- `TIKTOK_REDIRECT_URI`

BUT:
exact names must be taken from the current codebase. Do not create unused variables just because they appear here.

## Render configuration procedure

1. Inspect code for environment variable reads.
2. Build authoritative list from actual imports/usages.
3. Compare against available credentials.
4. Configure only real credentials.
5. Add secrets through Render's secure environment-variable UI/API.
6. Never commit values.
7. Restart/redeploy.
8. Verify health and provider configuration without printing values.

## Missing/unfinished credentials previously noted

- OpenAI: unconfigured in latest report
- Anthropic: unconfigured
- Voyage: unconfigured
- ElevenLabs: unconfigured
- Runway: unconfigured in latest report despite user later saying key was collected
- Luma: user said no key at one point; later asked for Luma key creation guide
- v0: unconfigured
- Google Maps: unconfigured
- Render: provider credentials unconfigured in latest AI Core report
- production Google/YouTube/TikTok redirect URIs depend on final deployed URLs

Do not invent missing values.
