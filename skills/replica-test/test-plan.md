# Test plan: {{your app}}

Build: {{commit}}  Date: {{YYYY-MM-DD}}  Env: local, seed data

| case | flow | type | steps | expected | auto | result |
| --- | --- | --- | --- | --- | --- | --- |
| F01-H1 | guest books a meeting | happy | open /u/demo/30min, pick tomorrow 10:00, fill form, submit | confirmation screen, booking on host dashboard, email to both | e2e | |
| F01-E1 | | edge: slot taken while filling form | | clear message, pick another slot, no double booking | e2e | |
| F01-E2 | | edge: guest in another time zone | | times shown in guest zone, stored in UTC | e2e | |
| F01-N1 | | negative: card declined | | error shown, no booking created | manual | |
