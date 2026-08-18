# 13 — FRONTEND / PRODUCT EXPERIENCE SPECIFICATION

## Product aesthetic discussed

- magnificent/futuristic AI
- sharp
- colorful
- deep blue
- masculine AI
- futuristic/holographic feel

## Product shell discussed

- collapsible sidebar
- Tools section
- Go Pro pill (historical UI requirement)
- user avatar
- HOME page
- capability cards
- dashboard/preview areas

## Important current boundary

The user later explicitly said:
- do not copy Manus's current interface
- build the David AI interface yourself
- do not inherit Manus colors/styling by default
- do not copy external agent UIs

## Frontend stack previously referenced
- Next.js
- React
- Tailwind CSS
- `NEXT_PUBLIC_API_URL`
- `hooks/useChat.ts`
- components such as Navbar, DashboardPreview, FeatureCard

These are historical references; inspect the current frontend repository for actual source of truth.

## Future frontend surfaces
The UI should eventually expose:
- chat
- memory
- projects
- tasks
- agents
- tools
- provider status
- integrations
- YouTube/TikTok connection
- creative suite
- files/assets
- deployments
- system health
- evolution status
- approvals
- audit history

## UI security rule
Never expose server-side API keys in frontend code.
