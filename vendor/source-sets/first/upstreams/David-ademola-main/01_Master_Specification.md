# 01 — DAVID AI MASTER SPECIFICATION

You are the lead product architect, senior full-stack engineer, AI engineer, database engineer, security engineer, UI/UX designer, animation engineer, QA engineer, and DevOps engineer for this project.

Your job is to build **David AI**, a premium personal AI operating system.

Do not ask unnecessary technical questions. Do not stop because an optional service is unavailable. Make professional engineering decisions yourself and continue. Diagnose, fix, verify, and keep moving.

This document is the authoritative specification for the David AI project.

---

## 1) PRODUCT IDENTITY

**Product Name:** David AI  
**Product Type:** Personal AI Operating System

David AI must feel like a real intelligent operating system and control center, not a simple chatbot.

It should support:
- chat
- voice
- memory
- tasks
- projects
- devices
- activity logs
- settings
- AI provider switching
- website generation
- website deployment
- video generation
- content generation
- automation
- owner control
- security
- future extensions

This is a real application, not a demo shell.

---

## 2) OWNER / CREATOR IDENTITY

David AI must permanently recognize a single creator/owner account.

### Owner Profile
- **Project Name:** David AI
- **AI Name:** David AI
- **Owner Display Name:** My Lord
- **Owner ID:** SEBIOMO231
- **Owner Email:** sebiomo231@gmail.com
- **Country:** Nigeria
- **Time Zone:** Africa/Lagos (UTC+01:00)
- **Preferred Languages:** English (Primary), Yoruba (Secondary)

When the owner signs in successfully, David AI should greet the owner with a premium welcome experience.

Example welcome:
> Welcome back, My Lord. David AI Core is online and fully operational. All primary systems have initialized successfully. Memory, AI Core, Voice, Projects, Security, Devices, and Tool Systems are standing by. Awaiting your command.

---

## 3) OWNER AUTHENTICATION

Use only:
- password
- fingerprint authentication where supported by the device/browser

Do not require passkeys/WebAuthn unless added later as an optional feature.

Do not hardcode a real password.

Use this placeholder in the implementation:

```text
OWNER_PASSWORD=<SET_DURING_INSTALLATION>
```

Rules:
- prompt for the real owner password once during secure installation
- store only a secure password hash
- never store or expose plaintext passwords
- never expose secrets in frontend code, logs, prompts, or client-side JavaScript
- fingerprint authentication should be supported where the device/browser allows it
- the owner may use password or fingerprint to authenticate

---

## 4) OWNER PRIVILEGES

The owner can:
- manage AI providers
- manage deployments
- manage users
- approve registrations
- suspend or reactivate accounts
- reset user passwords
- view activity logs
- configure system settings
- configure AI models
- manage tools
- manage devices
- manage memory
- manage security
- monitor system health

All privileged actions require proper authentication and authorization.

---

## 5) OWNER-APPROVED REGISTRATION

New user registration must be owner-approved.

Flow:
1. a new user registers
2. the account enters **Pending Approval**
3. the system sends an approval request to the owner email
4. the owner approves or rejects
5. only approved accounts become active

The owner email for approval notifications is:

```text
sebiomo231@gmail.com
```

All approval actions must be logged.

This should be configurable in settings, but owner approval should be the default.

---

## 6) BACKEND CONNECTION / RENDER

The frontend must connect to the deployed backend.

### Primary backend:
```text
https://davidai-backend3-0-4-2.onrender.com
```

### Failover backend:
```text
https://davidai-backend3-0-4-3.onrender.com
```

The app must:
- use the primary backend first
- automatically fail over to the secondary backend if the primary is unavailable
- preserve session and application continuity where possible
- never expose backend secrets to the frontend

The frontend built by Lovable must connect to the backend cleanly and transparently.

---

## 7) AI PROVIDER ARCHITECTURE

Implement a clean provider router with automatic failover.

Supported providers:
- OpenAI where configured
- Gemini
- Groq
- OpenRouter
- Cloudflare
- Cerebras
- SambaNova
- Hugging Face

Rules:
- prefer the best available provider
- automatically switch to the next provider if one fails
- retry failed providers later
- temporarily skip repeatedly failing providers
- log provider selection and failures
- continue until one provider succeeds or all fail
- keep API keys strictly on the backend
- allow manual provider override in settings
- support streaming where possible
- support structured output and tool calling where available

If no provider is configured, use a graceful fallback mode that still keeps the app working.

---

## 8) WEBSITE CREATION ENGINE

David AI must be able to create websites from prompts.

The user can say:
- build me a company website
- create a SaaS dashboard
- create a portfolio
- create an ecommerce site
- create a school system
- create a hotel booking website

David AI should:
- analyze the prompt
- plan the project automatically
- generate frontend structure
- generate backend structure if needed
- generate API endpoints if needed
- generate database structures if needed
- generate authentication if needed
- generate responsive UI
- generate deployment configuration
- test the result
- fix errors automatically
- return a production-ready build
- deploy if credentials and deployment target are configured
- return the deployment URL

David AI should also be able to deploy websites to supported platforms such as:
- Vercel
- Netlify
- Render
- Railway
- Cloudflare
- Fly.io
- other supported hosting targets when configured

The app should return the deployment URL after success.

---

## 9) VIDEO CREATION ENGINE

David AI must support AI-powered video creation through connected providers.

Capabilities:
- text-to-video
- image-to-video
- scene-based video generation
- video enhancement
- video editing
- subtitle generation
- voice-over generation
- thumbnail generation
- export in multiple resolutions
- optional social platform publishing where API access is available

Maximum video length target:
- **up to 2 hours**
- long videos may be generated by splitting into scenes/chapters and combining them if the provider workflow supports it

Important:
- do not claim every provider can generate a single uninterrupted two-hour video
- build a segmented workflow that can assemble long content where supported
- keep it truthful and provider-aware

The system should support publishing workflows for:
- YouTube
- TikTok where supported
- Instagram where supported
- Facebook
- X
- LinkedIn
- WordPress
- Medium

Use only official APIs and authorized OAuth flows.

---

## 10) CONTENT STUDIO

David AI should be able to create:
- websites
- applications
- landing pages
- blog posts
- social posts
- ad copy
- presentations
- documents
- audio scripts
- voiceovers
- videos
- thumbnails
- marketing assets
- product descriptions

---

## 11) AI CORE VISUAL SYSTEM

The interface must have a futuristic AI core.

Use an original design with:
- a glowing red sphere/orb
- rotating rings
- orbiting particles
- scanning arcs
- energy pulses
- waveform animation
- subtle HUD-like glow
- dark futuristic surroundings

The central AI core should react to assistant state.

States:
- IDLE
- LISTENING
- THINKING
- PROCESSING
- SPEAKING
- EXECUTING
- SUCCESS
- WARNING
- ERROR
- OFFLINE

Visual behavior:
- IDLE: soft breathing glow
- LISTENING: stronger pulse and active ring
- THINKING: rotating rings
- PROCESSING: scanning arc motion
- SPEAKING: red glowing sphere with waveform and brightness following speech rhythm
- EXECUTING: faster motion and energy trails
- SUCCESS: short confirmation pulse
- WARNING: amber/red pulse
- ERROR: controlled red pulse
- OFFLINE: dimmed inactive state

Keep animations smooth, elegant, and performant. Support reduced-motion settings.

---

## 12) VISUAL THEME

Use a premium futuristic AI interface with a **red dominant** identity.

Primary palette:
- deep black
- charcoal
- dark red
- crimson
- electric red glow
- white highlights
- metallic gray
- soft amber
- success green
- error red

The UI should feel:
- futuristic
- intelligent
- premium
- command-center-like
- original
- readable

Use centralized design tokens and CSS variables.

Do not hardcode random colors everywhere.

---

## 13) FRONTEND REQUIREMENTS

Create a complete responsive frontend with:
- landing page
- auth page
- dashboard
- chat page
- memory page
- tasks page
- projects page
- devices page
- activity page
- settings page
- website builder page
- video studio page if needed
- provider management panel
- owner panel
- system status widgets

The design must be:
- mobile friendly
- tablet friendly
- desktop friendly
- futuristic
- readable
- polished

Use:
- Next.js
- React
- TypeScript
- Tailwind CSS
- Lucide React
- clean component architecture

---

## 14) NAVIGATION

Include:
- Dashboard
- Chat
- Memory
- Tasks
- Projects
- Devices
- Activity
- Settings
- Website Builder
- Video Studio
- Providers
- Owner/Admin

Navigation should work on all screen sizes and show active state clearly.

---

## 15) CHAT INTERFACE

Create a futuristic chat experience.

Features:
- conversation history
- new conversation
- rename conversation
- delete conversation
- timestamps
- loading state
- error state
- retry
- copy response
- clear conversation
- input box
- send button
- voice button
- attachment architecture
- model/provider indicator
- streaming support where possible

User messages and David AI responses should look like communication packets in a futuristic control system.

---

## 16) VOICE SYSTEM

David AI must talk naturally.

Support:
- speech-to-text
- text-to-speech
- microphone input
- listening state
- speaking state
- thinking state
- mute/unmute
- wake-word / hands-free mode
- conversation mode
- barge-in / interruptible speech

Hands-free voice behavior:
- the user should not need to tap a button every time
- optional wake phrase listening should be supported
- if the user starts speaking while David AI is speaking, David AI should stop and listen immediately
- the UI must visibly show microphone and listening states
- the user can enable/disable hands-free mode

Support:
- English
- Yoruba
- mixed English/Yoruba

Language behavior:
- auto-detect language
- respond in the same language where appropriate
- support a manual language setting:
  - AUTO
  - ENGLISH
  - YORUBA

If a voice provider does not support Yoruba speech output, show that clearly and keep Yoruba text support functional.

---

## 17) MEMORY SYSTEM

Implement persistent user memory.

Categories:
- preferences
- personal context
- projects
- tasks
- assistant preferences
- language
- workflows
- decisions
- knowledge

Requirements:
- user-scoped
- editable
- searchable
- deletable
- optional
- configurable on/off
- separate conversation context from long-term memory
- user-approved persistent memory only

Create a memory management UI with:
- view memory
- edit memory
- delete memory
- clear all memory
- search memory

---

## 18) TASKS

Tasks must be fully functional.

Fields:
- title
- description
- status
- priority
- due date
- project
- createdAt
- updatedAt

Statuses:
- PENDING
- RUNNING
- WAITING_FOR_APPROVAL
- COMPLETED
- FAILED
- CANCELLED

Task UI should be futuristic and easy to use.

---

## 19) PROJECTS

Projects must support:
- create
- rename
- archive
- delete
- view
- tasks
- activity

Everything must be user-scoped.

---

## 20) DEVICE SYSTEM

Create a secure device management architecture.

Each device can have:
- name
- platform
- OS
- version
- status
- capabilities
- lastSeenAt

Show connected devices in the dashboard.

Do not fake unrestricted phone control.

A normal web application cannot bypass device security or OS permissions.

Use legitimate browser/device integration architecture only.

---

## 21) ANDROID COMPANION ARCHITECTURE

Create the architecture so an Android companion app can later integrate securely.

Possible capabilities through proper permissions:
- notifications
- calendar
- contacts
- files
- microphone
- camera
- approved app actions
- approved device actions

Do not bypass Android security. Do not secretly monitor or record.

---

## 22) TOOL REGISTRY

Implement a real tool system.

Every tool must define:
- name
- description
- input schema
- permission level
- handler
- result format

Use Zod validation where appropriate.

Permission levels:
- PUBLIC
- READ
- WRITE
- SENSITIVE
- CRITICAL

---

## 23) TOOL EXECUTION RULES

Every tool execution must:
1. authenticate the user
2. verify ownership and authorization
3. validate input
4. check permissions
5. ask for confirmation when necessary
6. execute the tool
7. record activity
8. return a structured result

Never allow arbitrary AI-generated code execution.

---

## 24) SECURITY

Implement:
- authentication
- authorization
- secure password hashing
- session protection
- ownership checks
- input validation
- audit logging
- security events
- safe error messages
- secret protection
- rate limiting architecture
- upload validation

User data must remain isolated:
- User A must never access User B’s conversations, memory, tasks, projects, devices, or tools

Never expose service-role/private database credentials to frontend code.

---

## 25) AUTHENTICATION

Implement:
- registration
- login
- logout
- protected routes
- password hashing
- session management
- validation
- friendly error states

Fix authentication problems properly.

Do not create fake security.

---

## 26) DATABASE

Use PostgreSQL + Prisma where the project architecture supports it.

Support these data models:
- User
- Account
- Session
- VerificationToken
- UserPreference
- Conversation
- Message
- Memory
- Project
- Task
- Device
- ToolExecution
- SecurityEvent
- ActivityLog

Add the appropriate relations, indexes, and timestamps.

Implement proper authorization and ownership checks.

---

## 27) SETTINGS

Create settings for:
- account
- appearance
- language
- AI
- memory
- voice
- devices
- security

Appearance:
- dark
- light
- system

Primary theme should remain the futuristic red David AI theme.

---

## 28) SYSTEM STATUS HUD

Create a system status section with:
- AI
- MEMORY
- DATABASE
- VOICE
- DEVICES
- TOOLS
- SECURITY
- NETWORK

Each should show:
- ONLINE
- READY
- PROCESSING
- DEGRADED
- NOT CONFIGURED
- OFFLINE
- ERROR

Only show true status based on backend state where possible.

Never fake online status.

---

## 29) ACTIVITY FEED

Create an activity feed showing:
- login
- logout
- conversation created
- memory saved
- task created
- task completed
- project created
- device connected
- tool executed
- security event
- provider switch
- deployment event

Show:
- timestamp
- event type
- description
- status

---

## 30) SYSTEM CORE / MAINFRAME CONCEPT

David AI should have a central core architecture:
- Core Intelligence Engine
- Provider Router
- Website Factory
- Application Factory
- Video Studio
- Image Studio
- Audio Studio
- Automation Engine
- Deployment Engine
- Memory Engine
- Tool Engine
- Security Engine
- Plugin Engine
- Workflow Engine
- Monitoring Engine

This is the conceptual “core” of the system.

---

## 31) WEBSITE + AI APP FACTORY

David AI must be able to:
- create websites from prompts
- create AI assistants from prompts
- create dashboards from prompts
- create applications from prompts
- generate code
- generate UI
- generate APIs
- generate databases
- test generated work
- fix errors automatically
- deploy when configured

---

## 32) AUTONOMOUS BUILD RULES

Do not repeatedly ask technical questions.

Do not ask:
- which framework to use
- which database to use
- whether to add authentication
- whether to add dark mode
- whether to add validation
- whether to add tests
- whether to add error handling
- whether to add responsive design

Make the safest professional decision and continue.

When a service is unavailable:
- create fallbacks
- continue building
- do not stop the whole project

When an error occurs:
- identify it
- fix it
- test it
- continue

Do not leave TODOs, placeholders, or fake completion claims.

---

## 33) RED-FUTURISTIC UI DETAILS

Add:
- glowing sphere core
- subtle scan lines
- moving particles
- animated grid
- data flows
- corner brackets
- thin illuminated borders
- holographic panels
- smooth transitions
- premium spacing
- responsive layout
- reduced-motion support

The interface must look futuristic and AI-like while staying readable.

---

## 34) AI BROWSER / PROVIDER FAILOVER

If one backend or provider fails:
- switch automatically to the next healthy backend/provider
- continue the user session
- preserve conversation continuity
- log the change
- retry failed providers later

This should be transparent to the user.

---

## 35) VIDEO AND WEBSITE DEPLOYMENT

David AI should be able to:
- create videos
- create websites
- deploy websites
- publish content where officially supported
- manage outputs from prompts

Video duration target:
- up to 2 hours using segmented workflows where supported

Do not claim every provider can generate a single 2-hour file natively.

---

## 36) MOCK / FALLBACK MODE

If real AI credentials are missing:
- the app should still run
- authentication should still work
- dashboards should still work
- memory/tasks/projects should still work
- provider status should show unavailable states clearly

Do not break the rest of the app.

---

## 37) TESTING

Add tests for:
- health
- chat
- authentication
- memory
- tasks
- projects
- provider routing
- authorization
- ownership isolation
- language handling
- UI safety where applicable

Fix failing tests.

---

## 38) RESPONSIVE DESIGN

The app must work well on:
- Android/mobile
- tablet
- laptop
- desktop
- ultrawide screens

Avoid horizontal overflow and broken layouts.

---

## 39) ACCESSIBILITY

Support:
- keyboard navigation
- focus states
- readable contrast
- semantic HTML
- screen reader labels
- reduced motion

---

## 40) PERFORMANCE

Optimize:
- API requests
- rendering
- animations
- bundle size
- re-renders

Use lazy loading and reusable components where appropriate.

---

## 41) FINAL BUILD VERIFICATION

Before completion, verify:
- landing page works
- login works
- registration works
- owner approval works
- dashboard works
- chat works
- voice architecture works
- memory works
- tasks work
- projects work
- devices page works
- activity feed works
- settings work
- provider switching works
- backend failover works
- website generation works
- deployment architecture works
- video generation architecture works
- tests pass
- typecheck passes
- build passes
- mobile layout works
- desktop layout works
- secrets are not exposed
- ownership is respected
- user isolation is secure

Fix everything that fails.

---

## 42) OUTPUT REQUIREMENT

Build the complete repository as a coherent production-ready project.

Do not output fragments without context.

Do not stop halfway.

Do not ask me what to do next.

Do not return a list of issues for me to fix.

Build, test, repair, verify, and continue until the project is complete.

END OF MASTER SPECIFICATION
