// n8n Code Node: Lead Scorer — Pipeline A (No Website)
// Input: array of normalised lead objects (no website)
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

const SEASONAL_BOOST = {
  'landscap': [8, 9, 10, 11],
  'pool': [8, 9, 10, 11],
  'air con': [9, 10, 11, 12],
  'solar': [1, 2, 3, 9, 10, 11],
  'pest': [9, 10, 11, 12, 1, 2],
  'clean': [1, 2, 11, 12],
};

function scoreNoWebsiteLead(lead) {
  let score = 0;
  const breakdown = {};

  // Signal 1: New business registration (ABR source) — timing advantage
  if (lead.registration_date) {
    const daysSinceReg = Math.floor(
      (Date.now() - new Date(lead.registration_date)) / (1000 * 60 * 60 * 24)
    );
    if (daysSinceReg <= 14) {
      score += 3;
      breakdown.new_business = '+3 (registered < 14 days ago)';
    } else if (daysSinceReg <= 30) {
      score += 2;
      breakdown.new_business = '+2 (registered < 30 days ago)';
    } else if (daysSinceReg <= 90) {
      score += 1;
      breakdown.new_business = '+1 (registered < 90 days ago)';
    }
  }

  // Signal 2: Google reviews (established + growing = budget to spend)
  if (lead.google_reviews >= 20) {
    score += 3;
    breakdown.reviews = '+3 (20+ reviews — established, ready to invest)';
  } else if (lead.google_reviews >= 10) {
    score += 2;
    breakdown.reviews = '+2 (10+ reviews — growing)';
  } else if (lead.google_reviews >= 5) {
    score += 1;
    breakdown.reviews = '+1 (5+ reviews)';
  }

  // Signal 3: HiPages activity (actively seeking work)
  if (lead.hipages_jobs >= 20) {
    score += 2;
    breakdown.hipages = '+2 (20+ HiPages jobs — very active)';
  } else if (lead.hipages_jobs >= 10) {
    score += 1;
    breakdown.hipages = '+1 (10+ HiPages jobs)';
  }

  // Signal 4: Website is just a Facebook page
  if (lead.website_is_facebook) {
    score += 1;
    breakdown.facebook_only = '+1 (website is Facebook page — knows they need web presence)';
  }

  // Signal 5: High-value trade category
  const catLower = (lead.category || '').toLowerCase();
  if (HIGH_VALUE_TRADES.some(hv => catLower.includes(hv))) {
    score += 1;
    breakdown.high_value_category = '+1 (high-value trade)';
  }

  // Signal 6: Seasonal timing bonus
  const month = new Date().getMonth() + 1;
  for (const [keyword, months] of Object.entries(SEASONAL_BOOST)) {
    if (catLower.includes(keyword) && months.includes(month)) {
      score += 1;
      breakdown.seasonal = '+1 (seasonal timing match)';
      break;
    }
  }

  // Signal 7: Multi-source confirmation
  if (lead.found_on_sources && lead.found_on_sources.length > 1) {
    score += 1;
    breakdown.multi_source = `+1 (found on ${lead.found_on_sources.length} platforms)`;
  }

  // Signal 8: Uses free email (gmail/hotmail) as business email
  // Busy business + free email = needs professionalising
  if (lead.email) {
    const emailDomain = lead.email.split('@')[1]?.toLowerCase();
    if (FREE_EMAIL_DOMAINS.includes(emailDomain)) {
      lead.uses_free_email = true;
      // Only boost if they have other growth signals (reviews/hipages)
      if ((lead.google_reviews || 0) >= 5 || (lead.hipages_jobs || 0) >= 5) {
        score += 1;
        breakdown.free_email = '+1 (busy business using free email — needs professionalising)';
      }
    }
  }

  return {
    ...lead,
    score: Math.min(score, 10),
    score_breakdown: breakdown,
  };
}

// n8n Code node entry point — process all items
const results = [];
for (const item of $input.all()) {
  const scored = scoreNoWebsiteLead(item.json);
  results.push({ json: scored });
}
return results;
