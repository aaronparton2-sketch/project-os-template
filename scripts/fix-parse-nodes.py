"""Fix Parse Email nodes + HTTP Request node options.

Problems:
1. fullResponse wraps OpenAI response in {statusCode, headers, body}
2. HTTP Request replaces input data — lead fields are lost
3. Parse node can't find business_name, phone, etc.

Fix:
1. Remove fullResponse from HTTP Request nodes
2. Add continueOnFail so errors don't kill pipeline
3. Parse nodes use $('Build Email Prompt A/B').item.json for lead data
4. Parse nodes use $input.item.json for OpenAI response
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

# ── Parse Email A — references Build Email Prompt A for lead data ──
PARSE_A_CODE = r"""// Parse OpenAI Response — Pipeline A
// Lead data: from Build Email Prompt A (HTTP Request replaced it with response)
// OpenAI response: from $input.item.json (direct API response)

const lead = $('Build Email Prompt A').item.json;
const response = $input.item.json;

let emailData = { subject: '', body: '', call_script: '' };

try {
  const content = response.choices?.[0]?.message?.content || '{}';
  const cleaned = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
  emailData = JSON.parse(cleaned);
} catch {
  const raw = response.choices?.[0]?.message?.content || '';
  emailData = { subject: '[PARSE ERROR]', body: raw, call_script: '' };
}

// Build "why this lead" summary
const whyParts = [];
if (lead.google_reviews >= 20) whyParts.push(`${lead.google_reviews} reviews`);
else if (lead.google_reviews >= 5) whyParts.push(`${lead.google_reviews} reviews`);
if (lead.website_is_facebook) whyParts.push('FB only');
if (lead.address_type === 'residential') whyParts.push('home-based');
if (lead.hipages_jobs >= 10) whyParts.push(`${lead.hipages_jobs} HiPages jobs`);
if (lead.registration_date) whyParts.push('new registration');
const whySummary = whyParts.length > 0 ? whyParts.join(', ') : 'standard lead';

return {
  json: {
    business_name: lead.business_name || '',
    phone: lead.phone || '',
    suburb: lead.suburb || '',
    category: lead.category || '',
    score: lead.score,
    why: `${lead.score}/10 — ${whySummary}`,
    tier: lead.outreach_tier || (lead.score >= 7 ? 'priority_call' : 'email_only'),
    draft_subject: emailData.subject || '',
    draft_email: emailData.body || '',
    call_script: emailData.call_script || '',
    email: lead.email || '',
    email_variant: lead._variant_name || '',
    pipeline: lead.pipeline || 'no_website',
    address_type: lead.address_type || '',
    google_reviews: lead.google_reviews,
    google_rating: lead.google_rating,
    website: lead.website || '',
    website_verified: lead.website_verified,
    website_check_method: lead.website_check_method,
    postcode: lead.postcode || '',
    address: lead.address || '',
    source: lead.source || '',
    score_breakdown: lead.score_breakdown,
    top_review_quote: lead.top_review_quote,
    found_on_sources: lead.found_on_sources,
    place_id: lead.place_id,
    abn: lead.abn,
  }
};"""

# ── Parse Email B — references Build Email Prompt B for lead data ──
PARSE_B_CODE = r"""// Parse OpenAI Response — Pipeline B
// Lead data: from Build Email Prompt B (HTTP Request replaced it with response)
// OpenAI response: from $input.item.json (direct API response)

const lead = $('Build Email Prompt B').item.json;
const response = $input.item.json;

let emailData = { subject: '', body: '', call_script: '' };

try {
  const content = response.choices?.[0]?.message?.content || '{}';
  const cleaned = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
  emailData = JSON.parse(cleaned);
} catch {
  const raw = response.choices?.[0]?.message?.content || '';
  emailData = { subject: '[PARSE ERROR]', body: raw, call_script: '' };
}

const whyParts = [];
if (lead.pagespeed_score != null && lead.pagespeed_score < 50) whyParts.push(`speed ${lead.pagespeed_score}/100`);
if (lead.diy_platform) whyParts.push(lead.diy_platform);
if (lead.google_reviews >= 20) whyParts.push(`${lead.google_reviews} reviews`);
if (lead.running_google_ads) whyParts.push('running ads');
if (lead.address_type === 'residential') whyParts.push('home-based');
if (lead.has_ssl === false) whyParts.push('no SSL');
if (lead.mobile_friendly === false) whyParts.push('not mobile-friendly');
const whySummary = whyParts.length > 0 ? whyParts.join(', ') : 'standard lead';

return {
  json: {
    business_name: lead.business_name || '',
    phone: lead.phone || '',
    suburb: lead.suburb || '',
    category: lead.category || '',
    score: lead.score,
    why: `${lead.score}/10 — ${whySummary}`,
    tier: lead.outreach_tier || (lead.score >= 7 ? 'priority_call' : 'email_only'),
    draft_subject: emailData.subject || '',
    draft_email: emailData.body || '',
    call_script: emailData.call_script || '',
    email: lead.email || '',
    email_variant: lead._variant_name || '',
    pipeline: lead.pipeline || 'diy_website',
    address_type: lead.address_type || '',
    google_reviews: lead.google_reviews,
    google_rating: lead.google_rating,
    website: lead.website || '',
    diy_platform: lead.diy_platform || '',
    pagespeed_score: lead.pagespeed_score,
    pagespeed_mobile: lead.pagespeed_mobile,
    has_ssl: lead.has_ssl,
    mobile_friendly: lead.mobile_friendly,
    running_google_ads: lead.running_google_ads,
    website_verified: lead.website_verified,
    postcode: lead.postcode || '',
    address: lead.address || '',
    source: lead.source || '',
    score_breakdown: lead.score_breakdown,
    place_id: lead.place_id,
    abn: lead.abn,
  }
};"""

fixes = []
for node in wf['nodes']:
    name = node['name']

    # Fix HTTP Request nodes — remove fullResponse, add continueOnFail
    if name in ('OpenAI: Draft Email A', 'OpenAI: Draft Email B'):
        node['parameters']['options'] = {'timeout': 30000}  # remove fullResponse
        node['onError'] = 'continueRegularOutput'  # don't kill pipeline on error
        fixes.append(f'{name} (removed fullResponse, added continueOnFail)')

    # Fix Parse nodes — use cross-node reference for lead data
    elif name == 'Parse Email A':
        node['parameters']['jsCode'] = PARSE_A_CODE
        fixes.append(name)

    elif name == 'Parse Email B':
        node['parameters']['jsCode'] = PARSE_B_CODE
        fixes.append(name)

for f in fixes:
    print(f'  Fixed: {f}')

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
