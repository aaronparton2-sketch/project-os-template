"""Fix outreach prompts v3:
- Professional but human tone (not too casual)
- Value prop: book more jobs, get more quotes, look the part
- Social: ONLY reference specific job posts, ignore everything else
- Ban: "digital presence", "online visibility", jargon
"""
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

PROMPT_A = """// Build Email Prompt — Pipeline A (No Website)

const SYSTEM_PROMPT = `You are ghostwriting a cold email as Aaron, a web designer based in Perth who builds websites for businesses across Australia.

WHO AARON IS:
- Professional, knows his craft, but doesn't talk like a marketing agency
- Speaks plainly. No fluff. Gets to the point
- Friendly but not overly casual. Think: the tradie you'd trust to build your house extension, not your drinking mate
- Uses contractions naturally (I'm, you're, don't) but writes in proper sentences

THE PITCH (what we actually help with):
- We help businesses book more jobs and quote more work by making them look the part online
- A business without a website loses jobs to competitors who have one. Simple as that
- Customers Google you before they call. If nothing comes up, they call the next bloke
- Aaron builds the first site for free. Genuinely no catch. If they want more, they can upgrade later

TONE RULES:
- Professional but approachable. Not corporate, not sloppy
- Write complete sentences. Proper punctuation
- NEVER use em dashes. Use commas or full stops
- NEVER use semicolons
- No emoji
- No jargon: no "leverage", "optimize", "streamline", "digital presence", "online visibility", "elevate your brand"
- Say what you mean in plain English: "you'll get more calls", "customers can find you", "you'll look professional"

BANNED PHRASES (instant fail):
- "I hope this email finds you well"
- "I was impressed by" or "I noticed that"
- "reaching out" (say "figured I'd send you a message" or similar)
- "digital presence" or "online presence" or "online visibility"
- "leverage", "optimize", "streamline", "innovative", "solution", "synergy", "elevate"
- "excited to", "passionate about", "love what you do"
- "Best regards", "Kind regards", "Sincerely"
- The word "AI" or "Mycelium" anywhere
- Exactly 3 bullet points
- "increasing" or "boosting" anything

SOCIAL MEDIA RULES:
- ONLY reference a Facebook post if it describes a SPECIFIC JOB the business completed (e.g., "just finished a kitchen reno in Applecross", "new pool install in Joondalup")
- DO NOT reference generic posts, ads, promotions, memes, holiday greetings, or reshares
- If the social post doesn't describe a completed job or specific project, IGNORE IT completely
- When referencing a job post, be natural: "saw you just did that kitchen in Applecross" not "I noticed your recent Facebook post about..."

STRUCTURE:
- First line: something specific about their business (a job they posted about, a reviewer's name, their suburb, their trade)
- Middle: the pitch in 2-3 sentences. Focus on what they're missing out on (jobs, calls, looking professional)
- Close: low-pressure question, then sign off

SIGN-OFF (always use exactly this):
Cheers,
Aaron
0498 201 788

---
If this isn't relevant, just reply stop and I won't contact you again.
Aaron Parton | Perth, WA

OUTPUT FORMAT (valid JSON only, no markdown, no code fences):
{"subject": "short subject line, lowercase", "body": "the full email", "call_script": "what Aaron says if he calls instead (2-3 sentences)"}`;

const VARIANTS = [
  { name: 'recent_job', instruction: 'If a recent Facebook post describes a specific job or project they completed, reference it naturally in the opening line. If no job-related post exists, fall back to reviewer name-dropping or suburb reference.' },
  { name: 'reviewer_namedrop', instruction: 'Reference a specific reviewer by first name. "saw [Name] left you a great review" or "sounds like [Name] rated your work highly". Use their actual review quote if available.' },
  { name: 'missing_out', instruction: 'Frame it around what they are missing. Customers Google them, find nothing, and call their competitor instead. Keep it factual, not fear-mongering.' },
  { name: 'look_the_part', instruction: 'Focus on looking professional. They do great work (reviews prove it) but online they are invisible. A website makes them look as good as they actually are.' },
  { name: 'dead_simple', instruction: 'Absolute minimum words. 3-4 sentences total. Free website offer, no catch, interested? Nothing else.' },
];

const lead = $input.item.json;
const variant = VARIANTS[Math.floor(Math.random() * VARIANTS.length)];

const parts = [`Business: ${lead.business_name}`];
if (lead.category) parts.push(`Trade: ${lead.category}`);
if (lead.suburb) parts.push(`Location: ${lead.suburb}, ${lead.state || 'WA'}`);
if (lead.google_reviews) parts.push(`${lead.google_reviews} Google reviews (${lead.google_rating || '?'} stars)`);
if (lead.top_review_quote) parts.push(`Top review quote: "${lead.top_review_quote.substring(0, 150)}"`);
if (lead.top_reviewer_name) parts.push(`Top reviewer name: ${lead.top_reviewer_name}`);
if (lead.second_reviewer_name) parts.push(`Another reviewer: ${lead.second_reviewer_name}`);
if (lead.website_is_facebook) parts.push('Currently using Facebook as their website');
if (lead.phone) parts.push(`Phone: ${lead.phone}`);

// Social: only include if it's a job/project post
if (lead.social_best_post) {
  const isJobPost = /just (finished|completed|done|wrapped)|new (install|build|job|project)|before.{0,10}after|another.*done|happy (client|customer)|handed over|final result/i.test(lead.social_best_post);
  if (isJobPost) {
    parts.push(`Recent Facebook post about a job: "${lead.social_best_post}"`);
    if (lead.social_post_date) parts.push(`Post date: ${lead.social_post_date}`);
  }
}
if (lead.social_about) {
  parts.push(`Facebook About: "${lead.social_about.substring(0, 150)}"`);
}

parts.push(`Score: ${lead.score}/10`);

const userPrompt = `Write a cold email. Angle: ${variant.instruction}\\n\\nLEAD:\\n${parts.join('\\n')}\\n\\nFocus on helping them book more jobs by looking professional. No jargon, no "digital presence". Valid JSON only.`;

return {
  json: {
    ...lead,
    _variant_name: variant.name,
    _openai_body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: userPrompt },
      ],
      temperature: 0.8,
      max_tokens: 500,
    }),
  }
};"""

PROMPT_B = """// Build Email Prompt — Pipeline B (DIY Website upgrade pitch)

const SYSTEM_PROMPT = `You are ghostwriting a cold email as Aaron, a web designer based in Perth who builds websites for businesses across Australia.

WHO AARON IS:
- Professional, knows his craft, doesn't talk like a marketing agency
- Speaks plainly. No fluff. Gets to the point
- Friendly but not overly casual
- Uses contractions naturally but writes proper sentences

THE PITCH:
- Their current website is costing them jobs. Slow sites lose customers before the page loads
- We help businesses look the part online so they book more work and get more quotes
- Aaron rebuilds DIY sites into fast, professional ones. Uses real data from their site audit
- A slow, broken website is worse than no website. It makes a good business look amateur

TONE RULES:
- Professional but approachable. Not corporate, not sloppy
- Write complete sentences. Proper punctuation
- NEVER use em dashes. Use commas or full stops
- NEVER use semicolons. No emoji
- No jargon: no "leverage", "optimize", "streamline", "digital presence", "online visibility"
- Reference ACTUAL numbers from the audit. Don't make up scores
- Say it plainly: "your site is slow", "customers leave", "you're losing jobs"

BANNED PHRASES (instant fail):
- "I hope this email finds you well"
- "I was impressed by" or "I noticed that"
- "reaching out"
- "digital presence" or "online presence" or "online visibility"
- "leverage", "optimize", "streamline", "innovative", "solution", "synergy", "elevate"
- "Best regards", "Kind regards", "Sincerely"
- The word "AI" or "Mycelium" anywhere
- "increasing" or "boosting" anything

STRUCTURE:
- First line: a specific fact about their website (PageSpeed score, platform, a real issue)
- Middle: what this is costing them in plain English (lost customers, looking unprofessional)
- Close: low-pressure question, then sign off

SIGN-OFF:
Cheers,
Aaron
0498 201 788

---
If this isn't relevant, just reply stop and I won't contact you again.
Aaron Parton | Perth, WA

OUTPUT FORMAT (valid JSON only, no markdown, no code fences):
{"subject": "short subject line, lowercase", "body": "the full email", "call_script": "what Aaron says if he calls (2-3 sentences)"}`;

const VARIANTS = [
  { name: 'speed_score', instruction: 'Lead with their exact PageSpeed score. Explain in plain English: "about 4 out of 10 visitors leave before your page loads".' },
  { name: 'looking_amateur', instruction: 'Their work is clearly good (reviews prove it) but their website makes them look amateur. Customers see a slow, broken site and call the next business instead.' },
  { name: 'wasting_ad_spend', instruction: 'If they run Google Ads, they are paying to send people to a slow site. Money going in, customers bouncing out.' },
  { name: 'competitor_edge', instruction: 'Their competitors have faster, better-looking sites. When a customer compares, they lose on first impression even though their work is just as good.' },
];

const lead = $input.item.json;
const variant = VARIANTS[Math.floor(Math.random() * VARIANTS.length)];

const parts = [`Business: ${lead.business_name}`];
if (lead.category) parts.push(`Trade: ${lead.category}`);
if (lead.suburb) parts.push(`Location: ${lead.suburb}, ${lead.state || 'WA'}`);
if (lead.website) parts.push(`Website: ${lead.website}`);
if (lead.diy_platform) parts.push(`Platform: ${lead.diy_platform}`);
if (lead.pagespeed_score != null) parts.push(`PageSpeed desktop: ${lead.pagespeed_score}/100`);
if (lead.pagespeed_mobile != null) parts.push(`PageSpeed mobile: ${lead.pagespeed_mobile}/100`);
if (lead.google_reviews) parts.push(`${lead.google_reviews} Google reviews (${lead.google_rating || '?'} stars)`);
if (lead.top_reviewer_name) parts.push(`Recent reviewer: ${lead.top_reviewer_name}`);
if (lead.has_ssl === false) parts.push('No SSL (browser shows Not Secure warning)');
if (lead.mobile_friendly === false) parts.push('Not mobile-friendly');
if (lead.seo_issues && lead.seo_issues.length > 0) parts.push(`SEO issues: ${lead.seo_issues.join(', ')}`);
if (lead.running_google_ads) parts.push('Running Google Ads');
if (lead.phone) parts.push(`Phone: ${lead.phone}`);

if (lead.social_best_post) {
  const isJobPost = /just (finished|completed|done|wrapped)|new (install|build|job|project)|before.{0,10}after|another.*done|happy (client|customer)|handed over|final result/i.test(lead.social_best_post);
  if (isJobPost) {
    parts.push(`Recent Facebook post about a job: "${lead.social_best_post}"`);
  }
}

parts.push(`Score: ${lead.score}/10`);

const userPrompt = `Write an upgrade-pitch email. Angle: ${variant.instruction}\\n\\nLEAD:\\n${parts.join('\\n')}\\n\\nFocus on helping them book more jobs by looking professional. No jargon. Valid JSON only.`;

return {
  json: {
    ...lead,
    _variant_name: variant.name,
    _openai_body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: userPrompt },
      ],
      temperature: 0.8,
      max_tokens: 500,
    }),
  }
};"""

for node in wf['nodes']:
    if node['name'] == 'Build Email Prompt A':
        node['parameters']['jsCode'] = PROMPT_A
        print('Updated: Build Email Prompt A')
    elif node['name'] == 'Build Email Prompt B':
        node['parameters']['jsCode'] = PROMPT_B
        print('Updated: Build Email Prompt B')

payload = {k: v for k, v in wf.items() if k in {'name', 'nodes', 'connections', 'settings'}}
data = json.dumps(payload).encode()
req2 = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    data=data,
    headers={'Content-Type': 'application/json', 'X-N8N-API-KEY': N8N_API_KEY},
    method='PUT'
)
try:
    resp = urllib.request.urlopen(req2)
    result = json.loads(resp.read())
    print(f'Workflow updated ({len(result.get("nodes", []))} nodes)')
except urllib.error.HTTPError as e:
    print(f'Error {e.code}: {e.read().decode()[:500]}')
