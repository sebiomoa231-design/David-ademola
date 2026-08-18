# 02 — FRONTEND ARCHITECTURE

## Purpose

This file defines the full frontend architecture for David AI.

The frontend must feel like a premium futuristic operating system with a red-dominant visual identity, a central AI sphere/core, voice-aware interaction, responsive dashboards, and clean modular UI layers.

The frontend must not be a simple landing page. It is the primary user experience for David AI.

---

## 1) FRONTEND TECHNOLOGY STACK

Use:
- Next.js (App Router)
- React
- TypeScript
- Tailwind CSS
- Lucide React
- reusable component architecture
- optional Framer Motion only where it improves the experience without making the app heavy

Requirements:
- strict typing
- small reusable components
- clear separation between UI, data, hooks, and page layouts
- no duplicated logic
- no hardcoded secrets
- no backend secrets in client-side code
- client-side code must communicate through a centralized API layer

---

## 2) VISUAL DESIGN SYSTEM

The UI must use a red futuristic theme.

Primary colors:
- black
- charcoal
- deep red
- crimson
- electric red glow
- white highlights
- metallic gray
- amber warning
- green success

Design style:
- premium
- futuristic
- command-center-like
- glowing
- holographic
- original
- readable
- polished

Do not mimic any copyrighted assistant interface exactly.

Create an original David AI identity with:
- glowing AI core
- subtle scan lines
- orbiting particles
- grid background
- thin illuminated borders
- holographic panels
- clean shadows
- subtle motion
- responsive spacing

Use centralized CSS variables / design tokens.

---

## 3) CORE FRONTEND LAYOUT

The app should be organized around a shell layout:

- left sidebar navigation
- top status bar
- main content area
- right side information/status panels where useful

On mobile:
- sidebar collapses into a drawer or bottom navigation
- panels stack vertically
- the AI core scales down
- buttons remain touch-friendly

---

## 4) REQUIRED PAGES

Implement these frontend routes:

- `/`
- `/auth`
- `/dashboard`
- `/chat`
- `/memory`
- `/tasks`
- `/projects`
- `/devices`
- `/activity`
- `/settings`
- `/website-builder`
- `/video-studio`
- `/providers`
- `/owner`

If a route is not yet fully functional because the backend or a provider is unavailable, show a graceful status state instead of breaking.

---

## 5) LANDING PAGE

The landing page should introduce David AI as a premium AI operating system.

Must include:
- futuristic hero section
- central red AI sphere/core
- concise product statement
- primary CTA
- secondary CTA
- key feature cards
- system capability highlights
- premium footer

The hero should immediately communicate:
- David AI is intelligent
- David AI is premium
- David AI is futuristic
- David AI is ready for creation and automation

The central AI core on the landing page should animate subtly and react visually to a simulated idle state.

---

## 6) AUTH PAGE

The auth page must support:
- login
- registration
- owner login flow
- loading states
- validation states
- user-friendly error messages

Requirements:
- secure login architecture
- clear password input
- fingerprint/biometric support where the platform allows it
- owner approval workflow if the backend supports it
- no broken authentication flow
- no confusing UI states

The page should look premium and not generic.

---

## 7) DASHBOARD

The dashboard is the main operating view.

It should include:
- AI core
- status summary
- memory summary
- recent conversations
- active tasks
- active projects
- provider status
- backend connection status
- activity feed preview
- quick actions

The dashboard should behave like a command center.

It must be responsive and feel alive without being visually noisy.

---

## 8) CHAT UI

The chat interface must support:
- message history
- assistant replies
- timestamps
- loading indicators
- error indicators
- retry buttons
- clear conversation
- new conversation
- rename conversation
- delete conversation
- copy response
- voice button
- send button
- attachment architecture
- provider/model indicator

The chat should visually feel like a communication console.

Messages should have a structured packet-like appearance:
- user message cards
- assistant response cards
- system notices
- provider notices
- status ribbons where useful

---

## 9) VOICE-AWARE UI

The frontend must support voice interaction states:
- idle
- listening
- thinking
- processing
- speaking
- muted
- error

UI behavior:
- microphone icon must clearly show the state
- speaking state should animate in sync with speech rhythm where possible
- listening state should pulse
- barge-in behavior should be visible to the user
- wake/listen state should be obvious

If voice features are not configured, show a clear NOT CONFIGURED status and do not break the rest of the interface.

---

## 10) MEMORY PAGE

The memory page should allow:
- view memories
- search memories
- edit memories
- delete memories
- clear memories
- separate long-term memory from conversation context

Visual style:
- clean list cards
- tags and categories
- confidence and importance indicators where appropriate
- search bar with futuristic styling

---

## 11) TASKS PAGE

The tasks page should allow:
- create task
- edit task
- mark task complete
- archive task
- filter by status
- filter by priority
- search tasks
- attach to project

Statuses:
- pending
- running
- waiting for approval
- completed
- failed
- cancelled

The UI should present tasks as a futuristic productivity view.

---

## 12) PROJECTS PAGE

The projects page should allow:
- create project
- rename project
- archive project
- delete project
- view project details
- see attached tasks
- see project activity

This section should feel like a creative workspace.

---

## 13) DEVICES PAGE

The devices page should show:
- connected devices
- browser/device capability status
- microphone permission status
- notification permission status
- last seen times
- platform labels

Important:
- do not fake unrestricted phone control
- only expose what browser/device permissions legitimately allow
- build future integration architecture for Android companion support later

---

## 14) ACTIVITY PAGE

The activity page should show:
- login events
- logout events
- memory events
- task events
- project events
- provider switches
- deployment events
- security events
- tool execution events

Each item should include:
- timestamp
- event type
- concise description
- status

---

## 15) SETTINGS PAGE

The settings page should include:
- account settings
- appearance
- language
- AI provider preferences
- voice preferences
- memory preferences
- notification preferences
- device settings
- security settings
- owner approval settings where applicable

Appearance:
- dark / system / light if the system supports them
- default theme should remain the red futuristic David AI theme

Language:
- AUTO
- ENGLISH
- YORUBA

---

## 16) WEBSITE BUILDER PAGE

The website builder page should allow:
- prompt input
- generation request
- progress indication
- generated preview
- deployment action if the backend supports it

The interface should communicate:
- prompt received
- plan in progress
- components generated
- backend/build generated
- deployment status

---

## 17) VIDEO STUDIO PAGE

The video studio page should allow:
- video prompt input
- generation workflow
- asset preview
- duration handling
- export options
- publication workflow where supported

If video generation is not configured, show a clear fallback state.

---

## 18) PROVIDERS PAGE

The providers page should show:
- all configured providers
- active provider
- fallback provider
- status per provider
- health state
- switch controls if allowed by the backend

Provider switch behavior must be transparent and user-friendly.

---

## 19) OWNER PAGE

The owner page should show:
- owner identity confirmation
- approved owner privileges
- approval queue for new registrations if the backend supports it
- system health
- provider health
- backend health
- security events
- critical settings

This page should feel administrative and secure.

---

## 20) STATE MANAGEMENT

Use a lightweight and maintainable state strategy.

Requirements:
- keep UI state local when possible
- use shared state only when needed
- centralize API communication
- avoid overengineering
- preserve session-aware state
- handle loading and error states consistently

If a user action depends on backend data:
- show loading
- show success
- show failure
- allow retry where appropriate

---

## 21) API CLIENT LAYER

All frontend-to-backend communication must pass through one centralized API client/service layer.

Rules:
- no scattered hardcoded fetch URLs
- use the configured backend base URL
- support the primary Render backend and failover backend
- support backend health checks
- support reconnect/retry behavior
- support provider status retrieval
- support memory, tasks, projects, settings, chat, and other application APIs

The frontend should be able to recover gracefully if the backend is temporarily unavailable.

---

## 22) PERFORMANCE

Optimize the frontend for:
- fast first render
- minimal re-renders
- reusable components
- lazy loading where appropriate
- no unnecessary heavy animation loops
- no excessive dependencies

The app must feel responsive on mobile devices.

---

## 23) ACCESSIBILITY

Support:
- keyboard navigation
- visible focus states
- semantic HTML
- screen-reader support
- sufficient contrast
- reduced-motion mode
- accessible labels for icon buttons and voice controls

---

## 24) RESPONSIVE BEHAVIOR

The UI must work on:
- Android phones
- iPhones
- tablets
- laptops
- desktops
- ultrawide displays

Rules:
- no horizontal scrolling caused by layout mistakes
- sidebar collapses on small screens
- cards stack cleanly
- the AI core scales down smoothly
- controls stay touch-friendly

---

## 25) BUILD RULES

Do not:
- create broken links
- create fake buttons that do nothing
- expose secrets
- put API keys in client code
- leave placeholder UI without a fallback plan
- break working features

Do:
- build cleanly
- use reusable components
- keep code readable
- maintain visual consistency
- respect the backend contract
- show fallback states when a feature is unavailable

---

## 26) FRONTEND ACCEPTANCE CHECK

The frontend is considered acceptable only if:
- the landing page renders correctly
- the auth flow is usable
- the dashboard is informative
- the chat interface works
- voice states are represented
- memory, tasks, projects, devices, activity, settings pages render
- provider/backend status is visible
- the website builder page is functional
- the video studio page is represented
- the app is responsive and visually polished
- the red AI theme is consistent across the app

END OF FRONTEND ARCHITECTURE