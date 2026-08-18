# Supabase implementation references

This implementation uses the official Supabase Data REST API and Storage REST API from the server-side David AI backend.

1. [Supabase Data REST API](https://supabase.com/docs/guides/api): Supabase exposes database CRUD and PostgreSQL functions through PostgREST at `https://<project_ref>.supabase.co/rest/v1/`. The API is reflected from the database schema and works with PostgreSQL roles, grants, and Row Level Security.
2. [Supabase Storage](https://supabase.com/docs/guides/storage): Supabase Storage supports private file buckets, fine-grained access control, and REST/S3-compatible access patterns for project assets.
3. [Supabase Python signed URLs](https://supabase.com/docs/reference/python/storage-from-createsignedurl): private objects can be made available through time-limited signed URLs.
4. [Supabase API keys](https://supabase.com/docs/guides/getting-started/api-keys): `sb_secret_...` keys are elevated server-only credentials that must not be exposed in browser code, public documents, URLs, or source control. They bypass Row Level Security, so the David backend must perform authentication and authorization before using them.

The repository stores only placeholders in `.env.example`. The real key is kept in the ignored local `.env` used for connectivity verification and must be provisioned through the deployment platform’s server-side secret mechanism for production.
