---
name: replica-architect
description: >-
  Plans the stack, database schema and API for an app clone, from the recon
  map replica-recon wrote. Picks boring, managed tech, turns the inferred data
  model into real SQL with indexes and access rules, lists every route by
  flow, and orders the build as a thin vertical slice first. Use when the user
  says "plan the clone", "what stack should I use", "design the database",
  "write the schema", "plan the API", "architecture for my version of X", or
  after /replica-recon finishes.
---

# replica-architect

Reads `replica/recon.md` and `replica/features.csv`. Writes
`replica/architecture.md` (template: architecture.md in this folder).

If there is no recon map, stop and run `/replica-recon` first. Planning a
clone from memory of what an app does is how you miss half of it.

## Step 1: the stack

Use what the user already knows if they have a stack. Otherwise the default,
because every part is managed, documented and cheap at zero users:

| layer | default | swap for |
| --- | --- | --- |
| web app | Next.js (App Router) + TypeScript | Remix, SvelteKit, Rails |
| styling | Tailwind, tokens from replica-design | CSS modules |
| mobile | Expo (React Native) | SwiftUI, Kotlin |
| database | Postgres on Supabase or Neon | PlanetScale, SQLite (Turso) |
| ORM | Drizzle or Prisma | raw SQL |
| auth | Supabase Auth or Auth.js | Clerk |
| payments | Stripe Checkout + Billing | Lemon Squeezy, Paddle |
| email | Resend or Postmark | SES |
| jobs | Vercel Cron, Inngest or Trigger.dev | a worker on Fly |
| files | Supabase Storage or Cloudflare R2 | S3 |
| hosting | Vercel | Netlify, Fly, Render |

Write each choice with one line of why. One database. No microservices. The
clone does not need the original's architecture, it needs the original's
features.

## Step 2: the schema

Turn the inferred data model into SQL. For every table:

- `id uuid primary key default gen_random_uuid()`, `created_at`, `updated_at`
- an owner column (`user_id` or `org_id`) on everything a user owns
- foreign keys with an `on delete` rule decided, not defaulted
- indexes on every foreign key and every column you filter or sort by
- enums or check constraints for status fields
- times as `timestamptz`, always, stored in UTC
- money as integer cents plus a currency column
- access rules: Postgres row level security on Supabase, or one
  authorisation check per query in the data layer. Write which.

Example, for a booking app:

```sql
create table bookings (
  id uuid primary key default gen_random_uuid(),
  event_type_id uuid not null references event_types(id) on delete cascade,
  host_id uuid not null references users(id) on delete cascade,
  start_at timestamptz not null,
  end_at timestamptz not null,
  guest_name text not null,
  guest_email text not null,
  guest_timezone text not null,
  status text not null default 'confirmed'
    check (status in ('confirmed','cancelled','rescheduled')),
  answers jsonb not null default '{}',
  created_at timestamptz not null default now(),
  constraint no_zero_length check (end_at > start_at)
);
create index on bookings (host_id, start_at);
```

Then the hard constraints the recon found. Two guests booking the same slot
is a database problem (an exclusion constraint or a unique index), not a UI
problem.

## Step 3: the API

One table per flow from the recon map. For every route or server action:

`method path | what it does | who can call it | input | output | flow`

Plus webhooks in (Stripe, calendar providers) and out, and background jobs
(reminders, sync, cleanup) with their schedule.

Only official, public APIs with the user's own keys. Never the original app's
private endpoints, even if they are visible in a browser.

## Step 4: the parts that bite

Write a line on each that applies: time zones and daylight saving, idempotency
(webhooks arrive twice), race conditions, rate limits, file size limits,
search, realtime, offline, email deliverability, multi-tenancy, GDPR deletion.

## Step 5: build order

1. **Vertical slice.** The core loop end to end, ugly: sign up, do the one
   thing, see the result. Proves the stack.
2. **Must-haves** from `features.csv`, by area.
3. **Should-haves**, then could-haves.
4. **The fixes** replica-entrepreneur finds, once it has run.

Each milestone lists its screens (S-IDs), tables and routes.

## Output

`replica/architecture.md`, the SQL in `replica/schema.sql` or as the first
migration, and a summary: stack in one line, table count, route count, the
three riskiest parts, and the next step: `/replica-design`.
