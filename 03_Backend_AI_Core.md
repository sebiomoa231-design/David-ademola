# 03 – Backend & AI Core Architecture

## Purpose
This document defines the backend architecture for David AI.

## Core Principles
- Production-ready backend.
- Modular architecture.
- Automatic provider routing.
- Graceful fallbacks.
- No hard-coded secrets.
- Environment-variable based configuration.

## AI Core
The AI Core coordinates:
- Conversation engine
- Memory engine
- Task engine
- Project engine
- Tool execution
- Website generation
- Video generation
- Voice system
- Security layer

## Provider Router
Support multiple AI providers through a unified router with automatic failover.

## Website Builder
Generate complete websites from prompts.
Support preview, export, and deployment through configured deployment providers.

## Video Generation
Generate AI videos through supported providers.
Support queued rendering, progress tracking, cancellation, and configurable maximum duration.

## Memory
Persistent user memory with searchable long-term storage and temporary conversation context.

## Security
Server-side secret management.
Role-based authorization.
Owner privileges enforced on protected operations.

## APIs
REST endpoints for:
- chat
- memory
- tasks
- projects
- tools
- website generation
- video generation
- health
- authentication

## Deployment
Primary backend should connect to the production backend configuration discussed in the project, with support for the alternate backend configuration as a fallback when appropriate.
