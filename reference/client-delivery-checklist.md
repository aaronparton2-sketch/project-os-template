# Client Delivery Checklist

Reusable checklist for every new client. Copy this into a plan or project notes and tick off as you go.

---

## Pre-Sale

- [ ] Discovery call completed
- [ ] Demo meeting done (ugly version → premium version shown)
- [ ] Client confirmed scope and pricing verbally

## Payment & Legal

- [ ] Stripe payment link created (correct amount, ToS checkbox enabled)
- [ ] Payment link sent to client
- [ ] Client paid (check Stripe dashboard)
- [ ] Monthly subscription set up in Stripe (hosting/maintenance)

## Domain & Hosting

- [ ] Domain purchased on GoDaddy
- [ ] DNS configured (point to Netlify/Vercel)
- [ ] SSL certificate active (auto via Netlify/Vercel)
- [ ] Site deployed and live at client domain

## Code & Access

- [ ] GitHub repo created for client (naming: `client-name-website`)
- [ ] Client invited to GitHub repo (full access — they own their code)
- [ ] Repo README has basic info (site URL, hosting provider, how to request changes)

## Automations

- [ ] Contact form webhook live (n8n)
- [ ] Email notification working (test submission sent)
- [ ] Any client-specific automations configured and tested

## Handoff

- [ ] Onboarding email sent (see `reference/onboarding-emails.md`)
- [ ] Client confirmed they can see the site live
- [ ] Client added to CRM (Google Sheet — check lifecycle stage)
- [ ] Monthly billing start date noted

## Post-Launch (within 7 days)

- [ ] Follow-up call/message — "How's the site going?"
- [ ] Upsell conversation started (CRM → SEO → Ads)
- [ ] Content idea logged if the build was interesting (`Content Pipeline` tab)

---

## Upsell Add-Ons (use when applicable)

### CRM Setup
- [ ] Google Sheet CRM created from template
- [ ] n8n workflow connected (form → sheet → email notification)
- [ ] Client walkthrough done (how to view leads, what columns mean)
- [ ] Stripe subscription updated (add CRM monthly fee)

### SEO
- [ ] SEO audit completed
- [ ] Google Business Profile claimed/optimised
- [ ] Meta tags, sitemap, analytics set up
- [ ] Monthly SEO reporting configured
- [ ] Stripe subscription updated (add SEO monthly fee)

### Paid Ads
- [ ] Ad account set up (Google Ads or Meta Ads)
- [ ] Initial campaigns built
- [ ] Tracking pixels installed on client site
- [ ] Minimum ad spend confirmed with client
- [ ] Stripe subscription updated (add ads management fee)
