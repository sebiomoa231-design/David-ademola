# 09 — YOUTUBE, TIKTOK, GOOGLE/GMAIL STATUS

## YouTube

APIs:
- YouTube Data API v3
- YouTube Analytics API

Credential style:
- Google OAuth client
- client ID
- client secret
- redirect URI
- user authorization

Capabilities discussed:
- channel information
- video list/details
- upload
- metadata
- playlists
- supported content management
- analytics
- performance reporting

Safety:
- upload is different from publish/public visibility
- verify actual upload result
- never claim success without confirmation

Historical setup:
- YouTube Data API v3 enabled
- YouTube Analytics API enabled
- David AI YouTube OAuth client created
- production redirect URL depended on final deployed backend/frontend URL

## TikTok

Products discussed:
- TikTok Login Kit
- TikTok Content Posting API

Capabilities:
- account connection
- publishing
- content workflows
- supported status/analytics

User requirement:
- YouTube + TikTok
- DO NOT give David Facebook control.

Production redirect URL was not available until deployment configuration was finalized.

## Google/Gmail

Gmail API / Google OAuth was discussed and configured at the app/client level.

Capabilities:
- read
- search
- draft
- send/reply
- attachments
- workflow automation

Redirect URI is deployment-dependent.

## Important OAuth rule

Do not invent redirect URLs.
Use the actual deployed frontend/backend callback URL required by the current OAuth app configuration.
