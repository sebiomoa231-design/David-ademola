# YOUTUBE / TIKTOK / GOOGLE INTEGRATION NOTES

## YouTube
Configured in Google Cloud during the project:
- YouTube Data API v3
- YouTube Analytics API
- DAVID AI YOUTUBE OAuth client
- channel/content management permissions
- analytics permissions

Production redirect URL depends on the deployed frontend/backend. Never invent the redirect URI.

## TikTok
Configured/started:
- TikTok Developer app
- Login Kit
- Content Posting API
- publishing scopes/products

Production redirect URL/review requirements depend on deployed URLs and TikTok app settings. Never invent them.

## Gmail / Google
- Google Auth Platform configuration
- DAVID AI WEB OAuth client
- Gmail-related authorization

Again, redirect URI must use the actual deployed URL.

## Facebook
User explicitly said Facebook should NOT be controlled by David AI. Do not add Facebook control to the current social scope.
