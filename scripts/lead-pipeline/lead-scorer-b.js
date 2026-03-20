// n8n Code Node: Lead Scorer — Pipeline B (DIY Website)
// Input: array of leads with DIY website + audit data
// Output: leads with score (0-10) + score_breakdown
//
// Paste this into an n8n Code node. It processes all items.

const FREE_EMAIL_DOMAINS = [
  'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
  'icloud.com', 'live.com', 'aol.com', 'mail.com',
  'hotmail.com.au', 'outlook.com.au', 'yahoo.com.au',
  'bigpond.com', 'bigpond.net.au', 'optusnet.com.au',
];

const HIGH_VALUE_TRADES = [
  'plumber', 'electrician', 'builder', 'roofer', 'concreter',
  'landscaper', 'pool', 'painter', 'fencer', 'carpenter',
  'pest control', 'cleaner', 'air conditioning', 'solar',
  'bore', 'drilling', 'excavation', 'demolition',
  'tiler', 'tiling', 'glazier', 'glass', 'garage door',
  'handyman', 'cabinet', 'kitchen', 'bathroom',
];

function scoreDiyWebsiteLead(lead) {
  let score = 0;
  const breakdown = {};

  // Signal 1: PageSpeed score (worse = more opportunity)
  if (lead.pagespeed_score !== null && lead.pagespeed_score !== undefined) {
    if (lead.pagespeed_score < 30) {
      score += 3;
      breakdown.pagespeed = `+3 (PageSpeed ${lead.pagespeed_score}/100 — terrible)`;
    } else if (lead.pagespeed_score < 50) {
      score += 2;
      breakdown.pagespeed = `+2 (PageSpeed ${lead.pagespeed_score}/100 — poor)`;
    } else if (lead.pagespeed_score < 70) {
      score += 1;
      breakdown.pagespeed = `+1 (PageSpeed ${lead.pagespeed_score}/100 — mediocre)`;
    }
  }

  // Signal 2: Not mobile-friendly (huge for tradies — customers search on phone)
  if (lead.mobile_friendly === false) {
    score += 2;
    breakdown.mobile = '+2 (not mobile-friendly — losing phone searchers)';
  }

  // Signal 3: No SSL (browser shows "Not Secure")
  if (lead.has_ssl === false) {
    score += 1;
    breakdown.ssl = '+1 (no SSL — browser shows "Not Secure" warning)';
  }

  // Signal 4: SEO issues
  const seoIssues = lead.seo_issues || [];
  if (seoIssues.length >= 3) {
    score += 2;
    breakdown.seo = `+2 (${seoIssues.length} SEO issues found)`;
  } else if (seoIssues.length >= 1) {
    score += 1;
    breakdown.seo = `+1 (${seoIssues.length} SEO issue(s) found)`;
  }

  // Signal 5: Google reviews (established = has budget)
  if (lead.google_reviews >= 20) {
    score += 2;
    breakdown.reviews = '+2 (20+ reviews — established, can afford upgrade)';
  } else if (lead.google_reviews >= 10) {
    score += 1;
    breakdown.reviews = '+1 (10+ reviews)';
  }

  // Signal 6: Running Google Ads (already spending on marketing)
  if (lead.running_google_ads) {
    score += 2;
    breakdown.ads = '+2 (running Google Ads — marketing-minded, has budget)';
  }

  // Signal 7: High-value trade category
  const catLower = (lead.category || '').toLowerCase();
  if (HIGH_VALUE_TRADES.some(hv => catLower.includes(hv))) {
    score += 1;
    breakdown.high_value_category = '+1 (high-value trade)';
  }

  // Signal 8: Expired domain (had a site, lost it — proven intent)
  if (lead.domain_expired) {
    score += 2;
    breakdown.expired = '+2 (domain expired — had website before, needs new one)';
  }

  // Signal 9: Uses free email (gmail/hotmail) as business email
  // DIY website + free email = cobbling it together, prime upgrade target
  if (lead.email) {
    const emailDomain = lead.email.split('@')[1]?.toLowerCase();
    if (FREE_EMAIL_DOMAINS.includes(emailDomain)) {
      lead.uses_free_email = true;
      if ((lead.google_reviews || 0) >= 5 || lead.running_google_ads) {
        score += 1;
        breakdown.free_email = '+1 (DIY website + free email — doing everything themselves)';
      }
    }
  }

  return {
    ...lead,
    score: Math.min(score, 10),
    score_breakdown: breakdown,
  };
}

// n8n Code node entry point
const results = [];
for (const item of $input.all()) {
  const scored = scoreDiyWebsiteLead(item.json);
  results.push({ json: scored });
}
return results;
