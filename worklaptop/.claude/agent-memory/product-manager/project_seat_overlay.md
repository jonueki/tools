---
name: project-seat-overlay
description: Chrome extension for Ticketmaster seat selection — single-user decision-support overlay, hard constraints on no-automation
metadata:
  type: project
---

Jonathan is building a Chrome extension (MV3) that overlays Ticketmaster's interactive seat map with a visual highlight layer and ranked candidate panel. The goal is faster seat selection decisions for himself — not bots, not automation.

**Hard constraints (never relax):**
- No synthetic clicks, no auto-cart, no auto-checkout
- No outbound network calls to Ticketmaster
- No DOM event spoofing, no queue automation, no fingerprint modifications
- All UI in Shadow DOM with `tmx-` prefix scoping
- Chrome-only, Manifest V3, single user

**Current state (2026-05-14):**
- Architecture doc drafted by SWE: `docs/seat-overlay-architecture.md`
- PRD written by PM: `docs/prd.md`
- Working in parallel with a Designer (Figma mockups) and SWE (feasibility)
- v0 research (DevTools audit: SVG vs Canvas) is the unblocking task before any code

**Why:** Jonathan attends 10–20 concert drops/year, budget ~$250, lower bowl. Loses seats to other humans because TM dumps 3000 seats with no signal. Decision latency is the problem, not click latency.

**Key open question:** Is TM's seat map SVG or Canvas? This determines which data-reading strategy (DOM observation vs fetch interception) is viable in v1.

**How to apply:** When working on this project, respect all hard constraints above. PRD and arch doc are the source of truth for scope decisions.
