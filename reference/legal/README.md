# Legal Reference Documents

This directory holds the Terms of Service and Privacy Policy used in Stripe payment links.

**These are the live documents clients agree to at checkout.** Review with a legal professional before making changes.

## Current Files

| File | Status | Purpose |
|------|--------|---------|
| `Terms of Service_Mycelium.pdf` | Active | ToS embedded in Stripe payment link — client ticks checkbox to agree before paying |
| `Privacy Policy_Mycelium.pdf` | Active | Privacy policy referenced in Stripe checkout and on website |

## How Contracts Work

No separate contract signing. The legal flow is built into Stripe checkout:

1. Aaron sends client a Stripe payment link
2. Payment link includes a ToS checkbox (links to Terms of Service)
3. Client ticks the box + pays → legally binding agreement
4. Stripe records the acceptance with timestamp

This removes friction (no e-sign tools, no PDF contracts) while still being legally enforceable.

## When to Update

- If services or pricing tiers change significantly
- If adding new service types (e.g., ad management, custom apps)
- If legal requirements change (Australian consumer law, privacy act)
- Always get legal review before publishing changes
