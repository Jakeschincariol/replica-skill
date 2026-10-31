# Recon map: {{app}} ({{platform}})

Scope: {{the slice being cloned}}
For: {{who the clone is for}}
Date: {{YYYY-MM-DD}}

## Sources

| # | source | URL | notes |
| --- | --- | --- | --- |
| 1 | help center | | |

## Core loop

{{one sentence: the thing users pay for}}

## Screens

| ID | screen | route / how to reach | purpose | key components | states seen |
| --- | --- | --- | --- | --- | --- |
| S01 | | | | | empty, filled, error |

## Flows

```
F01 {{goal}}
    S01 -> S02 -> S03
    happy path clicks: {{n}}
    edge: {{cases}}
```

## Components

| component | variants | states | used on |
| --- | --- | --- | --- |
| Button | primary, secondary, ghost, danger | default, hover, focus, disabled, loading | all |

## Inferred data model

```
{{Entity}}  {{fields}}
            evidence: {{screen IDs, help articles}}
            confidence: high | medium | guess
```

Relationships: {{User 1-n EventType, EventType 1-n Booking, ...}}

## Feature matrix

See `features.csv`. Must: {{n}}, should: {{n}}, could: {{n}}, skip: {{n}}.

## Out of scope (cannot or should not be cloned)

- {{licensed content, the network, partner deals, ...}}

## Size

Screens {{n}}, flows {{n}}, entities {{n}}. Hard parts: {{list}}. Size: {{S|M|L|XL}}.
