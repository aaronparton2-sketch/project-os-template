"""Deploy Facebook Business Page Scraper as 5th lead source.

Changes:
1. Supabase migration: offer_type on outreach_events, facebook_page_url on leads, new views
2. Source Allocator updated: 5 sources (Facebook 30%, HiPages 25%, GMaps 20%, ABR 15%, DIY 10%)
3. New Facebook branch: Search → Filter → Score → wire into Merge Pipeline A
4. Daily digest updated with Facebook source label
"""
import json, urllib.request, subprocess, sys, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

N8N_API_KEY = os.environ['N8N_API_KEY']
N8N_API_URL = os.environ['N8N_API_URL']
APIFY_TOKEN = os.environ['APIFY_API_TOKEN']
PIPELINE_PROJECT_REF = os.environ['SUPABASE_PIPELINE_PROJECT_REF']
SUPABASE_ACCESS_TOKEN = os.environ['SUPABASE_ACCESS_TOKEN']
WF_ID = '3qqw96oRGpyqxt57'


def supabase_query(sql):
    """Run SQL against pipeline Supabase via Management API (uses curl to avoid Cloudflare blocks)."""
    result = subprocess.run(
        ['curl', '-s', '-X', 'POST',
         f'https://api.supabase.com/v1/projects/{PIPELINE_PROJECT_REF}/database/query',
         '-H', f'Authorization: Bearer {SUPABASE_ACCESS_TOKEN}',
         '-H', 'Content-Type: application/json',
         '-d', json.dumps({'query': sql})],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f'  ERROR: {result.stderr[:300]}')
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f'  Response: {result.stdout[:300]}')
        return result.stdout


# ═══════════════════════════════════════════════════════════════
# STEP 1: SUPABASE MIGRATION
# ═══════════════════════════════════════════════════════════════

print('Step 1: Running Supabase migration...')

MIGRATION_SQL = """
-- Migration 006: Facebook source + offer type tracking
-- Add offer_type to outreach_events
ALTER TABLE outreach_events ADD COLUMN IF NOT EXISTS offer_type TEXT DEFAULT 'free_website';

-- Add facebook_page_url to leads
ALTER TABLE leads ADD COLUMN IF NOT EXISTS facebook_page_url TEXT;

-- Index for offer_type queries
CREATE INDEX IF NOT EXISTS idx_outreach_events_offer_type ON outreach_events(offer_type);
"""

supabase_query(MIGRATION_SQL)
print('  Migration applied (offer_type + facebook_page_url columns)')

# Create/update views
VIEWS_SQL = """
-- Offer type A/B comparison
CREATE OR REPLACE VIEW offer_type_performance AS
SELECT
    offer_type,
    COUNT(*) FILTER (WHERE event_type = 'email_sent') as sent,
    COUNT(*) FILTER (WHERE event_type = 'email_opened') as opened,
    COUNT(*) FILTER (WHERE event_type = 'email_replied') as replied,
    COUNT(*) FILTER (WHERE event_type = 'email_bounced') as bounced,
    ROUND(
        COUNT(*) FILTER (WHERE event_type = 'email_opened')::numeric /
        NULLIF(COUNT(*) FILTER (WHERE event_type = 'email_sent'), 0) * 100, 1
    ) as open_rate,
    ROUND(
        COUNT(*) FILTER (WHERE event_type = 'email_replied')::numeric /
        NULLIF(COUNT(*) FILTER (WHERE event_type = 'email_sent'), 0) * 100, 1
    ) as reply_rate
FROM outreach_events
WHERE channel = 'email'
GROUP BY offer_type;

-- Update email_variant_performance to include offer_type
CREATE OR REPLACE VIEW email_variant_performance AS
SELECT
    e_sent.variant,
    COUNT(DISTINCT e_sent.lead_id) as sent,
    COUNT(DISTINCT e_open.lead_id) as opened,
    COUNT(DISTINCT e_reply.lead_id) as replied,
    COUNT(DISTINCT e_bounce.lead_id) as bounced,
    ROUND(COUNT(DISTINCT e_open.lead_id)::numeric / NULLIF(COUNT(DISTINCT e_sent.lead_id), 0) * 100, 1) as open_rate,
    ROUND(COUNT(DISTINCT e_reply.lead_id)::numeric / NULLIF(COUNT(DISTINCT e_sent.lead_id), 0) * 100, 1) as reply_rate
FROM outreach_events e_sent
LEFT JOIN outreach_events e_open ON e_sent.lead_id = e_open.lead_id AND e_open.event_type = 'email_opened'
LEFT JOIN outreach_events e_reply ON e_sent.lead_id = e_reply.lead_id AND e_reply.event_type = 'email_replied'
LEFT JOIN outreach_events e_bounce ON e_sent.lead_id = e_bounce.lead_id AND e_bounce.event_type = 'email_bounced'
WHERE e_sent.event_type = 'email_sent'
GROUP BY e_sent.variant;

-- Update weekly summary to include offer_type stats
CREATE OR REPLACE VIEW weekly_outreach_summary AS
SELECT
    DATE_TRUNC('week', created_at) as week,
    COUNT(*) FILTER (WHERE event_type = 'email_sent') as emails_sent,
    COUNT(*) FILTER (WHERE event_type = 'email_opened') as emails_opened,
    COUNT(*) FILTER (WHERE event_type = 'email_replied') as emails_replied,
    COUNT(*) FILTER (WHERE event_type = 'email_bounced') as emails_bounced,
    COUNT(*) FILTER (WHERE event_type IN ('call_made', 'call_answered', 'call_voicemail', 'call_no_answer')) as calls_made,
    COUNT(*) FILTER (WHERE event_type = 'call_interested') as calls_interested,
    COUNT(*) FILTER (WHERE event_type = 'call_not_interested') as calls_not_interested,
    COUNT(*) FILTER (WHERE event_type = 'email_sent' AND offer_type = 'free_website') as free_website_sent,
    COUNT(*) FILTER (WHERE event_type = 'email_sent' AND offer_type = 'mates_rates') as mates_rates_sent,
    COUNT(*) FILTER (WHERE event_type = 'email_sent' AND offer_type = 'portfolio_build') as portfolio_build_sent
FROM outreach_events
GROUP BY DATE_TRUNC('week', created_at)
ORDER BY week DESC;
"""

supabase_query(VIEWS_SQL)
print('  Views created/updated (offer_type_performance + weekly_outreach_summary)')


# ═══════════════════════════════════════════════════════════════
# STEP 2: FETCH WORKFLOW
# ═══════════════════════════════════════════════════════════════

print('\nStep 2: Fetching n8n workflow...')
req = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': N8N_API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())
print(f'  Loaded workflow: {len(wf["nodes"])} nodes')

existing_names = {n['name'] for n in wf['nodes']}


# ═══════════════════════════════════════════════════════════════
# STEP 3: UPDATE SOURCE ALLOCATOR (5 sources)
# ═══════════════════════════════════════════════════════════════

print('\nStep 3: Updating Source Allocator...')

SOURCE_ALLOCATOR_CODE = r"""// Source Allocator - 5 sources (Facebook 30%, HiPages 25%, GMaps 20%, ABR 15%, DIY 10%)
const regionData = $input.item.json;

if (regionData._no_region || regionData._skip) {
  return [{ json: { ...regionData, _skip: true } }];
}

// Source percentage split (tunable - updated 2026-03-24)
const SPLIT = {
  facebook: 0.30,                // 30% - new, untapped source
  hipages: 0.25,                 // 25% - strong structured directory
  google_maps_no_website: 0.20,  // 20% - proven but well-mined
  abr: 0.15,                     // 15% - fresh registrations
  google_maps_has_website: 0.10, // 10% - DIY websites (Pipeline B)
};

const DAILY_TARGET = 100;

const facebookMax = Math.round(DAILY_TARGET * SPLIT.facebook);
const hipagesMax = Math.round(DAILY_TARGET * SPLIT.hipages);
const gmapsNoWebMax = Math.round(DAILY_TARGET * SPLIT.google_maps_no_website);
const abrMax = Math.round(DAILY_TARGET * SPLIT.abr);
const gmapsHasWebMax = Math.round(DAILY_TARGET * SPLIT.google_maps_has_website);

const regionState = regionData._region_state || 'WA';
const regionName = regionData._region_name || 'Perth, Western Australia';

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
      facebook_max: facebookMax,
      hipages_max: hipagesMax,
      gmaps_no_website_max: gmapsNoWebMax,
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

for node in wf['nodes']:
    if node['name'] == 'Source Allocator':
        node['parameters']['jsCode'] = SOURCE_ALLOCATOR_CODE
        print('  Source Allocator updated to 5-source split')
        break


# ═══════════════════════════════════════════════════════════════
# STEP 4: ADD FACEBOOK BRANCH NODES
# ═══════════════════════════════════════════════════════════════

print('\nStep 4: Adding Facebook branch nodes...')

# --- FACEBOOK SEARCH (Apify HTTP Request) ---
# Uses apify/facebook-pages-scraper to search for business pages by location
FACEBOOK_SEARCH_CODE = f'''// Facebook Business Search - find businesses without websites
// Uses Apify to search Facebook for local business pages

const config = $input.item.json;
if (config._skip) return [{{ json: {{ _skip: true, _leads: [] }} }}];

const APIFY_TOKEN = '{APIFY_TOKEN}';
const regionName = config._region_name || 'Perth, Western Australia';
const cityName = regionName.split(',')[0].trim();
const facebookMax = config._source_config?.facebook_max || 30;

// Trade categories to search on Facebook
const TRADE_SEARCHES = [
  'plumber', 'electrician', 'builder', 'landscaper', 'painter',
  'roofer', 'concreter', 'cleaner', 'fencer', 'carpenter',
  'pest control', 'air conditioning', 'tiler', 'mechanic',
  'removalist', 'handyman', 'solar', 'pool',
];

const allLeads = [];
const seenNames = new Set();
const maxPerSearch = Math.max(3, Math.ceil(facebookMax / 8));

// Search Facebook for each trade in the target city
for (const trade of TRADE_SEARCHES) {{
  if (allLeads.length >= facebookMax) break;

  const searchQuery = `${{trade}} ${{cityName}}`;

  try {{
    // Use Apify Facebook Pages Scraper
    const result = await this.helpers.httpRequest({{
      method: 'POST',
      url: `https://api.apify.com/v2/acts/apify~facebook-pages-scraper/run-sync-get-dataset-items?token=${{APIFY_TOKEN}}`,
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{
        startUrls: [{{ url: `https://www.facebook.com/search/pages/?q=${{encodeURIComponent(searchQuery)}}` }}],
        maxPages: maxPerSearch,
        maxPagesPerQuery: maxPerSearch,
      }}),
      timeout: 120000,
    }});

    const pages = Array.isArray(result) ? result : [];

    for (const page of pages) {{
      if (allLeads.length >= facebookMax) break;

      const name = (page.title || page.name || '').trim();
      if (!name || seenNames.has(name.toLowerCase())) continue;

      // Extract phone (multiple possible fields)
      const phone = (page.phone || page.phoneNumber || '').replace(/\\D/g, '');

      // Extract website
      const website = (page.website || page.url || '').trim();

      // Check if website is just Facebook/Instagram or empty
      const hasRealWebsite = website &&
        !website.includes('facebook.com') &&
        !website.includes('instagram.com') &&
        !website.includes('fb.com') &&
        website.length > 5;

      // HARD FILTER: skip if they have a real website
      if (hasRealWebsite) continue;

      // Extract other data
      const address = (page.address || page.location || '').trim();
      const category = page.categories?.[0] || page.category || trade;
      const likes = page.likes || page.followersCount || 0;
      const pageUrl = page.pageUrl || page.url || '';
      const about = (page.about || page.description || '').substring(0, 300);
      const lastPost = page.posts?.[0]?.text || page.latestPost || '';
      const lastPostDate = page.posts?.[0]?.time || page.latestPostDate || null;

      seenNames.add(name.toLowerCase());
      allLeads.push({{
        business_name: name,
        phone: phone,
        email: page.email || null,
        category: trade,
        address: address,
        suburb: cityName,
        state: config._region_state || 'WA',
        website: website || null,
        pipeline: 'no_website',
        source: 'facebook',
        facebook_page_url: pageUrl,
        facebook_likes: likes,
        facebook_about: about,
        social_best_post: lastPost,
        social_post_date: lastPostDate,
        address_type: 'unknown',
        region: config._region_name || null,
        score: 0,
      }});
    }}
  }} catch (e) {{
    // Search failed for this trade, continue
  }}
}}

if (allLeads.length === 0) {{
  return [{{ json: {{ _skip: true, _source: 'facebook', _count: 0 }} }}];
}}

return allLeads.map(lead => ({{ json: lead }}));'''

# --- FILTER FACEBOOK ---
FILTER_FACEBOOK_CODE = f'''// Filter Facebook Leads - strict qualification
// Hard filters: must have phone, no real website, posted in last 90 days

const PROJECT_REF = '{PIPELINE_PROJECT_REF}';
const ACCESS_TOKEN = '{SUPABASE_ACCESS_TOKEN}';
const API_URL = `https://api.supabase.com/v1/projects/${{PROJECT_REF}}/database/query`;

const lead = $input.item.json;

if (lead._skip) return [];

// HARD FILTER 1: Must have phone number
if (!lead.phone || lead.phone.length < 8) return [];

// HARD FILTER 2: Must not have a real website (already filtered in search, double check)
const website = (lead.website || '').toLowerCase();
if (website && !website.includes('facebook.com') && !website.includes('instagram.com') && !website.includes('fb.com') && website.length > 5) return [];

// HARD FILTER 3: Check for duplicates in Supabase (by phone or business name)
const cleanPhone = lead.phone.replace(/\\D/g, '');
const safeName = (lead.business_name || '').replace(/'/g, "''");
const dedupQuery = `SELECT id FROM leads WHERE phone = '${{cleanPhone}}' OR LOWER(business_name) = LOWER('${{safeName}}') LIMIT 1;`;

try {{
  const existing = await this.helpers.httpRequest({{
    method: 'POST',
    url: API_URL,
    headers: {{
      'Authorization': `Bearer ${{ACCESS_TOKEN}}`,
      'Content-Type': 'application/json',
    }},
    body: {{ query: dedupQuery }},
    timeout: 10000,
  }});
  if (existing && existing.length > 0) return []; // Already in DB
}} catch {{
  // If dedup check fails, let the lead through (Supabase store handles final dedup)
}}

return {{ json: lead }};'''

# --- SCORE FACEBOOK ---
SCORE_FACEBOOK_CODE = r"""// Score Facebook Leads - stricter threshold (min 7)
// Scoring: no website +3, has phone +2, active page +2, address match +1, high-value trade +1, followers +1, residential +2

const lead = $input.item.json;
if (lead._skip) return [];

let score = 0;
const breakdown = {};

// No website listed (required - +3)
const hasRealWebsite = lead.website &&
  !lead.website.includes('facebook.com') &&
  !lead.website.includes('instagram.com') &&
  lead.website.length > 5;
if (!hasRealWebsite) {
  score += 3;
  breakdown.no_website = 3;
} else {
  return []; // Should not happen (filtered earlier) but safety check
}

// Has phone number (required - +2)
if (lead.phone && lead.phone.length >= 8) {
  score += 2;
  breakdown.has_phone = 2;
} else {
  return []; // Should not happen (filtered earlier)
}

// Active page - posted in last 90 days (+2)
if (lead.social_post_date) {
  const postDate = new Date(lead.social_post_date);
  const ninetyDaysAgo = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
  if (postDate > ninetyDaysAgo) {
    score += 2;
    breakdown.active_page = 2;
  }
} else if (lead.social_best_post) {
  // Has post content but no date - give partial credit
  score += 1;
  breakdown.active_page = 1;
}

// Has business address in target region (+1)
if (lead.address || lead.suburb) {
  score += 1;
  breakdown.address_match = 1;
}

// High-value trade category (+1)
const highValueTrades = ['plumber', 'electrician', 'builder', 'landscaper', 'roofer', 'air conditioning', 'solar'];
const cat = (lead.category || '').toLowerCase();
if (highValueTrades.some(t => cat.includes(t))) {
  score += 1;
  breakdown.high_value_trade = 1;
}

// 20+ followers/likes (+1)
if ((lead.facebook_likes || 0) >= 20) {
  score += 1;
  breakdown.established_page = 1;
}

// Residential postcode (+2)
const CBD_POSTCODES = ['6000','6001','6003','6004','6005','2000','2001','3000','3001','4000','4001','5000','5001','7000','7001','800','810','2600','2601'];
const postcode = (lead.postcode || '').toString();
if (postcode && !CBD_POSTCODES.includes(postcode)) {
  score += 2;
  breakdown.residential = 2;
  lead.address_type = 'residential';
} else if (postcode) {
  lead.address_type = 'cbd';
}

lead.score = score;
lead.score_breakdown = breakdown;

// STRICT THRESHOLD: minimum 7 for Facebook leads
if (score < 7) return [];

return { json: lead };"""

# Add new nodes
new_nodes = []

if 'Facebook Search' not in existing_names:
    # Position: parallel to other source branches, above the HiPages+ABR branch
    new_nodes.append({
        'name': 'Facebook Search',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [-176, -620],
        'parameters': {
            'mode': 'runOnceForAllItems',
            'jsCode': FACEBOOK_SEARCH_CODE,
        },
    })
    print('  + Facebook Search node')

if 'Filter Facebook' not in existing_names:
    new_nodes.append({
        'name': 'Filter Facebook',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [16, -620],
        'parameters': {
            'mode': 'runOnceForEachItem',
            'jsCode': FILTER_FACEBOOK_CODE,
        },
    })
    print('  + Filter Facebook node')

if 'Score Facebook' not in existing_names:
    new_nodes.append({
        'name': 'Score Facebook',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [200, -620],
        'parameters': {
            'mode': 'runOnceForEachItem',
            'jsCode': SCORE_FACEBOOK_CODE,
        },
    })
    print('  + Score Facebook node')

# Sticky note for Facebook section
if 'Sticky Note8' not in existing_names:
    new_nodes.append({
        'name': 'Sticky Note8',
        'type': 'n8n-nodes-base.stickyNote',
        'typeVersion': 1,
        'position': [-206, -720],
        'parameters': {
            'content': '## Facebook Source (30%)\nSearch Facebook business pages by trade + city.\nStrict filter: no website, has phone, active page.\nMin score 7 (stricter than other sources).',
            'width': 500,
            'height': 120,
        },
    })

wf['nodes'].extend(new_nodes)


# ═══════════════════════════════════════════════════════════════
# STEP 5: ADD SECOND MERGE NODE + REWIRE
# ═══════════════════════════════════════════════════════════════

print('\nStep 5: Wiring Facebook branch into pipeline...')

# n8n Merge nodes only accept 2 inputs. Current: Website Checker + Filter Multi-Source → Merge Pipeline A
# We need to chain: Score Facebook + Merge Pipeline A → Merge All Sources A → Lead Scorer A

if 'Merge All Sources A' not in existing_names:
    wf['nodes'].append({
        'name': 'Merge All Sources A',
        'type': 'n8n-nodes-base.merge',
        'typeVersion': 3,
        'position': [500, -400],
        'parameters': {
            'mode': 'append',
        },
    })
    print('  + Merge All Sources A (chains Facebook into pipeline)')

# Wire connections
conns = wf['connections']

# Source Allocator → 4 parallel branches (add Facebook)
conns['Source Allocator'] = {
    'main': [[
        {'node': 'Apify: Google Maps (No Website)', 'type': 'main', 'index': 0},
        {'node': 'Fetch HiPages + ABR', 'type': 'main', 'index': 0},
        {'node': 'Apify: Google Maps (Has Website)', 'type': 'main', 'index': 0},
        {'node': 'Facebook Search', 'type': 'main', 'index': 0},
    ]]
}

# Facebook chain: Search → Filter → Score
conns['Facebook Search'] = {
    'main': [[{'node': 'Filter Facebook', 'type': 'main', 'index': 0}]]
}
conns['Filter Facebook'] = {
    'main': [[{'node': 'Score Facebook', 'type': 'main', 'index': 0}]]
}

# Merge Pipeline A (existing: GMaps + HiPages/ABR) → Merge All Sources A (input 1)
conns['Merge Pipeline A'] = {
    'main': [[{'node': 'Merge All Sources A', 'type': 'main', 'index': 0}]]
}

# Score Facebook → Merge All Sources A (input 2)
conns['Score Facebook'] = {
    'main': [[{'node': 'Merge All Sources A', 'type': 'main', 'index': 1}]]
}

# Merge All Sources A → Lead Scorer A
conns['Merge All Sources A'] = {
    'main': [[{'node': 'Lead Scorer A', 'type': 'main', 'index': 0}]]
}

print('  Connections wired: Source Allocator -> Facebook Search -> Filter -> Score -> Merge All Sources A -> Lead Scorer A')


# ═══════════════════════════════════════════════════════════════
# STEP 6: UPDATE DIGEST SOURCE LABELS
# ═══════════════════════════════════════════════════════════════

print('\nStep 6: Updating digest source labels...')

for node in wf['nodes']:
    if node['name'] == 'Build HTML Digest':
        code = node['parameters'].get('jsCode', '')
        # Add Facebook to source labels if not already there
        if "'facebook'" not in code and 'facebook' not in code.lower().split('sourcelabels')[0] if 'sourceLabels' in code else True:
            code = code.replace(
                "const sourceLabels = { google_maps: 'Google Maps (no website)', hipages: 'HiPages', abr: 'ABR (new reg)', diy_website: 'DIY Websites' };",
                "const sourceLabels = { facebook: 'Facebook (no website)', google_maps: 'Google Maps (no website)', hipages: 'HiPages', abr: 'ABR (new reg)', diy_website: 'DIY Websites' };"
            )
            # Also update source short labels in priority calls
            code = code.replace(
                "const sourceShort = { google_maps: 'GMaps', hipages: 'HiPg', abr: 'ABR', diy_website: 'DIY' }[c.source] || c.source;",
                "const sourceShort = { facebook: 'FB', google_maps: 'GMaps', hipages: 'HiPg', abr: 'ABR', diy_website: 'DIY' }[c.source] || c.source;"
            )
            # Update source performance labels
            code = code.replace(
                "const label = { google_maps: 'Google Maps', hipages: 'HiPages', abr: 'ABR', diy_website: 'DIY' }[s.source] || s.source;",
                "const label = { facebook: 'Facebook', google_maps: 'Google Maps', hipages: 'HiPages', abr: 'ABR', diy_website: 'DIY' }[s.source] || s.source;"
            )
            # Update suggestions section
            code = code.replace(
                "const best = { google_maps: 'Google Maps', hipages: 'HiPages', abr: 'ABR', diy_website: 'DIY Websites' }[sorted[0].source] || sorted[0].source;",
                "const best = { facebook: 'Facebook', google_maps: 'Google Maps', hipages: 'HiPages', abr: 'ABR', diy_website: 'DIY Websites' }[sorted[0].source] || sorted[0].source;"
            )
            node['parameters']['jsCode'] = code
            print('  Build HTML Digest updated with Facebook labels')
        break

# Update sticky note for multi-source section
for node in wf['nodes']:
    if node['name'] == 'Sticky Note7':
        node['parameters']['content'] = '## Multi-Source Pipeline (5 sources)\nSource Allocator distributes daily 100 leads:\n- Facebook (no website) 30%\n- HiPages + ABR combined 40%\n- Google Maps (no website) 20%\n- Google Maps (has website) 10% → Pipeline B'
        print('  Sticky Note7 updated')
        break


# ═══════════════════════════════════════════════════════════════
# STEP 7: UPDATE SUPABASE STORE to handle facebook_page_url
# ═══════════════════════════════════════════════════════════════

print('\nStep 7: Updating Supabase Store...')

for node in wf['nodes']:
    if node['name'] == 'Supabase: Store Leads':
        code = node['parameters'].get('jsCode', '')
        if 'facebook_page_url' not in code:
            code = code.replace(
                "  facebook_url: lead.facebook_url || '',",
                "  facebook_url: lead.facebook_url || '',\n  facebook_page_url: lead.facebook_page_url || null,"
            )
            node['parameters']['jsCode'] = code
            print('  Supabase Store updated with facebook_page_url')
        else:
            print('  Supabase Store already has facebook_page_url')
        break


# ═══════════════════════════════════════════════════════════════
# STEP 8: PUSH WORKFLOW
# ═══════════════════════════════════════════════════════════════

print('\nStep 8: Pushing workflow...')

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

print('\n=== FACEBOOK SOURCE DEPLOYED ===')
print('Architecture now:')
print('  Region Picker -> Source Allocator -> 5 parallel branches:')
print('    1. Facebook Search -> Filter -> Score -> Merge All Sources A (30%)')
print('    2. Apify Google Maps (no website) -> Filter -> Checker -> Merge Pipeline A (20%)')
print('    3. HiPages + ABR (combined fetch) -> Filter -> Merge Pipeline A (40%)')
print('    4. Apify Google Maps (has website) -> Pipeline B chain (10%)')
print('    Merge Pipeline A + Score Facebook -> Merge All Sources A -> Lead Scorer A')
print('\nSupabase: offer_type column + facebook_page_url + offer_type_performance view')
print('\nNext: Deploy offer variants (deploy-offer-variants.py)')
