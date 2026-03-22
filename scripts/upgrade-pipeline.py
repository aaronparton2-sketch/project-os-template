"""Major pipeline upgrade:
1. Add OpenAI node after AI Personaliser to actually generate emails
2. Add Supabase upsert node after Scorer to store leads
3. Wire everything together properly
4. NO email sending — test mode only
"""
import json, urllib.request, sys

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNjE4ODEyNC02YzNiLTQxZDktODdhMS01MDljNmIzOTVkZmMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzcxNjQxODY1fQ.IWzbpXkITsoUvqLLpROW3hQ3PvGo_11D0yLjqRUVaXM'
WF_ID = '3qqw96oRGpyqxt57'
PG_CRED_ID = 'Mg98U6sOpU23VaJe'
OPENAI_CRED_ID = 'DX0ChPZkozXYBGrr'

req = urllib.request.Request(
    f'https://aaronparton2.app.n8n.cloud/api/v1/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())
print(f"Loaded: {len(wf['nodes'])} nodes")

# Get positions of existing nodes to place new ones sensibly
positions = {}
for node in wf['nodes']:
    positions[node['name']] = node.get('position', [0, 0])

# === 1. Rewrite AI Email Personaliser to call OpenAI directly ===
for node in wf['nodes']:
    if node['name'] == 'AI Email Personaliser':
        node['parameters']['jsCode'] = r"""// AI Email Personaliser — calls OpenAI to generate actual email drafts
// Uses gpt-4o-mini for cost efficiency (~$0.01 per 10 leads)

const SYSTEM_PROMPT = `You are writing a cold email from Aaron, a web designer in Perth, Western Australia.
Write like a real person texting a mate about business — not like a marketer.

RULES:
- Use contractions (I'm, you're, don't, it's)
- Max 5-6 sentences. Shorter is better.
- Start with something specific about THEIR business (a review quote, their suburb, a specific detail)
- Never start with "I" — start with "Your", "Found", "Noticed", or the business name
- Include one honest admission: "not sure if...", "might be a stretch...", "figured I'd reach out"
- End with "Cheers, Aaron" — never "Best regards" or "Sincerely"
- CTA must be low-commitment: "interested?" or "worth a look?" — never "schedule a call"
- No jargon: no "leverage", "optimize", "streamline", "innovative", "solution", "synergy"
- No emoji
- Sound like a tradie who's good with computers, not a marketing agency
- NEVER use "I hope this email finds you well"
- NEVER use "Please don't hesitate to reach out"

CONTEXT: Aaron offers a free website to businesses without one. He'll build them a basic site for free, no strings. If they like it, he can do a professional version.

EMAIL FOOTER (always include at the end):
---
If this isn't relevant, just reply "stop" and I won't contact you again.
Aaron Parton | Mycelium AI | Perth, WA

OUTPUT FORMAT (valid JSON only):
{"subject": "short subject line", "body": "the email body", "call_script": "what Aaron should say when calling (2-3 sentences)"}`;

const VARIANTS = [
  { name: 'review_quote', instruction: 'Lead with a specific Google review quote from their business.' },
  { name: 'competitor', instruction: 'Mention how many competitors in their area already have websites.' },
  { name: 'direct', instruction: 'Be super direct and short. 3-4 sentences max.' },
  { name: 'free_offer', instruction: 'Lead with the free website offer in the first sentence.' },
];

function buildContext(lead) {
  const parts = [`Business: ${lead.business_name}`];
  if (lead.category) parts.push(`Category: ${lead.category}`);
  if (lead.suburb) parts.push(`Location: ${lead.suburb}, WA`);
  if (lead.google_reviews) parts.push(`Google Reviews: ${lead.google_reviews} (${lead.google_rating || 'N/A'} stars)`);
  if (lead.top_review_quote) parts.push(`Review quote: "${lead.top_review_quote}"`);
  if (lead.website_is_facebook) parts.push('Currently using Facebook as their website');
  if (lead.address_type) parts.push(`Address type: ${lead.address_type}`);
  parts.push(`Lead score: ${lead.score}/10`);
  return parts.join('\n');
}

const allItems = $input.all();
if (allItems.length === 0) return [];

const results = [];

for (const item of allItems) {
  const lead = item.json;
  const variant = VARIANTS[Math.floor(Math.random() * VARIANTS.length)];
  const context = buildContext(lead);

  const userPrompt = `Write a cold email for this lead. Use the ${variant.name} angle: ${variant.instruction}\n\nLEAD DATA:\n${context}\n\nRemember: output valid JSON with "subject", "body", and "call_script" fields only.`;

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${$credentials.openAiApi.apiKey}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          { role: 'user', content: userPrompt },
        ],
        temperature: 0.8,
        max_tokens: 500,
      }),
      signal: AbortSignal.timeout(30000),
    });

    const data = await response.json();
    const content = data.choices?.[0]?.message?.content || '{}';

    // Parse the JSON response
    let emailData;
    try {
      // Handle markdown code blocks
      const cleaned = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      emailData = JSON.parse(cleaned);
    } catch {
      emailData = { subject: 'Could not parse', body: content, call_script: '' };
    }

    results.push({
      json: {
        ...lead,
        email_subject: emailData.subject || '',
        email_body: emailData.body || '',
        call_script: emailData.call_script || '',
        email_variant: variant.name,
      }
    });
  } catch (err) {
    // OpenAI call failed — pass lead through without email
    results.push({
      json: {
        ...lead,
        email_subject: `[FAILED] ${err.message}`,
        email_body: '',
        call_script: '',
        email_variant: variant.name,
      }
    });
  }
}

return results;"""
        # Add OpenAI credential
        node['credentials'] = {
            'openAiApi': {
                'id': OPENAI_CRED_ID,
                'name': 'OpenAI Lead Pipeline'
            }
        }
        print("Updated AI Email Personaliser with OpenAI integration")

    # Pipeline B version
    if node['name'] == 'AI Email Personaliser1':
        node['parameters']['jsCode'] = r"""// AI Email Personaliser — Pipeline B (DIY Website upgrade pitch)
const SYSTEM_PROMPT = `You are writing a cold email from Aaron, a web designer in Perth, Western Australia.
Write like a real person texting a mate about business — not like a marketer.

RULES:
- Use contractions (I'm, you're, don't, it's)
- Max 5-6 sentences. Shorter is better.
- Start with their specific PageSpeed score or website issue
- Never start with "I"
- End with "Cheers, Aaron"
- CTA: "interested?" or "worth a look?"
- No jargon, no emoji
- Sound like a tradie who's good with computers

CONTEXT: Aaron rebuilds websites for businesses with slow DIY sites. He includes REAL data from their audit. The pitch: your site is costing you customers, I can fix it.

EMAIL FOOTER:
---
If this isn't relevant, just reply "stop" and I won't contact you again.
Aaron Parton | Mycelium AI | Perth, WA

OUTPUT: valid JSON: {"subject": "...", "body": "...", "call_script": "..."}`;

const allItems = $input.all();
if (allItems.length === 0) return [];
const results = [];

for (const item of allItems) {
  const lead = item.json;
  const parts = [`Business: ${lead.business_name}`, `Website: ${lead.website}`];
  if (lead.diy_platform) parts.push(`Platform: ${lead.diy_platform}`);
  if (lead.pagespeed_score != null) parts.push(`PageSpeed: ${lead.pagespeed_score}/100`);
  if (lead.suburb) parts.push(`Location: ${lead.suburb}, WA`);
  if (lead.google_reviews) parts.push(`Reviews: ${lead.google_reviews}`);

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${$credentials.openAiApi.apiKey}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          { role: 'user', content: `Write an upgrade-pitch email.\n\nLEAD:\n${parts.join('\n')}\n\nOutput valid JSON.` },
        ],
        temperature: 0.8,
        max_tokens: 500,
      }),
      signal: AbortSignal.timeout(30000),
    });
    const data = await response.json();
    const cleaned = (data.choices?.[0]?.message?.content || '{}').replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
    let emailData;
    try { emailData = JSON.parse(cleaned); } catch { emailData = { subject: 'Parse error', body: cleaned, call_script: '' }; }

    results.push({ json: { ...lead, email_subject: emailData.subject || '', email_body: emailData.body || '', call_script: emailData.call_script || '', email_variant: 'upgrade_pitch' } });
  } catch (err) {
    results.push({ json: { ...lead, email_subject: `[FAILED] ${err.message}`, email_body: '', call_script: '' } });
  }
}
return results;"""
        node['credentials'] = {
            'openAiApi': {
                'id': OPENAI_CRED_ID,
                'name': 'OpenAI Lead Pipeline'
            }
        }
        print("Updated AI Email Personaliser1 (Pipeline B)")

# === 2. Add Supabase Upsert node after Lead Scorer A ===
scorer_pos = positions.get('Lead Scorer A', [384, -176])
supabase_node = {
    "parameters": {
        "operation": "executeQuery",
        "query": "=SELECT '{{ JSON.stringify($input.all().map(i => i.json)) }}'::text as leads_json;",
        "options": {}
    },
    "id": "supabase-upsert-a",
    "name": "Supabase: Store Leads",
    "type": "n8n-nodes-base.postgres",
    "typeVersion": 2.5,
    "position": [scorer_pos[0] + 100, scorer_pos[1] + 150],
    "credentials": {
        "postgres": {
            "id": PG_CRED_ID,
            "name": "Supabase Pipeline Postgres"
        }
    }
}

# Actually, let's use a Code node to do the Supabase insert via HTTP API instead
# This is simpler and more reliable than trying to build dynamic SQL in n8n
supabase_node = {
    "parameters": {
        "jsCode": r"""// Store all scored leads in Supabase via PostgREST API
// Uses the Supabase anon key for API access
const SUPABASE_URL = 'https://zdaznnifkhdioczrxsae.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpkYXpubmlma2hkaW9jenJ4c2FlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5MDMzNjgsImV4cCI6MjA4OTQ3OTM2OH0.NxE7BsIGAfLpowkRCo0eaIOXJZjiq1ozCeRCbgxb5QI';

const allItems = $input.all();
if (allItems.length === 0) return [];

let stored = 0;
let dupes = 0;
let errors = 0;

for (const item of allItems) {
  const lead = item.json;

  const row = {
    business_name: lead.business_name || 'Unknown',
    phone: lead.phone || null,
    email: lead.email || null,
    category: lead.category || null,
    address: lead.address || null,
    suburb: lead.suburb || null,
    postcode: lead.postcode || null,
    state: 'WA',
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
    const response = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Prefer': 'resolution=ignore-duplicates,return=minimal',
      },
      body: JSON.stringify(row),
      signal: AbortSignal.timeout(10000),
    });

    if (response.ok || response.status === 201) {
      stored++;
    } else if (response.status === 409) {
      dupes++;
    } else {
      const err = await response.text();
      if (err.includes('duplicate') || err.includes('unique')) {
        dupes++;
      } else {
        errors++;
      }
    }
  } catch (err) {
    errors++;
  }
}

// Pass all leads through (don't filter) + add storage stats
return allItems.map((item, i) => ({
  json: {
    ...item.json,
    _db_stored: i === 0 ? { stored, dupes, errors, total: allItems.length } : undefined,
  }
}));"""
    },
    "id": "supabase-store-1",
    "name": "Supabase: Store Leads",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [scorer_pos[0] + 100, scorer_pos[1] + 150],
}

# Check if node already exists
exists = any(n['name'] == 'Supabase: Store Leads' for n in wf['nodes'])
if not exists:
    wf['nodes'].append(supabase_node)
    # Wire it: Lead Scorer A -> both Tag & Pass AND Supabase Store (parallel)
    # Currently: Lead Scorer A -> Tag & Pass All Leads
    # New: Lead Scorer A -> Tag & Pass All Leads (main flow)
    #      Lead Scorer A -> Supabase: Store Leads (parallel, no downstream)
    current_targets = wf['connections'].get('Lead Scorer A', {}).get('main', [[]])[0]
    current_targets.append({
        "node": "Supabase: Store Leads",
        "type": "main",
        "index": 0
    })
    print("Added Supabase: Store Leads node (parallel to scoring flow)")
else:
    print("Supabase: Store Leads already exists")

# === 3. Push update ===
payload = {k: v for k, v in wf.items() if k in {'name', 'nodes', 'connections', 'settings'}}
data = json.dumps(payload).encode()
req = urllib.request.Request(
    f'https://aaronparton2.app.n8n.cloud/api/v1/workflows/{WF_ID}',
    data=data,
    headers={'Content-Type': 'application/json', 'X-N8N-API-KEY': API_KEY},
    method='PUT'
)
try:
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    print(f"\nWorkflow updated ({len(result.get('nodes', []))} nodes)")

    # Verify key connections
    c = result.get('connections', {})
    for source in ['Lead Scorer A', 'Tag & Pass All Leads', 'AI Email Personaliser']:
        if source in c:
            targets = [t['node'] for t in c[source]['main'][0]]
            print(f"  {source} -> {targets}")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()[:500]}")
    sys.exit(1)
