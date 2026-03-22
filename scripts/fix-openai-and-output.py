"""Fix OpenAI calls (fetch not available in n8n Code nodes) and redesign output.
n8n Code nodes need $http.request() instead of fetch().
Also: redesign the lead output to be concise and actionable.
"""
import json, urllib.request, sys

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNjE4ODEyNC02YzNiLTQxZDktODdhMS01MDljNmIzOTVkZmMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzcxNjQxODY1fQ.IWzbpXkITsoUvqLLpROW3hQ3PvGo_11D0yLjqRUVaXM'
WF_ID = '3qqw96oRGpyqxt57'
OPENAI_CRED_ID = 'DX0ChPZkozXYBGrr'

req = urllib.request.Request(
    f'https://aaronparton2.app.n8n.cloud/api/v1/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())

fixes = []

# === AI Email Personaliser — use $http.request instead of fetch ===
AI_PERSONALISER_CODE = r"""// AI Email Personaliser — generates real email drafts via OpenAI
// Uses n8n's $http.request (fetch is not available in Code nodes)

const SYSTEM_PROMPT = `You are writing a cold email from Aaron, a web designer in Perth, Western Australia.
Write like a real person texting a mate about business — not like a marketer.

RULES:
- Use contractions (I'm, you're, don't, it's)
- Max 5-6 sentences. Shorter is better.
- Start with something specific about THEIR business (a review quote, their suburb, a detail)
- Never start with "I" — start with "Your", "Found", "Noticed", or the business name
- Include one honest admission: "not sure if...", "might be a stretch...", "figured I'd reach out"
- End with "Cheers, Aaron" — never "Best regards" or "Sincerely"
- CTA must be low-commitment: "interested?" or "worth a look?" — never "schedule a call"
- No jargon: no "leverage", "optimize", "streamline", "innovative", "solution", "synergy"
- No emoji
- Sound like a tradie who's good with computers, not a marketing agency
- NEVER use "I hope this email finds you well"

CONTEXT: Aaron offers a free website to businesses without one. He'll build them a basic site for free, no strings. If they like it, he can do a professional version.

EMAIL FOOTER (always include):
---
If this isn't relevant, just reply "stop" and I won't contact you again.
Aaron Parton | Mycelium AI | Perth, WA

OUTPUT FORMAT (valid JSON only, no markdown):
{"subject": "short subject line", "body": "the email body", "call_script": "what Aaron says when calling (2-3 sentences, casual)"}`;

const VARIANTS = [
  { name: 'review_quote', instruction: 'Lead with a specific Google review quote if available.' },
  { name: 'competitor', instruction: 'Mention that competitors in their area already have websites.' },
  { name: 'direct', instruction: 'Super direct. 3-4 sentences max.' },
  { name: 'free_offer', instruction: 'Lead with the free website offer immediately.' },
];

const allItems = $input.all();
if (allItems.length === 0) return [];

const results = [];

for (const item of allItems) {
  const lead = item.json;
  const variant = VARIANTS[Math.floor(Math.random() * VARIANTS.length)];

  // Build concise lead context
  const parts = [`Business: ${lead.business_name}`];
  if (lead.category) parts.push(`Trade: ${lead.category}`);
  if (lead.suburb) parts.push(`Location: ${lead.suburb}, WA`);
  if (lead.google_reviews) parts.push(`${lead.google_reviews} Google reviews (${lead.google_rating || '?'} stars)`);
  if (lead.top_review_quote) parts.push(`Best review: "${lead.top_review_quote.substring(0, 100)}"`);
  if (lead.website_is_facebook) parts.push('Using Facebook as website');
  if (lead.phone) parts.push(`Phone: ${lead.phone}`);

  const userPrompt = `Write a cold email. Angle: ${variant.instruction}\n\nLEAD:\n${parts.join('\n')}\n\nValid JSON only.`;

  try {
    const response = await this.helpers.httpRequest({
      method: 'POST',
      url: 'https://api.openai.com/v1/chat/completions',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${$credentials.openAiApi.apiKey}`,
      },
      body: {
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          { role: 'user', content: userPrompt },
        ],
        temperature: 0.8,
        max_tokens: 500,
      },
      timeout: 30000,
    });

    const content = response.choices?.[0]?.message?.content || '{}';
    let emailData;
    try {
      const cleaned = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      emailData = JSON.parse(cleaned);
    } catch {
      emailData = { subject: 'Parse error', body: content, call_script: '' };
    }

    // Build the concise "why this lead" summary
    const whyParts = [];
    if (lead.google_reviews >= 20) whyParts.push(`${lead.google_reviews} reviews`);
    else if (lead.google_reviews >= 5) whyParts.push(`${lead.google_reviews} reviews`);
    if (lead.website_is_facebook) whyParts.push('FB only');
    if (lead.address_type === 'residential') whyParts.push('home-based');
    if (lead.hipages_jobs >= 10) whyParts.push(`${lead.hipages_jobs} HiPages jobs`);
    if (lead.registration_date) whyParts.push('new registration');
    const whySummary = whyParts.length > 0 ? whyParts.join(', ') : 'standard lead';

    results.push({
      json: {
        // === WHAT AARON SEES (top-level, scannable) ===
        business_name: lead.business_name,
        phone: lead.phone,
        suburb: lead.suburb,
        category: lead.category,
        score: lead.score,
        why: `${lead.score}/10 — ${whySummary}`,
        tier: lead.outreach_tier,
        draft_subject: emailData.subject || '',
        draft_email: emailData.body || '',
        call_script: emailData.call_script || '',
        // === METADATA (for Instantly/Supabase later) ===
        email: lead.email,
        email_variant: variant.name,
        address_type: lead.address_type,
        google_reviews: lead.google_reviews,
        google_rating: lead.google_rating,
        website: lead.website,
        pipeline: lead.pipeline,
        website_verified: lead.website_verified,
        website_check_method: lead.website_check_method,
        postcode: lead.postcode,
        address: lead.address,
        source: lead.source,
        score_breakdown: lead.score_breakdown,
        top_review_quote: lead.top_review_quote,
        found_on_sources: lead.found_on_sources,
        place_id: lead.place_id,
        abn: lead.abn,
      }
    });
  } catch (err) {
    results.push({
      json: {
        business_name: lead.business_name,
        phone: lead.phone,
        suburb: lead.suburb,
        category: lead.category,
        score: lead.score,
        why: `${lead.score}/10 — OpenAI failed`,
        tier: lead.outreach_tier,
        draft_subject: `[ERROR] ${err.message || 'Unknown error'}`,
        draft_email: '',
        call_script: '',
        email: lead.email,
        email_variant: 'failed',
        pipeline: lead.pipeline,
        address_type: lead.address_type,
        google_reviews: lead.google_reviews,
        website: lead.website,
        source: lead.source,
        score_breakdown: lead.score_breakdown,
        postcode: lead.postcode,
        address: lead.address,
      }
    });
  }
}

return results;"""

# === Log Pipeline Run — redesigned for busy agency owner ===
LOG_CODE = r"""// Pipeline Run Summary — designed for a busy agency owner
const items = $input.all();
if (items.length === 0) return [{ json: { summary: 'No leads this run' } }];

const leads = items.map(i => i.json);
const priorityCalls = leads.filter(l => l.tier === 'priority_call');
const emailOnly = leads.filter(l => l.tier === 'email_only');
const now = new Date();

// Build the call list — what Aaron actually needs
const callList = priorityCalls.map((l, i) => ({
  rank: i + 1,
  name: l.business_name,
  phone: l.phone || 'NO PHONE',
  suburb: l.suburb,
  category: l.category,
  why: l.why,
  call_script: l.call_script,
  draft_subject: l.draft_subject,
}));

return [{
  json: {
    // === GLANCEABLE SUMMARY ===
    headline: `${leads.length} leads found | ${priorityCalls.length} worth calling | ${emailOnly.length} email-only`,
    run_date: now.toISOString().split('T')[0],
    pipeline: 'no_website',

    // === CALL LIST (priority leads only) ===
    call_list: callList,

    // === ALL LEADS (full data for review) ===
    all_leads: leads.map(l => ({
      name: l.business_name,
      phone: l.phone,
      suburb: l.suburb,
      category: l.category,
      score: l.score,
      why: l.why,
      tier: l.tier,
      draft_subject: l.draft_subject,
      draft_email: l.draft_email,
    })),
  }
}];"""

for node in wf['nodes']:
    name = node['name']

    if name == 'AI Email Personaliser':
        node['parameters']['jsCode'] = AI_PERSONALISER_CODE
        node['credentials'] = {
            'openAiApi': {
                'id': OPENAI_CRED_ID,
                'name': 'OpenAI Lead Pipeline'
            }
        }
        fixes.append(name)

    elif name == 'AI Email Personaliser1':
        # Same fix for Pipeline B — use this.helpers.httpRequest
        code = node['parameters'].get('jsCode', '')
        code = code.replace(
            "await fetch('https://api.openai.com/v1/chat/completions', {\n      method: 'POST',\n      headers: {",
            "await this.helpers.httpRequest({\n      method: 'POST',\n      url: 'https://api.openai.com/v1/chat/completions',\n      headers: {"
        )
        code = code.replace(
            "      body: JSON.stringify({",
            "      body: {"
        )
        code = code.replace(
            "      }),\n      signal: AbortSignal.timeout(30000),\n    });",
            "      },\n      timeout: 30000,\n    });"
        )
        # Remove response.json() since httpRequest returns parsed JSON directly
        code = code.replace(
            "    const data = await response.json();\n    const cleaned = (data.choices",
            "    const cleaned = (response.choices"
        )
        node['parameters']['jsCode'] = code
        node['credentials'] = {
            'openAiApi': {
                'id': OPENAI_CRED_ID,
                'name': 'OpenAI Lead Pipeline'
            }
        }
        fixes.append(name)

    elif name == 'Log Pipeline Run':
        node['parameters']['jsCode'] = LOG_CODE
        fixes.append(name)

    elif name == 'Log Pipeline Run1':
        node['parameters']['jsCode'] = LOG_CODE.replace("'no_website'", "'diy_website'")
        fixes.append(name)

    # === Fix Supabase Store node too — also uses fetch ===
    elif name == 'Supabase: Store Leads':
        code = node['parameters'].get('jsCode', '')
        if 'await fetch(' in code:
            code = code.replace(
                "    const response = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {\n      method: 'POST',\n      headers: {\n        'Content-Type': 'application/json',\n        'apikey': SUPABASE_KEY,\n        'Authorization': `Bearer ${SUPABASE_KEY}`,\n        'Prefer': 'resolution=ignore-duplicates,return=minimal',\n      },\n      body: JSON.stringify(row),\n      signal: AbortSignal.timeout(10000),\n    });",
                """    const response = await this.helpers.httpRequest({
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
    }).catch(err => ({ statusCode: err.statusCode || 500, body: err.message }));"""
            )
            code = code.replace(
                "    if (response.ok || response.status === 201) {\n      stored++;\n    } else if (response.status === 409) {\n      dupes++;\n    } else {\n      const err = await response.text();\n      if (err.includes('duplicate') || err.includes('unique')) {\n        dupes++;\n      } else {\n        errors++;\n      }\n    }",
                "    const status = response.statusCode || 201;\n    if (status >= 200 && status < 300) {\n      stored++;\n    } else if (status === 409 || String(response.body || '').includes('duplicate')) {\n      dupes++;\n    } else {\n      errors++;\n    }"
            )
            node['parameters']['jsCode'] = code
            fixes.append(name)

print(f"Fixed {len(fixes)} nodes: {fixes}")

# Push
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
    print(f"Workflow updated ({len(result.get('nodes', []))} nodes)")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()[:500]}")
    sys.exit(1)
