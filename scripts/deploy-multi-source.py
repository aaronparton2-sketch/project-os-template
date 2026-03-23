"""Deploy Multi-Source Lead Pipeline to n8n workflow.

Architecture:
  Region Picker → Source Allocator
      ├─→ Apify: Google Maps (No Website) → Filter & Normalise → Website Checker ──→ Merge Pipeline A
      ├─→ Fetch HiPages + ABR (Code) → Filter Multi-Source ────────────────────→ Merge Pipeline A
      └─→ Apify: Google Maps (Has Website) → Filter & Normalise (Has Website) → [Pipeline B chain]

  Merge Pipeline A → Lead Scorer A → Tag & Pass → Social → Build Prompt A → ...

Also:
  - Upgraded daily digest (source splits, phone numbers, reply analytics, spreadsheet link)
  - Write to Pipeline Leads Google Sheet tab
"""
import json, urllib.request, subprocess, sys, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

N8N_API_KEY = os.environ['N8N_API_KEY']
N8N_API_URL = os.environ['N8N_API_URL']
OPENAI_KEY = os.environ['OPENAI_API_KEY']
APIFY_TOKEN = os.environ['APIFY_API_TOKEN']
ABR_GUID = os.environ['ABR_GUID']
PIPELINE_PROJECT_REF = os.environ['SUPABASE_PIPELINE_PROJECT_REF']
SUPABASE_ACCESS_TOKEN = os.environ['SUPABASE_ACCESS_TOKEN']
GOOGLE_SA_JSON = os.environ['GOOGLE_SERVICE_ACCOUNT_JSON']
SHEETS_ID = os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID', '')
WF_ID = '3qqw96oRGpyqxt57'

print('Step 1: Fetching workflow...')
req = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': N8N_API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())
print(f'  Loaded: {len(wf["nodes"])} nodes')

# ═══════════════════════════════════════════════════════════════
# NODE CODE DEFINITIONS
# ═══════════════════════════════════════════════════════════════

# --- SOURCE ALLOCATOR ---
SOURCE_ALLOCATOR_CODE = r"""// Source Allocator — determines daily mix across 4 sources
// Reads region from Region Picker, outputs config for all downstream scrapers

const regionData = $input.item.json;

// Skip if no region available
if (regionData._no_region || regionData._skip) {
  return [{ json: { ...regionData, _skip: true } }];
}

// Source percentage split (tunable)
const SPLIT = {
  google_maps_no_website: 0.30,  // 30%
  hipages: 0.20,                 // 20%
  abr: 0.20,                    // 20%
  google_maps_has_website: 0.30, // 30%
};

const DAILY_TARGET = 100;

// Calculate maxItems per source
const gmapsNoWebMax = Math.round(DAILY_TARGET * SPLIT.google_maps_no_website);
const hipagesMax = Math.round(DAILY_TARGET * SPLIT.hipages);
const abrMax = Math.round(DAILY_TARGET * SPLIT.abr);
const gmapsHasWebMax = Math.round(DAILY_TARGET * SPLIT.google_maps_has_website);

// Determine state for ABR based on region
const regionState = regionData._region_state || 'WA';
const regionName = regionData._region_name || 'Perth, Western Australia';

// Build postcode range for ABR based on state
const STATE_POSTCODES = {
  WA: { start: 6000, end: 6999 },
  NSW: { start: 2000, end: 2999 },
  VIC: { start: 3000, end: 3999 },
  QLD: { start: 4000, end: 4999 },
  SA: { start: 5000, end: 5999 },
  TAS: { start: 7000, end: 7999 },
  NT: { start: 800, end: 899 },
  ACT: { start: 2600, end: 2620 },
};

const postcodeRange = STATE_POSTCODES[regionState] || STATE_POSTCODES.WA;

return [{
  json: {
    ...regionData,
    _source_config: {
      gmaps_no_website_max: gmapsNoWebMax,
      hipages_max: hipagesMax,
      abr_max: abrMax,
      gmaps_has_website_max: gmapsHasWebMax,
      daily_target: DAILY_TARGET,
      split: SPLIT,
    },
    _abr_config: {
      state: regionState,
      postcode_start: postcodeRange.start,
      postcode_end: postcodeRange.end,
    },
    _hipages_region: regionName.split(',')[0].trim(),
    _hipages_state: regionState,
  }
}];"""

# --- FETCH HIPAGES + ABR COMBINED ---
FETCH_HIPAGES_ABR_CODE = f'''// Fetch HiPages + ABR Combined
// Runs both sources in parallel and outputs merged leads

const config = $input.item.json;
if (config._skip) return [{{ json: {{ _skip: true, _leads: [] }} }}];

const ABR_GUID = '{ABR_GUID}';
const APIFY_TOKEN = '{APIFY_TOKEN}';
const hipagesRegion = config._hipages_region || 'Perth';
const hipagesState = config._hipages_state || 'WA';
const abrState = config._abr_config?.state || 'WA';
const abrPostcodeStart = config._abr_config?.postcode_start || 6000;
const abrPostcodeEnd = config._abr_config?.postcode_end || 6999;
const hipagesMax = config._source_config?.hipages_max || 20;
const abrMax = config._source_config?.abr_max || 20;

const allLeads = [];

// ═════════════════════════════════
// ABR — SOAP API for new registrations
// ═════════════════════════════════

const ABR_ENDPOINT = 'https://abr.business.gov.au/abrxmlsearch/AbrXmlSearch.asmx';
const TRADE_SEARCHES = [
  'plumber', 'electrician', 'builder', 'landscap', 'clean', 'painter',
  'roof', 'concret', 'fencing', 'carpent', 'pest control', 'air conditioning',
  'tiling', 'handyman', 'solar', 'pool', 'glass', 'mechanic', 'removalist',
];

// State flags for ABR SOAP
const stateFlags = {{
  WA: {{ WA: 'Y', NSW: 'N', VIC: 'N', QLD: 'N', SA: 'N', TAS: 'N', NT: 'N', ACT: 'N' }},
  NSW: {{ WA: 'N', NSW: 'Y', VIC: 'N', QLD: 'N', SA: 'N', TAS: 'N', NT: 'N', ACT: 'N' }},
  VIC: {{ WA: 'N', NSW: 'N', VIC: 'Y', QLD: 'N', SA: 'N', TAS: 'N', NT: 'N', ACT: 'N' }},
  QLD: {{ WA: 'N', NSW: 'N', VIC: 'N', QLD: 'Y', SA: 'N', TAS: 'N', NT: 'N', ACT: 'N' }},
  SA: {{ WA: 'N', NSW: 'N', VIC: 'N', QLD: 'N', SA: 'Y', TAS: 'N', NT: 'N', ACT: 'N' }},
  TAS: {{ WA: 'N', NSW: 'N', VIC: 'N', QLD: 'N', SA: 'N', TAS: 'Y', NT: 'N', ACT: 'N' }},
  NT: {{ WA: 'N', NSW: 'N', VIC: 'N', QLD: 'N', SA: 'N', TAS: 'N', NT: 'Y', ACT: 'N' }},
  ACT: {{ WA: 'N', NSW: 'N', VIC: 'N', QLD: 'N', SA: 'N', TAS: 'N', NT: 'N', ACT: 'Y' }},
}};
const flags = stateFlags[abrState] || stateFlags.WA;

const seenAbns = new Set();
let abrCount = 0;

for (const trade of TRADE_SEARCHES) {{
  if (abrCount >= abrMax) break;

  const soapBody = `<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"
                 xmlns:abr="http://abr.business.gov.au/ABRXMLSearch/">
  <soap12:Body>
    <abr:ABRSearchByNameAdvancedSimpleProtocol2017>
      <abr:name>${{trade}}</abr:name>
      <abr:postcode></abr:postcode>
      <abr:legalName>Y</abr:legalName>
      <abr:tradingName>Y</abr:tradingName>
      <abr:businessName>Y</abr:businessName>
      <abr:activeABNsOnly>Y</abr:activeABNsOnly>
      <abr:NSW>${{flags.NSW}}</abr:NSW>
      <abr:SA>${{flags.SA}}</abr:SA>
      <abr:ACT>${{flags.ACT}}</abr:ACT>
      <abr:VIC>${{flags.VIC}}</abr:VIC>
      <abr:WA>${{flags.WA}}</abr:WA>
      <abr:NT>${{flags.NT}}</abr:NT>
      <abr:QLD>${{flags.QLD}}</abr:QLD>
      <abr:TAS>${{flags.TAS}}</abr:TAS>
      <abr:authenticationGuid>${{ABR_GUID}}</abr:authenticationGuid>
      <abr:searchWidth>typical</abr:searchWidth>
      <abr:minimumScore>80</abr:minimumScore>
      <abr:maxSearchResults>50</abr:maxSearchResults>
    </abr:ABRSearchByNameAdvancedSimpleProtocol2017>
  </soap12:Body>
</soap12:Envelope>`;

  try {{
    const response = await this.helpers.httpRequest({{
      method: 'POST',
      url: ABR_ENDPOINT,
      headers: {{ 'Content-Type': 'application/soap+xml; charset=utf-8' }},
      body: soapBody,
      timeout: 30000,
      returnFullResponse: false,
    }});

    // Parse XML response (simple regex extraction since n8n doesn't have xml parser)
    const xml = typeof response === 'string' ? response : JSON.stringify(response);

    // Extract ABN records
    const records = xml.split('<searchResultsRecord>').slice(1);
    const now = new Date();
    const sevenDaysAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);

    for (const record of records) {{
      if (abrCount >= abrMax) break;

      const abnMatch = record.match(/<identifierValue>(\d+)<\\/identifierValue>/);
      if (!abnMatch) continue;
      const abn = abnMatch[1];
      if (seenAbns.has(abn)) continue;

      // Get name
      let name = '';
      const orgMatch = record.match(/<organisationName>([^<]+)<\\/organisationName>/);
      if (orgMatch) name = orgMatch[1];
      if (!name) {{
        const famMatch = record.match(/<familyName>([^<]+)<\\/familyName>/);
        const givMatch = record.match(/<givenName>([^<]+)<\\/givenName>/);
        if (famMatch) name = (givMatch ? givMatch[1] + ' ' : '') + famMatch[1];
      }}
      if (!name) continue;

      // Get postcode and state
      const pcMatch = record.match(/<postcode>(\d+)<\\/postcode>/);
      const stMatch = record.match(/<stateCode>([A-Z]+)<\\/stateCode>/);
      const postcode = pcMatch ? pcMatch[1] : '';
      const state = stMatch ? stMatch[1] : '';

      if (state !== abrState) continue;
      const pc = parseInt(postcode);
      if (pc < abrPostcodeStart || pc > abrPostcodeEnd) continue;

      // Check registration date (within 7 days)
      const dateMatch = record.match(/<replacedFrom>([\\d-]+)/);
      let regDate = null;
      if (dateMatch) {{
        regDate = new Date(dateMatch[1]);
        if (regDate < sevenDaysAgo) continue;
      }}

      seenAbns.add(abn);
      abrCount++;
      allLeads.push({{
        business_name: name.trim(),
        abn: abn,
        postcode: postcode,
        state: state,
        source: 'abr',
        pipeline: 'no_website',
        category: trade,
        registration_date: regDate ? regDate.toISOString().slice(0, 10) : null,
        address_type: (['6000','6001','6003','6004','6005'].includes(postcode)) ? 'cbd' : 'residential',
        region: config._region_name || null,
        score: 0,
      }});
    }}
  }} catch (e) {{
    // ABR call failed for this trade, continue with others
  }}
}}

// ═════════════════════════════════
// HIPAGES — Apify Web Scraper
// ═════════════════════════════════

const HIPAGES_CATEGORIES = [
  'plumber', 'electrician', 'builder', 'landscaper', 'painter',
  'roofer', 'concreter', 'fencer', 'carpenter', 'tiler',
  'air-conditioning', 'pest-control', 'cleaner', 'handyman',
];

// Use Apify Cheerio Crawler to scrape HiPages search results
const hipagesUrls = HIPAGES_CATEGORIES.slice(0, 5).map(cat =>
  ({{ url: `https://hipages.com.au/find/${{cat}}/in/${{hipagesRegion.toLowerCase().replace(/\\s+/g, '-')}}` }})
);

try {{
  const hipagesResult = await this.helpers.httpRequest({{
    method: 'POST',
    url: `https://api.apify.com/v2/acts/apify~cheerio-scraper/run-sync-get-dataset-items?token=${{APIFY_TOKEN}}`,
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{
      startUrls: hipagesUrls,
      maxRequestsPerCrawl: hipagesMax,
      pageFunction: `async function pageFunction(context) {{
        const {{ $, request }} = context;
        const results = [];
        $('[data-testid="business-card"], .business-card, .search-result').each((i, el) => {{
          const name = $(el).find('[data-testid="business-name"], .business-name, h3').first().text().trim();
          const phone = $(el).find('[data-testid="phone"], .phone-number, a[href^="tel:"]').first().text().trim();
          const category = request.url.split('/find/')[1]?.split('/')[0] || '';
          const suburb = $(el).find('.location, .suburb, [data-testid="location"]').first().text().trim();
          if (name) results.push({{ name, phone, category, suburb }});
        }});
        return results;
      }}`,
    }}),
    timeout: 120000,
  }});

  const hipagesLeads = Array.isArray(hipagesResult) ? hipagesResult : [];
  for (const hp of hipagesLeads.slice(0, hipagesMax)) {{
    if (!hp.name) continue;
    allLeads.push({{
      business_name: hp.name,
      phone: (hp.phone || '').replace(/\\D/g, ''),
      category: hp.category || '',
      suburb: hp.suburb || hipagesRegion,
      state: hipagesState,
      source: 'hipages',
      pipeline: 'no_website',
      region: config._region_name || null,
      address_type: 'unknown',
      score: 0,
    }});
  }}
}} catch (e) {{
  // HiPages scraping failed, continue with ABR leads only
}}

// Output all leads as individual items
if (allLeads.length === 0) {{
  return [{{ json: {{ _skip: true, _source: 'hipages_abr', _count: 0 }} }}];
}}

return allLeads.map(lead => ({{ json: lead }}));'''

# --- FILTER MULTI-SOURCE ---
FILTER_MULTI_SOURCE_CODE = r"""// Filter Multi-Source Leads — normalize HiPages + ABR leads
// Ensures schema matches Pipeline A format for merging

const lead = $input.item.json;

// Skip empty items
if (lead._skip) return [];

// Normalize to standard schema
const normalized = {
  business_name: lead.business_name || 'Unknown',
  phone: (lead.phone || '').replace(/\D/g, ''),
  email: lead.email || null,
  category: lead.category || '',
  address: lead.address || null,
  suburb: lead.suburb || null,
  postcode: lead.postcode || null,
  state: lead.state || 'WA',
  website: lead.website || null,
  pipeline: lead.pipeline || 'no_website',
  source: lead.source || 'unknown',
  google_reviews: lead.google_reviews || 0,
  google_rating: lead.google_rating || null,
  abn: lead.abn || null,
  website_is_facebook: false,
  address_type: lead.address_type || 'unknown',
  website_verified: false,
  website_check_method: null,
  website_check_url: null,
  score: 0,
  score_breakdown: {},
  found_on_sources: [lead.source || 'unknown'],
  top_review_quote: null,
  region: lead.region || null,
  registration_date: lead.registration_date || null,
};

// Skip leads without a business name
if (!normalized.business_name || normalized.business_name === 'Unknown') return [];

return { json: normalized };"""

# --- DEDUPLICATE ---
# Actually, we'll handle dedup in the Merge node itself

# --- APIFY: GOOGLE MAPS (HAS WEBSITE) for Pipeline B ---
# This is an HTTP Request node, configured via parameters (not code)

# --- UPGRADED DAILY DIGEST ---
QUERY_TODAYS_DATA_CODE = f'''// Query Today's Data — comprehensive multi-source stats
const PROJECT_REF = '{PIPELINE_PROJECT_REF}';
const ACCESS_TOKEN = '{SUPABASE_ACCESS_TOKEN}';
const API_URL = `https://api.supabase.com/v1/projects/${{PROJECT_REF}}/database/query`;

async function query(sql) {{
  try {{
    return await this.helpers.httpRequest({{
      method: 'POST',
      url: API_URL,
      headers: {{
        'Authorization': `Bearer ${{ACCESS_TOKEN}}`,
        'Content-Type': 'application/json',
      }},
      body: {{ query: sql }},
      timeout: 15000,
    }});
  }} catch (e) {{
    return [];
  }}
}}

const today = new Date().toISOString().slice(0, 10);

const [
  todayLeads,
  sourceCounts,
  priorityCalls,
  replyStats,
  sourcePerf,
  tradePerf,
  variantPerf,
] = await Promise.all([
  query(`SELECT COUNT(*) as total FROM leads WHERE created_at::date = '${{today}}';`),
  query(`SELECT source, COUNT(*) as count FROM leads WHERE created_at::date = '${{today}}' GROUP BY source ORDER BY count DESC;`),
  query(`SELECT business_name, category, phone, score, source, suburb, call_script, email_variant, personalisation_type
    FROM leads WHERE created_at::date = '${{today}}' AND score >= 7
    ORDER BY score DESC LIMIT 20;`),
  query(`SELECT
    COUNT(*) FILTER (WHERE event_type = 'email_sent') as sent,
    COUNT(*) FILTER (WHERE event_type = 'email_opened') as opened,
    COUNT(*) FILTER (WHERE event_type = 'email_replied') as replied,
    COUNT(*) FILTER (WHERE event_type = 'email_bounced') as bounced
    FROM outreach_events WHERE created_at > NOW() - INTERVAL '7 days';`),
  query(`SELECT l.source,
    COUNT(*) FILTER (WHERE e.event_type = 'email_sent') as sent,
    COUNT(*) FILTER (WHERE e.event_type = 'email_replied') as replied,
    ROUND(COUNT(*) FILTER (WHERE e.event_type = 'email_replied')::numeric / NULLIF(COUNT(*) FILTER (WHERE e.event_type = 'email_sent'), 0) * 100, 1) as reply_rate
    FROM outreach_events e JOIN leads l ON e.lead_id = l.id
    WHERE e.created_at > NOW() - INTERVAL '14 days'
    GROUP BY l.source;`),
  query(`SELECT trade_category, email_reply_rate FROM trade_performance ORDER BY email_reply_rate DESC NULLS LAST LIMIT 5;`),
  query(`SELECT variant, reply_rate FROM email_variant_performance ORDER BY reply_rate DESC NULLS LAST LIMIT 5;`),
]);

return [{{
  json: {{
    date: today,
    total: todayLeads?.[0]?.total || 0,
    sources: sourceCounts || [],
    priority_calls: priorityCalls || [],
    reply_stats: replyStats?.[0] || {{}},
    source_performance: sourcePerf || [],
    trade_performance: tradePerf || [],
    variant_performance: variantPerf || [],
    spreadsheet_url: 'https://docs.google.com/spreadsheets/d/{SHEETS_ID}/edit#gid=0',
  }}
}}];'''

BUILD_DIGEST_CODE = r"""// Build HTML Digest — multi-source command centre
const d = $input.item.json;

const total = d.total || 0;
const sources = d.sources || [];
const calls = d.priority_calls || [];
const rs = d.reply_stats || {};
const sp = d.source_performance || [];
const tp = d.trade_performance || [];
const vp = d.variant_performance || [];

let html = `<div style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto">`;
html += `<h2 style="border-bottom:2px solid #333;padding-bottom:8px">Daily Lead Digest - ${d.date}</h2>`;

// Summary
html += `<div style="background:#f8f8f8;padding:16px;border-radius:8px;margin:16px 0">`;
html += `<h3 style="margin:0 0 8px">Summary</h3>`;
html += `<p style="font-size:24px;font-weight:bold;margin:0">${total} leads processed today</p>`;
html += `<p style="margin:4px 0">${calls.length} priority calls (score 7+)</p>`;
html += `</div>`;

// Source breakdown
if (sources.length > 0) {
  html += `<h3>Source Breakdown</h3><table style="border-collapse:collapse;width:100%">`;
  html += `<tr style="background:#e8e8e8"><th style="padding:8px;text-align:left">Source</th><th style="padding:8px;text-align:right">Leads</th><th style="padding:8px;text-align:right">%</th><th style="padding:8px">Bar</th></tr>`;
  const sourceLabels = { google_maps: 'Google Maps (no website)', hipages: 'HiPages', abr: 'ABR (new reg)', diy_website: 'DIY Websites' };
  for (const s of sources) {
    const pct = total > 0 ? Math.round(s.count / total * 100) : 0;
    const bar = '█'.repeat(Math.max(1, Math.round(pct / 5)));
    const label = sourceLabels[s.source] || s.source;
    html += `<tr><td style="padding:6px">${label}</td><td style="padding:6px;text-align:right">${s.count}</td><td style="padding:6px;text-align:right">${pct}%</td><td style="padding:6px;color:#4a90d9">${bar}</td></tr>`;
  }
  html += `</table>`;
}

// Priority calls
if (calls.length > 0) {
  html += `<h3>Priority Calls (score 7+)</h3>`;
  html += `<table style="border-collapse:collapse;width:100%">`;
  html += `<tr style="background:#e8e8e8"><th style="padding:6px;text-align:left">Business</th><th style="padding:6px">Trade</th><th style="padding:6px">Phone</th><th style="padding:6px">Score</th><th style="padding:6px">Source</th></tr>`;
  for (const c of calls) {
    const phone = c.phone || '-';
    const sourceShort = { google_maps: 'GMaps', hipages: 'HiPg', abr: 'ABR', diy_website: 'DIY' }[c.source] || c.source;
    html += `<tr><td style="padding:6px"><b>${c.business_name}</b><br><span style="color:#666;font-size:12px">${c.suburb || ''}</span></td><td style="padding:6px;text-align:center">${c.category}</td><td style="padding:6px;text-align:center"><a href="tel:${phone}">${phone}</a></td><td style="padding:6px;text-align:center"><b>${c.score}/10</b></td><td style="padding:6px;text-align:center">${sourceShort}</td></tr>`;
  }
  html += `</table>`;
  html += `<p><a href="${d.spreadsheet_url}" style="color:#4a90d9;font-weight:bold">Open Pipeline Leads spreadsheet (call scripts + emails)</a></p>`;
}

// Reply analytics (7-day rolling)
const sent = rs.sent || 0;
const opened = rs.opened || 0;
const replied = rs.replied || 0;
const bounced = rs.bounced || 0;
if (sent > 0) {
  html += `<h3>Reply Analytics (last 7 days)</h3>`;
  html += `<table style="border-collapse:collapse;width:100%">`;
  html += `<tr><td style="padding:6px">Emails sent</td><td style="padding:6px;text-align:right"><b>${sent}</b></td></tr>`;
  html += `<tr style="background:#f8f8f8"><td style="padding:6px">Opened</td><td style="padding:6px;text-align:right">${opened} (${Math.round(opened/sent*100)}%)</td></tr>`;
  html += `<tr><td style="padding:6px">Replied</td><td style="padding:6px;text-align:right"><b>${replied} (${Math.round(replied/sent*100)}%)</b></td></tr>`;
  html += `<tr style="background:#f8f8f8"><td style="padding:6px">Bounced</td><td style="padding:6px;text-align:right">${bounced} (${Math.round(bounced/sent*100)}%)</td></tr>`;
  html += `</table>`;

  // Source performance
  if (sp.length > 0) {
    html += `<h4>By Source (14-day)</h4><table style="border-collapse:collapse;width:100%">`;
    for (const s of sp) {
      const label = { google_maps: 'Google Maps', hipages: 'HiPages', abr: 'ABR', diy_website: 'DIY' }[s.source] || s.source;
      html += `<tr><td style="padding:4px">${label}</td><td style="padding:4px;text-align:right">${s.reply_rate || 0}% reply rate (${s.sent} sent)</td></tr>`;
    }
    html += `</table>`;
  }

  // Best trade + variant
  if (tp.length > 0) {
    html += `<p>Best trade: <b>${tp[0].trade_category}</b> (${tp[0].email_reply_rate}% reply rate)</p>`;
  }
  if (vp.length > 0) {
    html += `<p>Best variant: <b>${vp[0].variant}</b> (${vp[0].reply_rate}% reply rate)</p>`;
  }
}

// Suggestions
html += `<h3>Suggestions</h3><ul>`;
if (sp.length >= 2) {
  const sorted = [...sp].sort((a, b) => (b.reply_rate || 0) - (a.reply_rate || 0));
  if ((sorted[0].reply_rate || 0) > (sorted[sorted.length-1].reply_rate || 0) * 2) {
    const best = { google_maps: 'Google Maps', hipages: 'HiPages', abr: 'ABR', diy_website: 'DIY Websites' }[sorted[0].source] || sorted[0].source;
    html += `<li>${best} converting ${sorted[0].reply_rate}% - consider increasing its allocation</li>`;
  }
}
if (bounced > sent * 0.05) {
  html += `<li>Bounce rate above 5% - check email verification quality</li>`;
}
html += `<li>Review trade lingo in emails if any feel unnatural</li>`;
html += `</ul>`;

html += `</div>`;

return [{
  json: {
    subject: `Lead Digest - ${d.date} - ${total} leads from ${sources.length} sources`,
    html: html,
    to: 'aaron@myceliumai.com.au',
  }
}];"""

# ═══════════════════════════════════════════════════════════════
# STEP 2: ADD/UPDATE NODES
# ═══════════════════════════════════════════════════════════════

print('\nStep 2: Adding new nodes...')

existing_names = {n['name'] for n in wf['nodes']}

# Positions based on current layout
# Region Picker is at [-352, -176]
# Apify: Google Maps is at [-176, -176]

# Source Allocator goes between Region Picker and Apify
new_nodes = []

if 'Source Allocator' not in existing_names:
    new_nodes.append({
        'name': 'Source Allocator',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [-264, -176],
        'parameters': {
            'mode': 'runOnceForAllItems',
            'jsCode': SOURCE_ALLOCATOR_CODE,
        },
    })
    print('  + Source Allocator')

if 'Fetch HiPages + ABR' not in existing_names:
    new_nodes.append({
        'name': 'Fetch HiPages + ABR',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [-176, -400],
        'parameters': {
            'mode': 'runOnceForAllItems',
            'jsCode': FETCH_HIPAGES_ABR_CODE,
        },
    })
    print('  + Fetch HiPages + ABR')

if 'Filter Multi-Source' not in existing_names:
    new_nodes.append({
        'name': 'Filter Multi-Source',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [16, -400],
        'parameters': {
            'mode': 'runOnceForEachItem',
            'jsCode': FILTER_MULTI_SOURCE_CODE,
        },
    })
    print('  + Filter Multi-Source')

# Merge Pipeline A: combines Google Maps leads (from Website Checker) + HiPages+ABR leads
if 'Merge Pipeline A' not in existing_names:
    new_nodes.append({
        'name': 'Merge Pipeline A',
        'type': 'n8n-nodes-base.merge',
        'typeVersion': 3,
        'position': [336, -280],
        'parameters': {
            'mode': 'append',
        },
    })
    print('  + Merge Pipeline A')

# Apify: Google Maps (Has Website) — feeds Pipeline B
if 'Apify: Google Maps (Has Website)' not in existing_names:
    new_nodes.append({
        'name': 'Apify: Google Maps (Has Website)',
        'type': 'n8n-nodes-base.httpRequest',
        'typeVersion': 4.2,
        'position': [-176, 144],
        'parameters': {
            'method': 'POST',
            'url': f'https://api.apify.com/v2/acts/compass~crawler-google-places/run-sync-get-dataset-items?token={APIFY_TOKEN}',
            'sendBody': True,
            'specifyBody': 'json',
            'jsonBody': '={{ JSON.stringify({ searchStringsArray: ["plumber " + $json._region_name, "electrician " + $json._region_name, "builder " + $json._region_name, "landscaper " + $json._region_name, "painter " + $json._region_name], maxCrawledPlacesPerSearch: Math.round(($json._source_config?.gmaps_has_website_max || 30) / 5), language: "en", countryCode: "au" }) }}',
            'options': {
                'timeout': 300000,
            },
        },
    })
    print('  + Apify: Google Maps (Has Website)')

# Sticky note for multi-source section
if 'Sticky Note7' not in existing_names:
    new_nodes.append({
        'name': 'Sticky Note7',
        'type': 'n8n-nodes-base.stickyNote',
        'typeVersion': 1,
        'position': [-270, -500],
        'parameters': {
            'content': '## Multi-Source Pipeline\nSource Allocator → 4 sources in parallel:\n- Google Maps (no website) 30%\n- HiPages + ABR combined 40%\n- Google Maps (has website) 30% → Pipeline B',
            'width': 500,
            'height': 150,
        },
    })

wf['nodes'].extend(new_nodes)

# ═══════════════════════════════════════════════════════════════
# STEP 3: UPDATE EXISTING NODES
# ═══════════════════════════════════════════════════════════════

print('\nStep 3: Updating existing nodes...')

for node in wf['nodes']:
    # Update Apify: Google Maps (No Website) to use dynamic maxItems from Source Allocator
    if node['name'] == 'Apify: Google Maps (No Website)':
        params = node['parameters']
        # Update the jsonBody to use Source Allocator's maxItems
        if '_source_config' not in str(params.get('jsonBody', '')):
            params['jsonBody'] = '={{ JSON.stringify({ searchStringsArray: $json._region_name ? ["plumber " + $json._region_name, "electrician " + $json._region_name, "builder " + $json._region_name, "landscaper " + $json._region_name, "painter " + $json._region_name, "roofer " + $json._region_name, "concreter " + $json._region_name, "cleaner " + $json._region_name, "landscaper " + $json._region_name, "fencer " + $json._region_name] : ["plumber Perth WA"], maxCrawledPlacesPerSearch: Math.round(($json._source_config?.gmaps_no_website_max || 30) / 10), language: "en", countryCode: "au" }) }}'
            print('  Updated Apify Google Maps (No Website) with dynamic maxItems')

    # Update Query Today's Data with comprehensive queries
    elif node['name'] == "Query Today's Data":
        node['parameters']['jsCode'] = QUERY_TODAYS_DATA_CODE
        print("  Updated Query Today's Data")

    # Update Build HTML Digest with full command centre
    elif node['name'] == 'Build HTML Digest':
        node['parameters']['jsCode'] = BUILD_DIGEST_CODE
        print('  Updated Build HTML Digest')

# Shift Apify node position right to make room for Source Allocator
for node in wf['nodes']:
    if node['name'] == 'Apify: Google Maps (No Website)':
        node['position'] = [-80, -176]

# ═══════════════════════════════════════════════════════════════
# STEP 4: REWIRE CONNECTIONS
# ═══════════════════════════════════════════════════════════════

print('\nStep 4: Rewiring connections...')
conns = wf['connections']

# Region Picker → Source Allocator (instead of directly to Apify)
conns['Region Picker'] = {
    'main': [[{'node': 'Source Allocator', 'type': 'main', 'index': 0}]]
}

# Source Allocator → 3 parallel outputs (Google Maps No Website, HiPages+ABR, Google Maps Has Website)
conns['Source Allocator'] = {
    'main': [[
        {'node': 'Apify: Google Maps (No Website)', 'type': 'main', 'index': 0},
        {'node': 'Fetch HiPages + ABR', 'type': 'main', 'index': 0},
        {'node': 'Apify: Google Maps (Has Website)', 'type': 'main', 'index': 0},
    ]]
}

# HiPages+ABR → Filter Multi-Source
conns['Fetch HiPages + ABR'] = {
    'main': [[{'node': 'Filter Multi-Source', 'type': 'main', 'index': 0}]]
}

# Google Maps (No Website) path stays the same until Website Checker
# Website Checker → Merge Pipeline A (input 1)
conns['Website Checker'] = {
    'main': [[{'node': 'Merge Pipeline A', 'type': 'main', 'index': 0}]]
}

# Filter Multi-Source → Merge Pipeline A (input 2)
conns['Filter Multi-Source'] = {
    'main': [[{'node': 'Merge Pipeline A', 'type': 'main', 'index': 1}]]
}

# Merge Pipeline A → Lead Scorer A
conns['Merge Pipeline A'] = {
    'main': [[{'node': 'Lead Scorer A', 'type': 'main', 'index': 0}]]
}

# Pipeline B: Google Maps (Has Website) → Filter & Normalise (Has Website)
conns['Apify: Google Maps (Has Website)'] = {
    'main': [[{'node': 'Filter & Normalise (Has Website)', 'type': 'main', 'index': 0}]]
}

# Remove the orphaned Daily 6am AWST1 → Filter (Has Website) connection
# by overriding it (Pipeline B now fed by Source Allocator via Apify Has Website)
if 'Daily 6am AWST1' in conns:
    del conns['Daily 6am AWST1']

print('  Connections rewired')

# ═══════════════════════════════════════════════════════════════
# STEP 5: PUSH WORKFLOW
# ═══════════════════════════════════════════════════════════════

print('\nStep 5: Pushing workflow...')

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
    print(f'  Workflow updated ({len(result.get("nodes", []))} nodes)')
except urllib.error.HTTPError as e:
    print(f'  Error {e.code}: {e.read().decode()[:500]}')
    sys.exit(1)

print('\n=== MULTI-SOURCE PIPELINE DEPLOYED ===')
print('New architecture:')
print('  Region Picker -> Source Allocator -> 3 parallel branches:')
print('    1. Apify Google Maps (no website) -> Filter -> Checker -> Merge -> Scorer A -> Pipeline A')
print('    2. HiPages + ABR (combined fetch) -> Filter -> Merge -> Scorer A -> Pipeline A')
print('    3. Apify Google Maps (has website) -> Pipeline B chain')
print('  Daily digest upgraded with source splits, call numbers, reply analytics')
print('\nNext: Create Pipeline Leads tab in Google Sheet, then test')
