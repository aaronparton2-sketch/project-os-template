// Website Existence Checker — 3-Layer Verification
// Problem: Google Maps "no website" just means they didn't fill in the field.
// ~20-30% of "no website" leads actually have websites (confirmed by Aaron's cold calls).
//
// Usage: Copy the functions below into n8n Code nodes.
// Runs between Apify scrape and lead scoring in Pipeline A.
// If a website IS found → reclassify lead to Pipeline B (DIY website check).
//
// Layer 1: URL pattern check (free, instant) — catches ~30-40%
// Layer 2: Google search via Apify (batched, ~$0.001/search) — catches ~80-90% of remainder
// Layer 3: ABN→domain check (free, bonus) — catches edge cases

// ============================================
// SHARED: Directory/social domain exclusion list
// ============================================

// These URLs don't count as "has a website" — they're directory listings, not owned websites
const DIRECTORY_DOMAINS = new Set([
  'facebook.com', 'instagram.com', 'tiktok.com',
  'linkedin.com', 'twitter.com', 'x.com',
  'yellowpages.com.au', 'truelocal.com.au', 'hipages.com.au',
  'yelp.com.au', 'hotfrog.com.au', 'localsearch.com.au',
  'servicepro.com.au', 'oneflare.com.au', 'airtasker.com',
  'google.com', 'google.com.au',  // Google Business Profile URLs
  'youtube.com', 'maps.google.com',
  'startlocal.com.au', 'brownbook.net',
  'infobel.com', 'cylex.com.au',
]);

function isRealWebsite(url) {
  try {
    const hostname = new URL(url).hostname.replace(/^www\./, '');
    for (const dir of DIRECTORY_DOMAINS) {
      if (hostname === dir || hostname.endsWith('.' + dir)) return false;
    }
    return true;
  } catch {
    return false;
  }
}

// Helper: normalise business name to a domain-friendly slug
function toSlug(name) {
  return (name || '')
    .toLowerCase()
    .replace(/[''`']/g, '')       // Remove apostrophes (Jim's → Jims)
    .replace(/&/g, 'and')          // & → and
    .replace(/\bpty\b/g, '')       // Remove "pty"
    .replace(/\bltd\b/g, '')       // Remove "ltd"
    .replace(/[^a-z0-9]+/g, '')    // Remove non-alphanumeric
    .trim();
}

// ============================================
// LAYER 1: URL Pattern Check (Free, Instant)
// ============================================
// n8n Code node — runs on ALL Pipeline A leads after normalisation
// Input: array of lead items
// Output: two arrays — websiteFound[] and needsGoogleSearch[]

async function checkUrlPatterns(businessName, suburb) {
  const slug = toSlug(businessName);
  if (!slug || slug.length < 3) return { found: false };

  const suburbSlug = toSlug(suburb);

  // Common Perth tradie domain patterns
  const patterns = [
    `${slug}.com.au`,
    `${slug}.au`,
    `${slug}.com`,
  ];
  // Only add suburb variants if suburb exists and slug isn't already very long
  if (suburbSlug && slug.length < 20) {
    patterns.push(`${slug}${suburbSlug}.com.au`);
    patterns.push(`${slug}perth.com.au`);
  }

  for (const domain of patterns) {
    try {
      // Quick HEAD request first
      const headResp = await fetch(`https://${domain}`, {
        method: 'HEAD',
        redirect: 'follow',
        signal: AbortSignal.timeout(5000),
      });

      if (headResp.ok || (headResp.status >= 300 && headResp.status < 400)) {
        // Domain responds — now fetch the actual page to check it's not parked
        const getResp = await fetch(`https://${domain}`, {
          redirect: 'follow',
          signal: AbortSignal.timeout(5000),
        });
        const html = await getResp.text();

        // Check for parked/for-sale indicators
        const isParked = /domain.{0,20}(for sale|available|expired)|buy this domain|parked.{0,10}(domain|page)|coming soon|under construction|this site can.t be reached/i.test(html);

        // Check page has real content (not just a blank or minimal page)
        const hasContent = html.length > 2000;

        if (!isParked && hasContent) {
          return { found: true, url: `https://${domain}`, method: 'url_pattern' };
        }
      }
    } catch (e) {
      // Connection refused, timeout, DNS failure = no website at this domain
      continue;
    }

    // Also try HTTP (some old tradie sites don't have SSL)
    try {
      const httpResp = await fetch(`http://${domain}`, {
        method: 'HEAD',
        redirect: 'follow',
        signal: AbortSignal.timeout(5000),
      });

      if (httpResp.ok) {
        const getResp = await fetch(`http://${domain}`, {
          redirect: 'follow',
          signal: AbortSignal.timeout(5000),
        });
        const html = await getResp.text();

        const isParked = /domain.{0,20}(for sale|available|expired)|buy this domain|parked.{0,10}(domain|page)|coming soon|under construction/i.test(html);
        const hasContent = html.length > 2000;

        if (!isParked && hasContent) {
          return { found: true, url: `http://${domain}`, method: 'url_pattern' };
        }
      }
    } catch (e) {
      continue;
    }
  }

  return { found: false };
}


// ============================================
// LAYER 1 — n8n Code Node (copy this into n8n)
// ============================================
// Paste this entire block into an n8n Code node.
// Input: leads from normalisation step
// Output: all items, with websiteFound leads tagged for Pipeline B reclassification
//         and remaining leads tagged as needsGoogleSearch

/*
// --- n8n Code Node: Layer 1 — URL Pattern Check ---

const results = [];

for (const item of $input.all()) {
  const lead = item.json;

  // Skip leads that already have a website or aren't Pipeline A
  if (lead.website && !lead.website.includes('facebook.com')) {
    results.push({ json: { ...lead, _checkStatus: 'has_website' } });
    continue;
  }

  const check = await checkUrlPatterns(lead.business_name, lead.suburb);

  if (check.found) {
    results.push({
      json: {
        ...lead,
        website: check.url,
        website_verified: true,
        website_check_method: check.method,
        website_check_url: check.url,
        pipeline: 'diy_website',
        _checkStatus: 'website_found',
      }
    });
  } else {
    results.push({
      json: {
        ...lead,
        _checkStatus: 'needs_google_search',
      }
    });
  }
}

return results;
*/


// ============================================
// LAYER 2: Google Search Result Processing
// ============================================
// After the Apify Google search actor returns results,
// this function matches them back to leads.

function findWebsiteInSearchResults(searchResults, businessName) {
  if (!searchResults || !Array.isArray(searchResults)) return { found: false };

  for (const result of searchResults) {
    const url = result.url || result.link || '';
    if (!isRealWebsite(url)) continue;

    // Verify the business name appears in the result
    const nameParts = businessName
      .toLowerCase()
      .split(/\s+/)
      .filter(w => w.length > 2 && !['pty', 'ltd', 'the', 'and'].includes(w));

    const titleLower = (result.title || '').toLowerCase();
    const snippetLower = (result.snippet || result.description || '').toLowerCase();

    // At least TWO meaningful words must match, OR the business name slug must appear in the URL
    const matchCount = nameParts.filter(part =>
      titleLower.includes(part) || snippetLower.includes(part)
    ).length;

    const urlSlug = new URL(url).hostname.replace(/^www\./, '').replace(/\.[^.]+\.[^.]+$/, '');
    const nameInUrl = nameParts.some(part => urlSlug.includes(part));

    if (matchCount >= 2 || (matchCount >= 1 && nameInUrl)) {
      return { found: true, url: url, method: 'google_search' };
    }
  }

  return { found: false };
}


// ============================================
// LAYER 2 — n8n Code Node (copy this into n8n)
// ============================================
// Runs AFTER the Apify Google search HTTP Request node returns.
// Input: Apify search results + original leads (via merge)

/*
// --- n8n Code Node: Layer 2 — Process Google Search Results ---

// $input.first() should contain the Apify results
// Match each search result set back to its lead

const apifyResults = $input.first().json; // Array of search result sets
const leads = $('Layer 1 — URL Pattern Check').all()
  .filter(item => item.json._checkStatus === 'needs_google_search');

const results = [];

for (let i = 0; i < leads.length; i++) {
  const lead = leads[i].json;
  const searchResults = apifyResults[i]?.organicResults || apifyResults[i]?.results || [];

  const check = findWebsiteInSearchResults(searchResults, lead.business_name);

  if (check.found) {
    results.push({
      json: {
        ...lead,
        website: check.url,
        website_verified: true,
        website_check_method: check.method,
        website_check_url: check.url,
        pipeline: 'diy_website',
        _checkStatus: 'website_found',
      }
    });
  } else {
    results.push({
      json: {
        ...lead,
        _checkStatus: 'needs_abn_check',
      }
    });
  }
}

return results;
*/


// ============================================
// LAYER 3: ABN→Domain Check (Free, Bonus)
// ============================================

async function checkAbnDomain(abn, businessName) {
  if (!abn) return { found: false };

  const slug = toSlug(businessName);
  if (!slug || slug.length < 3) return { found: false };

  // Only try .com.au — most Australian businesses use this TLD
  const domain = `${slug}.com.au`;

  try {
    const response = await fetch(`https://${domain}`, {
      method: 'HEAD',
      redirect: 'follow',
      signal: AbortSignal.timeout(5000),
    });

    if (response.ok) {
      return { found: true, url: `https://${domain}`, method: 'abn_whois' };
    }
  } catch {
    // Domain doesn't exist or isn't reachable
  }

  return { found: false };
}


// ============================================
// LAYER 3 — n8n Code Node (copy this into n8n)
// ============================================

/*
// --- n8n Code Node: Layer 3 — ABN Domain Check ---

const results = [];

for (const item of $input.all()) {
  const lead = item.json;

  if (lead._checkStatus !== 'needs_abn_check') {
    results.push(item);
    continue;
  }

  const check = await checkAbnDomain(lead.abn, lead.business_name);

  if (check.found) {
    results.push({
      json: {
        ...lead,
        website: check.url,
        website_verified: true,
        website_check_method: check.method,
        website_check_url: check.url,
        pipeline: 'diy_website',
        _checkStatus: 'website_found',
      }
    });
  } else {
    // All 3 layers checked — confirmed no website
    results.push({
      json: {
        ...lead,
        website_verified: true,
        website_check_method: 'none_found',
        website_check_url: null,
        pipeline: 'no_website',
        _checkStatus: 'confirmed_no_website',
      }
    });
  }
}

return results;
*/


// ============================================
// APIFY GOOGLE SEARCH — Batch Query Builder
// ============================================
// Use this to build the Apify actor input from leads that need Google search

function buildGoogleSearchQueries(leads) {
  return leads.map(lead => {
    const name = lead.business_name || '';
    const suburb = lead.suburb || '';
    // Quote the business name for exact match
    return `"${name}" ${suburb}`.trim();
  });
}

// Apify actor: tuningsearch/cheap-google-search-results-scraper
// POST https://api.apify.com/v2/acts/tuningsearch~cheap-google-search-results-scraper/runs
// Body:
// {
//   "queries": buildGoogleSearchQueries(leads),
//   "maxResults": 5,
//   "countryCode": "au",
//   "languageCode": "en"
// }
// Headers: { "Authorization": "Bearer YOUR_APIFY_TOKEN" }


// ============================================
// EXPORTS (for Node.js testing)
// ============================================

if (typeof module !== 'undefined') {
  module.exports = {
    checkUrlPatterns,
    findWebsiteInSearchResults,
    checkAbnDomain,
    isRealWebsite,
    toSlug,
    buildGoogleSearchQueries,
    DIRECTORY_DOMAINS,
  };
}
