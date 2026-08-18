# DAVID AI — PROVIDER / INTEGRATION INVENTORY

## Current reported AI providers
- Gemini
- Groq
- OpenRouter
- OpenAI
- Anthropic/Claude
- Voyage AI (semantic/embedding memory)
- Hugging Face
- Cloudflare AI
- Cerebras
- SambaNova
- xAI/Grok (when actually configured)

## Creative providers discussed
- Runway — user explicitly confirmed having a Runway API key
- Gemini/Google video capabilities such as Veo — use existing Google/Gemini credentials/access; verify actual endpoint/model access
- Luma — later discussed as a provider to add if a key is created; user initially said no Luma key
- v0/Vercel — discussed; credential status must be verified before configuration
- ElevenLabs — voice/TTS

## External services
- YouTube Data API v3
- YouTube Analytics API
- Google OAuth / YouTube OAuth client
- TikTok Login Kit
- TikTok Content Posting API
- Gmail/Google OAuth
- GitHub
- Supabase/PostgreSQL
- Supabase Storage
- Render
- Google Maps
- OpenWeather
- Paystack

## Important credential-status rules
- Do not assume every discussed provider has a live key.
- The latest conversation confirmed the user did NOT have Sora, Kling, or several other speculative provider keys and did not yet have production OAuth redirect URLs for YouTube/Google/TikTok before deployment.
- The latest Render report said Gemini/Groq/OpenRouter were configured, while OpenAI, Anthropic, Voyage, ElevenLabs, Runway, Luma, v0, Google Maps, and Render provider credentials remained unconfigured at that moment.
- Use the current repository/environment as the authority for what is actually configured.
