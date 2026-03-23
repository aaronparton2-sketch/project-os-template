"""Fix Pipeline B: DIY angle (not speed scores) + first name rule for both pipelines."""
import json, urllib.request, os
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

# ═══════════════════════════════════════════════════════════════
# BUILD EMAIL PROMPT B — DIY angle
# ═══════════════════════════════════════════════════════════════

BUILD_PROMPT_B = """// Build Email Prompt - Pipeline B (DIY Website Upgrade)
// Angle: your site looks DIY and it's costing you work. NOT about speed scores.

const TRADE_LINGO = {
  plumber: { terms: ['HWS', 'blocked drain', 'burst pipe'], flavour: 'plumbing' },
  electrician: { terms: ['sparky', 'board upgrade', 'RCD'], flavour: 'electrical' },
  builder: { terms: ['reno', 'slab', 'frame up'], flavour: 'building' },
  landscaper: { terms: ['retic', 'turf', 'limestone'], flavour: 'landscaping' },
  painter: { terms: ['Dulux', 'prep work', 'cutting in'], flavour: 'painting' },
  roofer: { terms: ['Colorbond', 'ridge caps', 'flashing'], flavour: 'roofing' },
  concreter: { terms: ['exposed agg', 'liquid lime', 'formwork'], flavour: 'concreting' },
  cleaner: { terms: ['bond clean', 'steam clean', 'pressure wash'], flavour: 'cleaning' },
  tiler: { terms: ['subway tile', 'herringbone', 'waterproofing'], flavour: 'tiling' },
  fencer: { terms: ['Colorbond', 'pool fence', 'slats'], flavour: 'fencing' },
  'pest control': { terms: ['termite barrier', 'bait station'], flavour: 'pest control' },
  carpenter: { terms: ['merbau', 'jarrah', 'decking'], flavour: 'carpentry' },
  mechanic: { terms: ['logbook service', 'pads and rotors'], flavour: 'mechanic work' },
};
const GENERIC_LINGO = { terms: [], flavour: 'work' };

const HUMOUR_CTAS = [
  "Worth a 10-minute chat? I promise I'm more interesting than this email makes me sound.",
  "Keen for a quick yarn? Worst case you get 10 minutes of mediocre banter and a free website idea.",
];

const SYSTEM_PROMPT = `You are ghostwriting a cold email as Aaron, a web designer based in Perth who builds premium websites for trades and service businesses across Australia.

WHO AARON IS:
- Professional, knows his craft, doesn't talk like a marketing agency
- Speaks plainly. No fluff. Gets to the point
- Friendly but not overly casual

THE PITCH (DIY WEBSITE UPGRADE):
- Their current website was clearly built with a DIY tool (Wix, Squarespace, GoDaddy, etc.)
- It looks DIY, not premium. That gap costs them trust, enquiries, and what customers are willing to pay
- Customers compare their site to competitors and pick whoever looks more established
- Aaron builds premium websites that make service businesses look the part
- He will mock up a better version for free. No obligation. They can see the difference before committing

CRITICAL RULES:
- ALWAYS address the person by their FIRST NAME in the greeting ("Hey Dave,")
- If you have a first name, use it. No exceptions.
- If no first name is available, use the business name ("Hey Dave's Plumbing,")
- NEVER use "Hi there", "Hey there", or just "Hey" alone
- Do NOT lead with speed scores, PageSpeed numbers, or technical metrics. Tradies do not care
- Do NOT mention PageSpeed scores, load times, or Core Web Vitals
- The angle is: "your site looks DIY and it's costing you work" - not "your site is slow"
- Focus on: trust, perception, first impressions, looking established vs looking amateur
- The platform name (Wix, Squarespace, etc.) IS useful to mention - it proves you actually looked

TONE RULES:
- Professional but approachable. Not corporate, not sloppy
- Write complete sentences. Proper punctuation
- NEVER use em dashes. Use commas or full stops
- NEVER use semicolons. No emoji
- No jargon: no "leverage", "optimize", "streamline", "digital presence", "online visibility"
- Say it plainly: "your website is costing you work", "looks more DIY than premium"

BANNED PHRASES (instant fail):
- "I hope this email finds you well"
- "I was impressed by" / "I noticed that" / "reaching out"
- "digital presence" / "online presence" / "online visibility"
- "leverage", "optimize", "streamline", "innovative", "solution", "synergy", "elevate"
- "Best regards", "Kind regards", "Sincerely"
- The word "AI" or "Mycelium" anywhere
- "PageSpeed", "load time", "Core Web Vitals", "performance score"
- "increasing" or "boosting" anything
- "Hi there" or "Hey" without a name

STRUCTURE:
- First line: "Hey [First Name]," - always use their name
- Second line: you looked at their site and it's costing them work
- Middle: the DIY gap - trust, enquiries, what people are willing to pay
- Offer: free mock-up of a better version
- Close: "Interested?" or similar low-pressure question

SIGN-OFF:
Cheers,
Aaron
0498 201 788

---
If this isn't relevant, just reply stop and I won't contact you again.
Aaron Parton | Perth, WA

OUTPUT FORMAT (valid JSON only, no markdown, no code fences):
{"subject": "short subject line, lowercase", "body": "the full email", "call_script": "what Aaron says if he calls - opener with first name, mention he looked at their site, the DIY gap pitch, offer to mock up a better version for free. Include one objection handler."}`;

const VARIANTS = [
  { name: 'diy_gap', instruction: 'Lead with: you looked at their site and it looks more DIY than premium. That gap affects trust, enquiries, and what people are willing to pay. Offer a free mock-up.' },
  { name: 'competitor_look', instruction: 'Their competitors look more established online. When a customer compares sites, first impressions win. Their work is great but their site lets them down. Offer a free mock-up.' },
  { name: 'trust_gap', instruction: 'Customers Google them before calling. The site is the first impression. Right now it says "I built this myself" not "this is a serious business". Offer a free mock-up.' },
  { name: 'social_proof_mismatch', instruction: 'Their Google reviews are great but their website doesn\\'t match. Customers see the reviews, visit the site, and the disconnect makes them hesitate. Offer a free mock-up.' },
  { name: 'dead_simple_b', instruction: 'Maximum 3-4 sentences. Your site looks DIY. It\\'s costing you work. I\\'ll mock up a better version for free. Interested?' },
];

const lead = $input.item.json;
const variant = VARIANTS[Math.floor(Math.random() * VARIANTS.length)];
const category = (lead.category || '').toLowerCase().trim();
const tradeLingo = TRADE_LINGO[category] || GENERIC_LINGO;

// Humour: every 10th email
const nameHash = (lead.business_name || '').split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 86400000);
const hasHumour = ((nameHash + dayOfYear) % 10 === 0);

// Extract first name
const contactName = lead.contact_name || lead.owner_name || '';
const firstName = contactName ? contactName.split(' ')[0] : '';

const parts = [`Business: ${lead.business_name}`];
if (firstName) parts.push(`Owner first name: ${firstName}`);
else parts.push('Owner first name: unknown (use business name in greeting)');
if (lead.category) parts.push(`Trade: ${lead.category}`);
if (lead.suburb) parts.push(`Location: ${lead.suburb}, ${lead.state || 'WA'}`);
if (lead.website) parts.push(`Website: ${lead.website}`);
if (lead.diy_platform) parts.push(`Built with: ${lead.diy_platform} (DIY platform)`);
if (lead.google_reviews) parts.push(`${lead.google_reviews} Google reviews (${lead.google_rating || '?'} stars)`);
if (lead.top_reviewer_name) parts.push(`Recent reviewer: ${lead.top_reviewer_name}`);
if (lead.has_ssl === false) parts.push('No SSL certificate (browser shows Not Secure warning)');
if (lead.running_google_ads) parts.push('Running Google Ads (paying for traffic to a DIY site)');
if (lead.phone) parts.push(`Phone: ${lead.phone}`);

// Social context
if (lead.social_best_post) {
  const isJobPost = /(?:just |recently )?(finished|completed|done|wrapped|installed|fitted)|before.{0,10}after|happy (client|customer)|handed over|final result/i.test(lead.social_best_post);
  if (isJobPost) {
    parts.push(`Recent Facebook post about a job: "${lead.social_best_post}"`);
  }
}

parts.push(`\\nTRADE TERMS (use 1-2 naturally): ${tradeLingo.terms.join(', ') || 'none'}`);

let humourInstruction = '';
if (hasHumour) {
  const humourCta = HUMOUR_CTAS[nameHash % HUMOUR_CTAS.length];
  humourInstruction = `\\n\\nHUMOUR (one light line, in opener or CTA): "${humourCta}"`;
}

const userPrompt = `Write a DIY website upgrade email. Angle: ${variant.instruction}${humourInstruction}\\n\\nLEAD:\\n${parts.join('\\n')}\\n\\nRemember: ALWAYS use their first name. Focus on the DIY gap, not speed scores. Valid JSON only.`;

return {
  json: {
    ...lead,
    _variant_name: variant.name,
    _personalisation_type: 'diy_website',
    _has_humour: hasHumour,
    _trade_lingo_used: [category || 'generic'],
    _openai_body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: userPrompt },
      ],
      temperature: 0.8,
      max_tokens: 700,
    }),
  }
};"""

# ═══════════════════════════════════════════════════════════════
# PARSE EMAIL B — String() cast + tracking fields
# ═══════════════════════════════════════════════════════════════

PARSE_EMAIL_B = """// Parse OpenAI Response - Pipeline B (DIY Website)
const lead = $('Build Email Prompt B').item.json;
const response = $input.item.json;

let emailData = { subject: '', body: '', call_script: '' };

try {
  const content = response.choices?.[0]?.message?.content || '{}';
  const cleaned = content.replace(/```json\\n?/g, '').replace(/```\\n?/g, '').trim();
  emailData = JSON.parse(cleaned);
} catch {
  const raw = response.choices?.[0]?.message?.content || '';
  emailData = { subject: '[PARSE ERROR]', body: raw, call_script: '' };
}

function cleanText(text) {
  if (!text) return '';
  text = String(text);
  return text
    .replace(/\\u2014/g, ',')
    .replace(/\\u2013/g, '-')
    .replace(/\\s*[\\u2014\\u2013]\\s*/g, ', ')
    .replace(/Mycelium\\s*AI/gi, '')
    .replace(/\\|\\s*Mycelium[^|]*/gi, '')
    .replace(/\\s{2,}/g, ' ')
    .trim();
}

emailData.subject = cleanText(emailData.subject);
emailData.body = cleanText(emailData.body);
emailData.call_script = cleanText(emailData.call_script);

const whyParts = [];
if (lead.diy_platform) whyParts.push(lead.diy_platform);
if (lead.google_reviews >= 20) whyParts.push(`${lead.google_reviews} reviews`);
if (lead.running_google_ads) whyParts.push('running ads on DIY site');
if (lead.address_type === 'residential') whyParts.push('home-based');
if (lead._has_humour) whyParts.push('humour');
const whySummary = whyParts.length > 0 ? whyParts.join(', ') : 'standard lead';

return {
  json: {
    business_name: lead.business_name || '',
    phone: lead.phone || '',
    suburb: lead.suburb || '',
    category: lead.category || '',
    score: lead.score,
    why: `${lead.score}/10, ${whySummary}`,
    tier: lead.outreach_tier || (lead.score >= 7 ? 'priority_call' : 'email_only'),
    draft_subject: emailData.subject || '',
    draft_email: emailData.body || '',
    call_script: emailData.call_script || '',
    email: lead.email || '',
    email_variant: lead._variant_name || '',
    personalisation_type: lead._personalisation_type || 'diy_website',
    has_humour: lead._has_humour || false,
    trade_lingo_used: lead._trade_lingo_used || [],
    pipeline: 'diy_website',
    source: lead.source || 'google_maps',
    address_type: lead.address_type || '',
    google_reviews: lead.google_reviews,
    google_rating: lead.google_rating,
    website: lead.website || '',
    diy_platform: lead.diy_platform || '',
    running_google_ads: lead.running_google_ads,
    postcode: lead.postcode || '',
    address: lead.address || '',
    score_breakdown: lead.score_breakdown,
    place_id: lead.place_id,
    abn: lead.abn,
    facebook_url: lead.facebook_url || '',
  }
};"""

# ═══════════════════════════════════════════════════════════════
# UPDATE NODES
# ═══════════════════════════════════════════════════════════════

for node in wf['nodes']:
    if node['name'] == 'Build Email Prompt B':
        node['parameters']['jsCode'] = BUILD_PROMPT_B
        print('Updated Build Email Prompt B (DIY angle, first name, trade lingo, humour)')

    elif node['name'] == 'Parse Email B':
        node['parameters']['jsCode'] = PARSE_EMAIL_B
        print('Updated Parse Email B (String cast, tracking fields)')

    elif node['name'] == 'Build Email Prompt A':
        code = node['parameters']['jsCode']
        if 'ALWAYS address the person by their FIRST NAME' not in code:
            # Add first name rule to banned phrases
            code = code.replace(
                '"increasing" or "boosting" anything',
                '"increasing" or "boosting" anything\n'
                '- "Hi there" or "Hey" without a name\n\n'
                'FIRST NAME RULE:\n'
                '- ALWAYS address the person by their FIRST NAME in the greeting ("Hey Dave,")\n'
                '- If you have a first name, use it. No exceptions.\n'
                '- If no first name is available, use the business name ("Hey Dave\'s Plumbing,")\n'
                '- NEVER use "Hi there", "Hey there", or just "Hey" alone'
            )
            # Add first name extraction
            code = code.replace(
                "const parts = [`Business: ${lead.business_name}`];",
                "// Extract first name\n"
                "const contactName = lead.contact_name || lead.owner_name || '';\n"
                "const firstName = contactName ? contactName.split(' ')[0] : '';\n\n"
                "const parts = [`Business: ${lead.business_name}`];\n"
                "if (firstName) parts.push(`Owner first name: ${firstName}`);\n"
                "else parts.push('Owner first name: unknown (use business name in greeting)');"
            )
            node['parameters']['jsCode'] = code
            print('Updated Build Email Prompt A (first name rule added)')
        else:
            print('Build Email Prompt A already has first name rule')

# Push
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
