---
trigger: always_on
---

# GWEN — Rules (condensed)

**Stack:** React 19, Vite/TanStack Start (check package.json), Tailwind, shadcn/ui, Framer Motion. npm, not bun.

**Structure:** ONE scrolling page: Landing → Home → Analysis → Video Studio → Shorts Factory. No route changes between sections.

## Landing
- ONE logo only, ever.
- Real 3D rotation: `perspective` on PARENT, `preserve-3d` + `rotateY` on child (not just scale/fade).
- Rotate + zoom + move-to-left = one continuous motion, no jump cut.
- Plays once per session (sessionStorage).

## Home
- Left: logo silhouette+eyes only, no box background. Glassmorphism (`backdrop-filter: blur`), web bg visible through it.
- Logo: NO expression, static.
- Right text: only "Welcome to GWEN." — no tagline, no "new manager" line.
- Floating chat agent ALSO visible here (bottom-right), separate from the left logo.

## Eyes — two specs, don't mix
**Static (landing+home logo):** tilted-flame shape, white fill, `#FF69B4` 6px stroke, black bg, sharp flame-flick top-outer corners, deep organic bottom curves, sharp inner corners.

**Animated blink (chat agent ONLY):** Framer Motion `<motion.path>`, morph `d`:
- Open: `M 180 215 C 172 163, 140 123, 70 123 C 62 123, 74 187, 94 227 C 110 251, 150 259, 180 243 C 184 241, 184 227, 180 215 Z`
- Closed: `M 180 230 C 172 230, 140 230, 70 230 C 62 230, 74 230, 94 230 C 110 230, 150 230, 180 230 C 184 230, 184 230, 180 230 Z`
- 0.1s close / 0.15s reopen / repeat Infinity / 3-5s repeatDelay

## Background
Muted dusty mauve/pink webs on black, uniform visibility whole page (not center-only), 2 layers, expand/compress motion, smooth.

## Nav
Top-right, fixed: Home, Analysis, Video Studio, Shorts Factory + profile/login icon next to Shorts Factory. Click = smooth scroll to section, no route change. Liquid-flow feel on every hover/click.

## Chat agent expressions
Curious=idle, Happy=after good response, Focused=loading (incl. 2-5min shorts generation). State-driven.

## APIs
`POST /ai/action`: `{message, conversation_history, current_page, user_id?}` → `{reply, action, data}`. current_page has no "shorts" value — use `"videos"` + TODO comment for that case.
`/video/analyze`, `/video/generate-shorts`, `/thumbnail/analyze`: multipart, sync, JSON, errors=`{detail}`. generate-shorts = 2-5min, needs real loading state.

## Sections
- Analysis: animated graph (views/watch time/health score) top, comment sentiment/themes bottom.
- Video Studio: video upload left, thumbnail upload right, recommendations below.
- Shorts Factory: upload → clips → preview → download.