---
name: replica-test
description: >-
  Clicks through every flow of an app clone and tests it for bugs: a test plan
  generated from the recon flows with happy paths and edge cases, Playwright
  end-to-end tests where possible, a browser click-through where not, and bug
  reports in a fixed format with severity, steps and evidence. Use when the
  user says "test my clone", "find bugs", "QA this", "click through
  everything", "write e2e tests", "does it work", or after /replica-build or
  /replica-backend.
---

# replica-test

Reads the flows in `replica/recon.md`. Writes `replica/test-plan.md`,
`replica/bugs.md`, and end-to-end tests in the project (`e2e/`). Templates in
this folder: `test-plan.md`, `bug-report.md`, `e2e.example.spec.ts`.

## The rule

**Test your clone, not the original.** Never load test, fuzz, script or
hammer the original app's servers. Using the original by hand, as a normal
user, to see how it behaves is fine.

## Step 1: the plan

For every flow F01, F02... in the recon map, write:

- **Happy path**: the steps, and what the user should see at the end.
- **Edge cases** that apply. Go down this list for every flow:
  empty input, very long input, emoji and accents, two tabs at once,
  double click on submit, back button mid-flow, refresh mid-flow, slow
  network, offline, expired session, second user's data (must be invisible),
  time zones and daylight saving, mobile width, keyboard only, screen reader
  labels.
- **Negative cases**: wrong password, card declined (Stripe test card
  `4000 0000 0000 0002`), permission denied, deleted record.

Number every case: F01-H1, F01-E3, F01-N2.

## Step 2: automate what you can

Playwright, one spec per flow, against the local dev server with seed data.
Use roles and labels for selectors (`getByRole('button', { name: 'Book' })`),
never CSS classes. See `e2e.example.spec.ts`.

```bash
npm i -D @playwright/test && npx playwright install chromium
npx playwright test
```

Add to every spec: fail on console errors, fail on any 5xx response, and an
axe accessibility scan (`@axe-core/playwright`) on each screen.

## Step 3: click through the rest

What cannot be automated (emails arriving, OAuth with real providers,
payments end to end, visual glitches) gets a manual pass. If a browser tool is
available, drive the local clone with it and screenshot each step. Otherwise
give the user the checklist and wait for answers.

## Step 4: report bugs

Every bug goes in `replica/bugs.md` in the `bug-report.md` format: an ID, a
severity, exact steps, expected, actual, evidence. Severity:

| | means |
| --- | --- |
| S1 | data loss, security hole, payments wrong, core flow blocked |
| S2 | a feature broken, no workaround |
| S3 | broken with a workaround, or visibly wrong |
| S4 | cosmetic |

Only report what you reproduced. "Might be an issue" goes in a separate
"to check" list.

## Step 5: fix loop

Fix S1 and S2 first. For every fix: write the failing test first, fix, watch
it pass, keep the test. Re-run the whole suite after each batch. Update
`bugs.md` with the commit that fixed each one.

## Output

`test-plan.md`, the specs, `bugs.md`, and a summary: cases run, passed,
failed, bugs by severity, fixed so far. Ship nothing with an open S1. Next:
`/replica-diff`.
