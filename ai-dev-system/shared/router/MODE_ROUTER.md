# Mode Router

Use QUICK / HYBRID / FULL before deciding solo-dev or team-dev.

## QUICK

Use when:
- one file
- isolated change
- no cross-layer effect
- no architecture decision
- low risk
- requirement is clear

Behavior:
- solo-dev
- minimal diff
- no long plan
- no team simulation

## HYBRID

Use when:
- 2-3 files
- one layer only
- clear change
- low to medium risk
- may need short review gate

Behavior:
- solo-dev with compact review
- short plan
- selected skills only

## FULL

Use when:
- many files
- cross-layer
- new screen/service/API/module
- architecture decision
- unclear scope
- production/security/data/deployment risk

Behavior:
- team-dev
- selected roles only
- planning + review gates

