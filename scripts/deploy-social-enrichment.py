"""Deploy social media enrichment to n8n workflow.

Adds 3 nodes between Tag & Pass and Build Prompt:
1. Find Social Profile (Code) — extracts Facebook URL from lead data or tries URL patterns
2. Scrape Facebook Posts (HTTP Request) — calls Apify to get recent posts
3. Parse Social Data (Code) — picks best post, merges with lead data

Also updates Build Prompt A/B with social context and new 'social_activity' variant.
"""
import json, urllib.request, sys, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

N8N_API_KEY = os.environ['N8N_API_KEY']
N8N_API_URL = os.environ['N8N_API_URL']
APIFY_TOKEN = os.environ['APIFY_API_TOKEN']
WF_ID = '3qqw96oRGpyqxt57'

req = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': N8N_API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())

# ═══════════════════════════════════════════════════════════════
# FIND SOCIAL PROFILE — per-item, extracts or discovers Facebook URL
# ═══════════════════════════════════════════════════════════════

FIND_SOCIAL_CODE = r"""// Find Social Profile — extracts Facebook URL from lead data
// or tries common URL patterns. Per-item mode, fast.

const lead = $input.item.json;

// 1. Already has a Facebook URL from Google Maps
if (lead.website_is_facebook && lead.website) {
  const fbUrl = lead.website.startsWith('http') ? lead.website : 'https://' + lead.website;
  return { json: { ...lead, facebook_url: fbUrl, _has_social: true } };
}

// 2. Check if there's a Facebook link in any field
const allText = JSON.stringify(lead).toLowerCase();
const fbMatch = allText.match(/(?:https?:\/\/)?(?:www\.)?facebook\.com\/[a-zA-Z0-9._-]+/);
if (fbMatch) {
  const url = fbMatch[0].startsWith('http') ? fbMatch[0] : 'https://' + fbMatch[0];
  return { json: { ...lead, facebook_url: url, _has_social: true } };
}

// 3. Try to guess Facebook URL from business name
const slug = (lead.business_name || '')
  .toLowerCase()
  .replace(/[''`]/g, '')
  .replace(/&/g, 'and')
  .replace(/\bpty\b|\bltd\b/g, '')
  .replace(/[^a-z0-9]+/g, '')
  .trim();

if (slug && slug.length >= 3) {
  // Try common Facebook URL patterns
  const candidates = [
    `https://www.facebook.com/${slug}`,
    `https://www.facebook.com/${slug}au`,
  ];

  for (const url of candidates) {
    try {
      const resp = await fetch(url, {
        method: 'HEAD',
        redirect: 'follow',
        signal: AbortSignal.timeout(5000),
        headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' },
      });
      // Facebook returns 200 for real pages, 404 for non-existent
      if (resp.ok && !resp.url.includes('/login')) {
        return { json: { ...lead, facebook_url: url, _has_social: true } };
      }
    } catch { continue; }
  }
}

// No social profile found — pass through with flag
return { json: { ...lead, facebook_url: null, _has_social: false } };"""

# ═══════════════════════════════════════════════════════════════
# PARSE SOCIAL DATA — extracts best post from Apify response
# ═══════════════════════════════════════════════════════════════

PARSE_SOCIAL_CODE = r"""// Parse Social Data — picks the most interesting recent post
// Reads lead data from Find Social Profile, response from Apify scraper

const lead = $('Find Social Profile').item.json;
const response = $input.item.json;

// If Apify returned error or empty, pass through without social data
if (!response || response.error || !Array.isArray(response)) {
  // Check if response itself is an array (Apify returns array of posts)
  // or if it's wrapped in a property
  let posts = [];
  if (Array.isArray(response)) {
    posts = response;
  } else if (response.posts) {
    posts = response.posts;
  } else if (response.data) {
    posts = Array.isArray(response.data) ? response.data : [];
  }

  if (posts.length === 0) {
    return { json: { ...lead, social_best_post: null, social_post_date: null, social_post_engagement: null, social_about: null } };
  }
}

// Handle various Apify response formats
let posts = [];
if (Array.isArray(response)) {
  posts = response;
} else if (response.posts) {
  posts = response.posts;
} else if (response.data) {
  posts = Array.isArray(response.data) ? response.data : [];
} else {
  // Single post object
  posts = [response];
}

// Filter: only posts with actual text content (not just images or ads)
const validPosts = posts.filter(p => {
  const text = (p.text || p.message || p.postText || '').trim();
  if (!text || text.length < 20) return false;

  // Skip generic advertising posts
  const lower = text.toLowerCase();
  const isGenericAd = /^(call us|contact us|book now|visit our|check out our|follow us|like our page|share this)/i.test(text);
  const isBoilerplate = lower.includes('terms and conditions') || lower.includes('privacy policy');
  if (isGenericAd || isBoilerplate) return false;

  return true;
});

if (validPosts.length === 0) {
  return { json: { ...lead, social_best_post: null, social_post_date: null, social_post_engagement: null, social_about: null } };
}

// Sort by engagement (likes + comments + shares), pick the best
const scored = validPosts.map(p => ({
  text: (p.text || p.message || p.postText || '').substring(0, 250),
  date: p.time || p.date || p.publishedAt || p.timestamp || '',
  engagement: (p.likes || p.likesCount || 0) + (p.comments || p.commentsCount || 0) + (p.shares || p.sharesCount || 0),
  type: p.type || 'post',
}));

scored.sort((a, b) => b.engagement - a.engagement);
const best = scored[0];

// Extract About section if available
const aboutText = posts[0]?.pageInfo?.about || posts[0]?.about || null;

return {
  json: {
    ...lead,
    social_best_post: best.text,
    social_post_date: best.date ? String(best.date).substring(0, 10) : null,
    social_post_engagement: best.engagement,
    social_about: aboutText ? String(aboutText).substring(0, 200) : null,
    social_scraped_at: new Date().toISOString(),
  }
};"""

# ═══════════════════════════════════════════════════════════════
# GET POSITIONS AND UPDATE WORKFLOW
# ═══════════════════════════════════════════════════════════════

positions = {}
for node in wf['nodes']:
    positions[node['name']] = node.get('position', [0, 0])

tag_a_pos = positions.get('Tag & Pass All Leads', [704, -176])
build_a_pos = positions.get('Build Email Prompt A', [954, -176])

# Add social nodes for Pipeline A
wf['nodes'].extend([
    {
        'name': 'Find Social Profile',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [tag_a_pos[0] + 180, tag_a_pos[1]],
        'parameters': {
            'mode': 'runOnceForEachItem',
            'jsCode': FIND_SOCIAL_CODE,
        },
    },
    {
        'name': 'Scrape Facebook Posts',
        'type': 'n8n-nodes-base.httpRequest',
        'typeVersion': 4.2,
        'position': [tag_a_pos[0] + 360, tag_a_pos[1]],
        'onError': 'continueRegularOutput',
        'parameters': {
            'method': 'POST',
            'url': f'https://api.apify.com/v2/acts/apify~facebook-posts-scraper/run-sync-get-dataset-items?token={APIFY_TOKEN}',
            'sendBody': True,
            'specifyBody': 'json',
            'jsonBody': '={{ JSON.stringify({ startUrls: [{ url: $json.facebook_url || "" }], resultsLimit: 5 }) }}',
            'options': {
                'timeout': 60000,
            },
        },
    },
    {
        'name': 'Parse Social Data',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [tag_a_pos[0] + 540, tag_a_pos[1]],
        'parameters': {
            'mode': 'runOnceForEachItem',
            'jsCode': PARSE_SOCIAL_CODE,
        },
    },
])

# ═══════════════════════════════════════════════════════════════
# UPDATE BUILD PROMPT A — add social context + variant
# ═══════════════════════════════════════════════════════════════

for node in wf['nodes']:
    if node['name'] == 'Build Email Prompt A':
        code = node['parameters']['jsCode']

        # Add social_activity variant
        old_variants_end = "  { name: 'free_offer_upfront'"
        new_variant = """  { name: 'social_activity', instruction: 'Reference their most recent Facebook post naturally. Mention what the post was about as if you came across it. Don\\'t say \"I saw on your Facebook\" - just reference the content like you know about it. Example: \"saw you just did that kitchen reno in Applecross, looked mint\". If no social data available, fall back to reviewer name-dropping.' },
  { name: 'free_offer_upfront'"""
        if old_variants_end in code:
            code = code.replace(old_variants_end, new_variant)

        # Add social fields to lead context
        old_score_line = "parts.push(`Score: ${lead.score}/10`);"
        social_context = """// Social media context (if available)
if (lead.social_best_post) {
  parts.push(`Recent Facebook post: "${lead.social_best_post}"`);
  if (lead.social_post_date) parts.push(`Post date: ${lead.social_post_date}`);
  if (lead.social_post_engagement) parts.push(`Post engagement: ${lead.social_post_engagement} likes/comments`);
}
if (lead.social_about) {
  parts.push(`Facebook About: "${lead.social_about}"`);
}
parts.push(`Score: ${lead.score}/10`);"""
        if old_score_line in code:
            code = code.replace(old_score_line, social_context)

        node['parameters']['jsCode'] = code

    # Same for Pipeline B
    elif node['name'] == 'Build Email Prompt B':
        code = node['parameters']['jsCode']

        old_score_line = "parts.push(`Score: ${lead.score}/10`);"
        social_context = """if (lead.social_best_post) {
  parts.push(`Recent Facebook post: "${lead.social_best_post}"`);
  if (lead.social_post_date) parts.push(`Post date: ${lead.social_post_date}`);
}
parts.push(`Score: ${lead.score}/10`);"""
        if old_score_line in code:
            code = code.replace(old_score_line, social_context)

        node['parameters']['jsCode'] = code

    # Update Supabase Store with social fields
    elif node['name'] == 'Supabase: Store Leads':
        code = node['parameters']['jsCode']
        if 'facebook_url' not in code:
            code = code.replace(
                "  region: lead.region || lead._region_name || null,",
                """  region: lead.region || lead._region_name || null,
  facebook_url: lead.facebook_url || null,
  instagram_url: lead.instagram_url || null,
  social_best_post: lead.social_best_post || null,
  social_post_date: lead.social_post_date || null,
  social_post_engagement: lead.social_post_engagement || null,
  social_about: lead.social_about || null,
  social_scraped_at: lead.social_scraped_at || null,"""
            )
            node['parameters']['jsCode'] = code

# ═══════════════════════════════════════════════════════════════
# REWIRE CONNECTIONS — insert social nodes between Tag and Build Prompt
# ═══════════════════════════════════════════════════════════════

conns = wf['connections']

# Pipeline A: Tag -> Find Social -> Scrape FB -> Parse Social -> Build Prompt A
conns['Tag & Pass All Leads'] = {
    'main': [[{'node': 'Find Social Profile', 'type': 'main', 'index': 0}]]
}
conns['Find Social Profile'] = {
    'main': [[{'node': 'Scrape Facebook Posts', 'type': 'main', 'index': 0}]]
}
conns['Scrape Facebook Posts'] = {
    'main': [[{'node': 'Parse Social Data', 'type': 'main', 'index': 0}]]
}
conns['Parse Social Data'] = {
    'main': [[{'node': 'Build Email Prompt A', 'type': 'main', 'index': 0}]]
}

# ═══════════════════════════════════════════════════════════════
# PUSH
# ═══════════════════════════════════════════════════════════════

print('Social enrichment changes:')
print('  - Find Social Profile (new Code node)')
print('  - Scrape Facebook Posts (new HTTP Request node)')
print('  - Parse Social Data (new Code node)')
print('  - Build Prompt A: social_activity variant + social context fields')
print('  - Build Prompt B: social context fields')
print('  - Supabase Store: social fields added')
print('  - Connections: Tag -> Social -> Build Prompt')

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
    print(f'\nWorkflow updated ({len(result.get("nodes", []))} nodes)')
except urllib.error.HTTPError as e:
    print(f'Error {e.code}: {e.read().decode()[:500]}')
    sys.exit(1)
