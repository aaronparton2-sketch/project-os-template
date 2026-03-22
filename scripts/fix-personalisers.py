"""Fix both AI Email Personaliser nodes in n8n.
- Pipeline A: no_website leads (free website offer)
- Pipeline B: diy_website leads (upgrade pitch with audit data)

Fixes:
1. Uses this.helpers.httpRequest (n8n Code node compatible)
2. Reads OpenAI key from .env and injects directly (Code nodes can't use $credentials)
3. Consistent output fields: draft_subject, draft_email, call_script
4. A/B variants for both pipelines
5. Full anti-slop framework
6. Mode: runOnceForEachItem — processes 1 lead per execution (avoids 60s timeout)
"""
import json, urllib.request, sys, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

N8N_API_KEY = os.environ['N8N_API_KEY']
N8N_API_URL = os.environ['N8N_API_URL']
OPENAI_KEY = os.environ['OPENAI_API_KEY']
WF_ID = '3qqw96oRGpyqxt57'

# ── Fetch current workflow ──
req = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': N8N_API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())

# ── Pipeline A Code (runOnceForEachItem — single lead per execution) ──
PIPELINE_A_CODE = f'''// AI Email Personaliser — Pipeline A (No Website — free site offer)
// Mode: Run Once for Each Item — processes 1 lead per execution

const API_KEY = '{OPENAI_KEY}';

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
- Vary sentence length — not all the same rhythm
- One sentence can be a fragment. That's fine.
- Sound like a tradie who's good with computers, not a marketing agency
- NEVER use "I hope this email finds you well" or similar
- NEVER use "I was impressed by" — reference something specific instead
- NEVER use "Please don't hesitate to reach out"
- NEVER use exactly 3 bullet points
- NEVER use perfect grammar throughout — use natural fragments and contractions
- Include Aaron's phone number (0498 201 788) in the sign-off

CONTEXT: Aaron offers a free website to businesses without one. The pitch is simple — he'll build them a basic site for free, no strings. If they like it, he can do a professional version.

EMAIL FOOTER (always include):
---
If this isn't relevant, just reply "stop" and I won't contact you again.
Aaron Parton | Mycelium AI | Perth, WA

OUTPUT FORMAT (valid JSON only, no markdown, no code fences):
{{"subject": "short subject line (no clickbait)", "body": "the email body (5-6 sentences max)", "call_script": "what Aaron should say when he calls (2-3 sentences, casual)"}}`;

const VARIANTS = [
  {{ name: 'review_quote', instruction: 'Lead with a specific Google review quote from their business. If no quote available, reference their review count and rating.' }},
  {{ name: 'competitor', instruction: 'Mention that competitors in their area already have websites. Make it about opportunity, not fear.' }},
  {{ name: 'direct', instruction: 'Super direct and short. 3-4 sentences max. No fluff at all.' }},
  {{ name: 'free_offer', instruction: 'Lead with the free website offer immediately in the first sentence. Make it clear there is genuinely no catch.' }},
];

const lead = $input.item.json;
const variant = VARIANTS[Math.floor(Math.random() * VARIANTS.length)];

// Build lead context
const parts = [`Business: ${{lead.business_name}}`];
if (lead.category) parts.push(`Trade: ${{lead.category}}`);
if (lead.suburb) parts.push(`Location: ${{lead.suburb}}, WA`);
if (lead.google_reviews) parts.push(`${{lead.google_reviews}} Google reviews (${{lead.google_rating || '?'}} stars)`);
if (lead.top_review_quote) parts.push(`Best review: "${{lead.top_review_quote.substring(0, 120)}}"`);
if (lead.website_is_facebook) parts.push('Currently using Facebook as their website');
if (lead.competitors_with_website) parts.push(`Competitors with websites: ${{lead.competitors_with_website}}`);
if (lead.hipages_jobs) parts.push(`HiPages jobs completed: ${{lead.hipages_jobs}}`);
if (lead.phone) parts.push(`Phone: ${{lead.phone}}`);
parts.push(`Score: ${{lead.score}}/10`);

const userPrompt = `Write a cold email. Angle: ${{variant.instruction}}\\n\\nLEAD:\\n${{parts.join('\\n')}}\\n\\nOutput valid JSON only — no markdown, no code fences.`;

try {{
  const response = await this.helpers.httpRequest({{
    method: 'POST',
    url: 'https://api.openai.com/v1/chat/completions',
    headers: {{
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${{API_KEY}}`,
    }},
    body: {{
      model: 'gpt-4o-mini',
      messages: [
        {{ role: 'system', content: SYSTEM_PROMPT }},
        {{ role: 'user', content: userPrompt }},
      ],
      temperature: 0.8,
      max_tokens: 500,
    }},
    timeout: 30000,
  }});

  const content = response.choices?.[0]?.message?.content || '{{}}';
  let emailData;
  try {{
    const cleaned = content.replace(/```json\\n?/g, '').replace(/```\\n?/g, '').trim();
    emailData = JSON.parse(cleaned);
  }} catch {{
    emailData = {{ subject: 'Parse error', body: content, call_script: '' }};
  }}

  // Build "why this lead" summary
  const whyParts = [];
  if (lead.google_reviews >= 20) whyParts.push(`${{lead.google_reviews}} reviews`);
  else if (lead.google_reviews >= 5) whyParts.push(`${{lead.google_reviews}} reviews`);
  if (lead.website_is_facebook) whyParts.push('FB only');
  if (lead.address_type === 'residential') whyParts.push('home-based');
  if (lead.hipages_jobs >= 10) whyParts.push(`${{lead.hipages_jobs}} HiPages jobs`);
  if (lead.registration_date) whyParts.push('new registration');
  const whySummary = whyParts.length > 0 ? whyParts.join(', ') : 'standard lead';

  return {{
    json: {{
      business_name: lead.business_name,
      phone: lead.phone || '',
      suburb: lead.suburb || '',
      category: lead.category || '',
      score: lead.score,
      why: `${{lead.score}}/10 — ${{whySummary}}`,
      tier: lead.outreach_tier || (lead.score >= 7 ? 'priority_call' : 'email_only'),
      draft_subject: emailData.subject || '',
      draft_email: emailData.body || '',
      call_script: emailData.call_script || '',
      email: lead.email || '',
      email_variant: variant.name,
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
    }}
  }};
}} catch (err) {{
  return {{
    json: {{
      business_name: lead.business_name,
      phone: lead.phone || '',
      suburb: lead.suburb || '',
      category: lead.category || '',
      score: lead.score,
      why: `${{lead.score}}/10 — OpenAI failed`,
      tier: lead.outreach_tier || 'email_only',
      draft_subject: `[ERROR] ${{err.message || 'Unknown error'}}`,
      draft_email: '',
      call_script: '',
      email: lead.email || '',
      email_variant: 'failed',
      pipeline: lead.pipeline || 'no_website',
      address_type: lead.address_type || '',
      google_reviews: lead.google_reviews,
      website: lead.website || '',
      source: lead.source || '',
      score_breakdown: lead.score_breakdown,
      postcode: lead.postcode || '',
      address: lead.address || '',
    }}
  }};
}}'''

# ── Pipeline B Code (runOnceForEachItem — single lead per execution) ──
PIPELINE_B_CODE = f'''// AI Email Personaliser — Pipeline B (DIY Website — upgrade pitch with audit data)
// Mode: Run Once for Each Item — processes 1 lead per execution

const API_KEY = '{OPENAI_KEY}';

const SYSTEM_PROMPT = `You are writing a cold email from Aaron, a web designer in Perth, Western Australia.
Write like a real person texting a mate about business — not like a marketer.

RULES:
- Use contractions (I'm, you're, don't, it's)
- Max 5-6 sentences. Shorter is better.
- Start with their specific PageSpeed score or a concrete website issue you found
- Never start with "I" — start with "Your", "Found", "Noticed", or the business name
- Include one honest admission: "not sure if...", "might be a stretch...", "figured I'd reach out"
- End with "Cheers, Aaron" — never "Best regards" or "Sincerely"
- CTA must be low-commitment: "interested?" or "worth a look?" — never "schedule a call"
- No jargon: no "leverage", "optimize", "streamline", "innovative", "solution", "synergy"
- No emoji
- Vary sentence length — not all the same rhythm
- One sentence can be a fragment. That's fine.
- Sound like a tradie who's good with computers, not a marketing agency
- NEVER use "I hope this email finds you well" or similar
- NEVER use "I was impressed by" — reference something specific instead
- NEVER use "Please don't hesitate to reach out"
- NEVER use exactly 3 bullet points
- Include Aaron's phone number (0498 201 788) in the sign-off
- Reference ACTUAL audit data — PageSpeed scores, platform, mobile issues. Be specific.

CONTEXT: Aaron rebuilds websites for businesses that have a DIY site (Wix, Squarespace, etc.) that's slow or poorly built. He includes REAL data from their site audit — PageSpeed scores, specific issues found. The pitch is: your site is costing you customers, I can fix it.

EMAIL FOOTER (always include):
---
If this isn't relevant, just reply "stop" and I won't contact you again.
Aaron Parton | Mycelium AI | Perth, WA

OUTPUT FORMAT (valid JSON only, no markdown, no code fences):
{{"subject": "short subject line (references their specific issue)", "body": "the email body (5-6 sentences max, includes actual PageSpeed score and issues)", "call_script": "what Aaron should say when he calls (2-3 sentences, references audit data)"}}`;

const VARIANTS = [
  {{ name: 'speed_score', instruction: 'Lead with their exact PageSpeed score and what it means for visitors. Frame it as money lost.' }},
  {{ name: 'mobile_issue', instruction: 'Focus on mobile experience — most of their customers search on phones. Reference their mobile score if available.' }},
  {{ name: 'competitor_compare', instruction: 'Mention that their competitors have faster/better sites. Make it about falling behind, not fear.' }},
  {{ name: 'money_loss', instruction: 'Frame it as money they are losing — "40% of visitors leave before your page loads". Reference Google Ads spend if they run ads.' }},
];

const lead = $input.item.json;
const variant = VARIANTS[Math.floor(Math.random() * VARIANTS.length)];

// Build lead context
const parts = [`Business: ${{lead.business_name}}`];
if (lead.category) parts.push(`Trade: ${{lead.category}}`);
if (lead.suburb) parts.push(`Location: ${{lead.suburb}}, WA`);
if (lead.website) parts.push(`Website: ${{lead.website}}`);
if (lead.diy_platform) parts.push(`Platform: ${{lead.diy_platform}}`);
if (lead.pagespeed_score != null) parts.push(`PageSpeed desktop: ${{lead.pagespeed_score}}/100`);
if (lead.pagespeed_mobile != null) parts.push(`PageSpeed mobile: ${{lead.pagespeed_mobile}}/100`);
if (lead.google_reviews) parts.push(`${{lead.google_reviews}} Google reviews (${{lead.google_rating || '?'}} stars)`);
if (lead.has_ssl === false) parts.push('No SSL certificate (browser shows "Not Secure")');
if (lead.has_meta_description === false) parts.push('Missing meta description (invisible to Google)');
if (lead.mobile_friendly === false) parts.push('Not mobile-friendly');
if (lead.seo_issues && lead.seo_issues.length > 0) parts.push(`SEO issues: ${{lead.seo_issues.join(', ')}}`);
if (lead.running_google_ads) parts.push('Currently running Google Ads (spending money on marketing)');
if (lead.phone) parts.push(`Phone: ${{lead.phone}}`);
parts.push(`Score: ${{lead.score}}/10`);

const userPrompt = `Write an upgrade-pitch email. Angle: ${{variant.instruction}}\\n\\nLEAD:\\n${{parts.join('\\n')}}\\n\\nOutput valid JSON only — no markdown, no code fences.`;

try {{
  const response = await this.helpers.httpRequest({{
    method: 'POST',
    url: 'https://api.openai.com/v1/chat/completions',
    headers: {{
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${{API_KEY}}`,
    }},
    body: {{
      model: 'gpt-4o-mini',
      messages: [
        {{ role: 'system', content: SYSTEM_PROMPT }},
        {{ role: 'user', content: userPrompt }},
      ],
      temperature: 0.8,
      max_tokens: 500,
    }},
    timeout: 30000,
  }});

  const content = response.choices?.[0]?.message?.content || '{{}}';
  let emailData;
  try {{
    const cleaned = content.replace(/```json\\n?/g, '').replace(/```\\n?/g, '').trim();
    emailData = JSON.parse(cleaned);
  }} catch {{
    emailData = {{ subject: 'Parse error', body: content, call_script: '' }};
  }}

  // Build "why this lead" summary
  const whyParts = [];
  if (lead.pagespeed_score != null && lead.pagespeed_score < 50) whyParts.push(`speed ${{lead.pagespeed_score}}/100`);
  if (lead.diy_platform) whyParts.push(lead.diy_platform);
  if (lead.google_reviews >= 20) whyParts.push(`${{lead.google_reviews}} reviews`);
  if (lead.running_google_ads) whyParts.push('running ads');
  if (lead.address_type === 'residential') whyParts.push('home-based');
  if (lead.has_ssl === false) whyParts.push('no SSL');
  if (lead.mobile_friendly === false) whyParts.push('not mobile-friendly');
  const whySummary = whyParts.length > 0 ? whyParts.join(', ') : 'standard lead';

  return {{
    json: {{
      business_name: lead.business_name,
      phone: lead.phone || '',
      suburb: lead.suburb || '',
      category: lead.category || '',
      score: lead.score,
      why: `${{lead.score}}/10 — ${{whySummary}}`,
      tier: lead.outreach_tier || (lead.score >= 7 ? 'priority_call' : 'email_only'),
      draft_subject: emailData.subject || '',
      draft_email: emailData.body || '',
      call_script: emailData.call_script || '',
      email: lead.email || '',
      email_variant: variant.name,
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
    }}
  }};
}} catch (err) {{
  return {{
    json: {{
      business_name: lead.business_name,
      phone: lead.phone || '',
      suburb: lead.suburb || '',
      category: lead.category || '',
      score: lead.score,
      why: `${{lead.score}}/10 — OpenAI failed`,
      tier: lead.outreach_tier || 'email_only',
      draft_subject: `[ERROR] ${{err.message || 'Unknown error'}}`,
      draft_email: '',
      call_script: '',
      email: lead.email || '',
      email_variant: 'failed',
      pipeline: lead.pipeline || 'diy_website',
      address_type: lead.address_type || '',
      google_reviews: lead.google_reviews,
      website: lead.website || '',
      diy_platform: lead.diy_platform || '',
      pagespeed_score: lead.pagespeed_score,
      source: lead.source || '',
      score_breakdown: lead.score_breakdown,
      postcode: lead.postcode || '',
      address: lead.address || '',
    }}
  }};
}}'''

# ── Apply to workflow ──
fixes = []
for node in wf['nodes']:
    name = node['name']
    if name == 'AI Email Personaliser':
        node['parameters']['jsCode'] = PIPELINE_A_CODE
        node['parameters']['mode'] = 'runOnceForEachItem'
        node.pop('credentials', None)
        fixes.append(f'{name} (Pipeline A)')
    elif name == 'AI Email Personaliser1':
        node['parameters']['jsCode'] = PIPELINE_B_CODE
        node['parameters']['mode'] = 'runOnceForEachItem'
        node.pop('credentials', None)
        fixes.append(f'{name} (Pipeline B)')

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
