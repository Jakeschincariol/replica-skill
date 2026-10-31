# Architecture: {{your app}} (a rebuild of {{app}}'s core features)

## Stack

| layer | choice | why |
| --- | --- | --- |
| web | | |
| database | | |
| auth | | |
| payments | | |
| email | | |
| jobs | | |
| hosting | | |

## Schema

Tables: {{n}}. Access rules: {{RLS | data-layer checks}}.

```sql
-- or see replica/schema.sql
```

## API

| method path | does | who | input | output | flow |
| --- | --- | --- | --- | --- | --- |

Webhooks in: {{...}}  Webhooks out: {{...}}
Jobs: {{name, schedule, what it does}}

## The parts that bite

- time zones:
- idempotency:
- races:

## Build order

1. Vertical slice: {{screens, tables, routes}}
2. Must-haves:
3. Should-haves:
4. Fixes from replica-entrepreneur:
