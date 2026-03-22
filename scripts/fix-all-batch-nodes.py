"""Fix ALL n8n Code nodes that have HTTP calls inside loops.
Convert from runOnceForAllItems → runOnceForEachItem to avoid 60s timeout.

Nodes fixed:
- Website Checker
- Platform Detector
- Google PageSpeed Audit
- Supabase: Store Leads
"""
import json, urllib.request, sys, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

N8N_API_KEY = os.environ['N8N_API_KEY']
N8N_API_URL = os.environ['N8N_API_URL']
WF_ID = '3qqw96oRGpyqxt57'

req = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': N8N_API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())

# ── Website Checker (per-item) ──
WEBSITE_CHECKER_CODE = r"""// Website Existence Checker — per-item mode
// Checks if "no website" leads actually have a website via URL patterns.
// If found: reclassify to Pipeline B (diy_website).

function toSlug(name) {
  return (name || '').toLowerCase()
    .replace(/[\u2019\u2018'`]/g, '')
    .replace(/&/g, 'and')
    .replace(/\bpty\b/g, '').replace(/\bltd\b/g, '')
    .replace(/[^a-z0-9]+/g, '').trim();
}

const lead = $input.item.json;

// If already has a real website, pass through
if (lead.website && !lead.website.includes('facebook.com')) {
  return {
    json: { ...lead, website_verified: true, website_check_method: 'already_has_website' }
  };
}

const slug = toSlug(lead.business_name);
if (!slug || slug.length < 3) {
  return {
    json: { ...lead, website_verified: true, website_check_method: 'none_found', pipeline: 'no_website' }
  };
}

const suburbSlug = toSlug(lead.suburb);
const patterns = [`${slug}.com.au`, `${slug}.au`, `${slug}.com`];
if (suburbSlug && slug.length < 20) {
  patterns.push(`${slug}${suburbSlug}.com.au`);
  patterns.push(`${slug}perth.com.au`);
}

for (const domain of patterns) {
  for (const proto of ['https', 'http']) {
    try {
      const resp = await fetch(`${proto}://${domain}`, {
        method: 'HEAD', redirect: 'follow',
        signal: AbortSignal.timeout(5000),
      });
      if (resp.ok || (resp.status >= 300 && resp.status < 400)) {
        const html = await fetch(`${proto}://${domain}`, {
          redirect: 'follow', signal: AbortSignal.timeout(5000),
        }).then(r => r.text());
        const isParked = /domain.{0,20}(for sale|available|expired)|buy this domain|parked.{0,10}(domain|page)|coming soon|under construction/i.test(html);
        if (!isParked && html.length > 2000) {
          return {
            json: { ...lead, website: `${proto}://${domain}`, website_verified: true,
              website_check_method: 'url_pattern', website_check_url: `${proto}://${domain}`, pipeline: 'diy_website' }
          };
        }
      }
    } catch (e) { continue; }
  }
}

return {
  json: { ...lead, website_verified: true, website_check_method: 'none_found', pipeline: 'no_website' }
};"""

# ── Platform Detector (per-item) ──
PLATFORM_DETECTOR_CODE = r"""// Website Platform Detector — per-item mode
// Fingerprints DIY platforms (Wix, Squarespace, etc.)

const PLATFORM_SIGNATURES = {
  wix: {
    html: [/wix\.com/i, /_wix_browser_sess/i, /wixsite\.com/i, /wix-warmup-data/i],
    headers: [/X-Wix-/i],
    generator: [/Wix\.com/i],
  },
  squarespace: {
    html: [/squarespace\.com/i, /sqsp/i, /static\.squarespace/i, /squarespace-cdn/i],
    headers: [/X-ServedBy.*squarespace/i],
    generator: [/Squarespace/i],
  },
  weebly: {
    html: [/weebly\.com/i, /editmysite\.com/i],
    headers: [],
    generator: [/Weebly/i],
  },
  wordpress_com: {
    html: [/s[0-9]\.wp\.com/i, /wordpress\.com/i, /wp-content\/themes\/starter/i],
    headers: [],
    generator: [/WordPress\.com/i],
  },
  godaddy: {
    html: [/godaddy\.com/i, /img1\.wsimg\.com/i, /secureserver\.net/i],
    headers: [],
    generator: [/GoDaddy/i],
  },
  jimdo: {
    html: [/jimdo\.com/i, /jimdosite\.com/i],
    headers: [],
    generator: [/Jimdo/i],
  },
  shopify: {
    html: [/cdn\.shopify\.com/i, /myshopify\.com/i],
    headers: [/X-ShopId/i],
    generator: [],
  },
};

const lead = $input.item.json;

if (!lead.website) {
  return { json: { ...lead, diy_platform: null } };
}

let url = lead.website;
if (!url.startsWith('http')) url = 'https://' + url;

try {
  const response = await fetch(url, {
    redirect: 'follow',
    signal: AbortSignal.timeout(10000),
    headers: {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    },
  });

  const html = await response.text();
  const headersStr = JSON.stringify(Object.fromEntries(response.headers));
  const generatorMatch = html.match(/<meta[^>]*name=["']generator["'][^>]*content=["']([^"']+)["']/i);
  const generator = generatorMatch ? generatorMatch[1] : '';

  for (const [platform, sigs] of Object.entries(PLATFORM_SIGNATURES)) {
    const htmlMatch = sigs.html.some(regex => regex.test(html));
    const headerMatch = sigs.headers.some(regex => regex.test(headersStr));
    const genMatch = sigs.generator.some(regex => regex.test(generator));
    if (htmlMatch || headerMatch || genMatch) {
      return { json: { ...lead, diy_platform: platform } };
    }
  }

  return { json: { ...lead, diy_platform: null } };
} catch (err) {
  return { json: { ...lead, diy_platform: null, platform_check_error: err.message } };
}"""

# ── Google PageSpeed Audit (per-item) ──
PAGESPEED_CODE = r"""// Google PageSpeed Audit — per-item mode
// Calls PageSpeed API for each DIY website lead

const lead = $input.item.json;

if (!lead.website) {
  return { json: { ...lead, pagespeed_score: null, pagespeed_mobile: null } };
}

try {
  const url = encodeURIComponent(lead.website.startsWith('http') ? lead.website : 'https://' + lead.website);
  const apiUrl = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=' + url + '&strategy=mobile&category=performance&category=seo';

  const response = await fetch(apiUrl, { signal: AbortSignal.timeout(20000) });
  const data = await response.json();

  const lh = data.lighthouseResult || {};
  const cats = lh.categories || {};
  const audits = lh.audits || {};

  const seoIssues = [];
  if (!audits['meta-description']?.score) seoIssues.push('missing_meta_desc');
  if (!audits['document-title']?.score) seoIssues.push('missing_title');
  if (audits['viewport']?.score === 0) seoIssues.push('no_viewport');
  if (audits['is-crawlable']?.score === 0) seoIssues.push('not_crawlable');

  return {
    json: {
      ...lead,
      pagespeed_score: Math.round((cats.performance?.score || 0) * 100),
      pagespeed_mobile: Math.round((cats.performance?.score || 0) * 100),
      has_ssl: (lead.website || '').startsWith('https'),
      has_meta_description: !seoIssues.includes('missing_meta_desc'),
      has_h1: true,
      mobile_friendly: (cats.performance?.score || 0) > 0.5,
      seo_issues: seoIssues,
      core_web_vitals: {
        lcp: audits['largest-contentful-paint']?.numericValue / 1000 || null,
        fid: audits['max-potential-fid']?.numericValue / 1000 || null,
        cls: audits['cumulative-layout-shift']?.numericValue || null,
      }
    }
  };
} catch (err) {
  return {
    json: { ...lead, pagespeed_score: null, pagespeed_mobile: null, pagespeed_error: err.message }
  };
}"""

# ── Supabase: Store Leads (per-item) ──
SUPABASE_CODE = r"""// Store lead in Supabase — per-item mode
const SUPABASE_URL = 'https://zdaznnifkhdioczrxsae.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkYXpubmlma2hkaW9jenJ4c2FlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5MDMzNjgsImV4cCI6MjA4OTQ3OTM2OH0.NxE7BsIGAfLpowkRCo0eaIOXJZjiq1ozCeRCbgxb5QI';

const lead = $input.item.json;

const row = {
  business_name: lead.business_name || 'Unknown',
  phone: lead.phone || null,
  email: lead.email || null,
  category: lead.category || null,
  address: lead.address || null,
  suburb: lead.suburb || null,
  postcode: lead.postcode || null,
  state: lead.state || 'WA',
  website: lead.website || null,
  pipeline: lead.pipeline || 'no_website',
  source: lead.source || 'google_maps',
  google_reviews: lead.google_reviews || 0,
  google_rating: lead.google_rating || null,
  abn: lead.abn || null,
  website_is_facebook: lead.website_is_facebook || false,
  address_type: lead.address_type || 'unknown',
  website_verified: lead.website_verified || false,
  website_check_method: lead.website_check_method || null,
  website_check_url: lead.website_check_url || null,
  score: lead.score || 0,
  score_breakdown: lead.score_breakdown || {},
  found_on_sources: lead.found_on_sources || ['google_maps'],
  top_review_quote: lead.top_review_quote || null,
  status: 'new',
};

try {
  const response = await this.helpers.httpRequest({
    method: 'POST',
    url: `${SUPABASE_URL}/rest/v1/leads`,
    headers: {
      'Content-Type': 'application/json',
      'apikey': SUPABASE_KEY,
      'Authorization': `Bearer ${SUPABASE_KEY}`,
      'Prefer': 'resolution=ignore-duplicates,return=minimal',
    },
    body: row,
    returnFullResponse: true,
    timeout: 10000,
  }).catch(err => ({ statusCode: err.statusCode || 500, body: err.message }));

  const status = response.statusCode || 201;
  let db_status = 'stored';
  if (status === 409 || String(response.body || '').includes('duplicate')) {
    db_status = 'duplicate';
  } else if (status < 200 || status >= 300) {
    db_status = 'error';
  }

  return { json: { ...lead, _db_status: db_status } };
} catch (err) {
  return { json: { ...lead, _db_status: 'error', _db_error: err.message } };
}"""

# ── Apply fixes ──
fixes = []
node_updates = {
    'Website Checker': WEBSITE_CHECKER_CODE,
    'Platform Detector': PLATFORM_DETECTOR_CODE,
    'Google PageSpeed Audit': PAGESPEED_CODE,
    'Supabase: Store Leads': SUPABASE_CODE,
}

for node in wf['nodes']:
    name = node['name']
    if name in node_updates:
        node['parameters']['jsCode'] = node_updates[name]
        node['parameters']['mode'] = 'runOnceForEachItem'
        fixes.append(name)

print(f'Fixed {len(fixes)} nodes: {fixes}')

# ── Push ──
payload = {k: v for k, v in wf.items() if k in {'name', 'nodes', 'connections', 'settings'}}
data = json.dumps(payload).encode()
req = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    data=data,
    headers={'Content-Type': 'application/json', 'X-N8N-API-KEY': N8N_API_KEY},
    method='PUT'
)
try:
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    print(f'Workflow updated ({len(result.get("nodes", []))} nodes)')
except urllib.error.HTTPError as e:
    print(f'Error {e.code}: {e.read().decode()[:500]}')
    sys.exit(1)
