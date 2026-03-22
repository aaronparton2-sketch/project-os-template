"""Improve outreach quality:
1. Ban em dashes from output (OpenAI loves them)
2. Remove "Mycelium AI" — just Aaron, no AI mention
3. Extract reviewer names from Google Maps data for name-dropping
4. Better anti-slop rules for genuine human tone
5. Post-process: strip any remaining em dashes from output
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

# ═══════════════════════════════════════════════════════════════
# Fix 1: Filter & Normalise — extract reviewer names + dates
# ═══════════════════════════════════════════════════════════════

for node in wf['nodes']:
    if node['name'] == 'Filter & Normalise':
        code = node['parameters']['jsCode']
        # Replace the review extraction to include reviewer name
        old_review = """  const reviewText = (d.reviews && d.reviews[0] && d.reviews[0].text)
    ? d.reviews[0].text.substring(0, 200) : '';"""
        new_review = """  // Extract review data — text, reviewer name, date
  const reviews = d.reviews || [];
  const topReview = reviews[0] || {};
  const reviewText = (topReview.text || '').substring(0, 200);
  const reviewerName = (topReview.name || topReview.author || '').trim();
  const reviewDate = topReview.publishedAtDate || topReview.publishAt || '';
  // Get a second review for variety
  const secondReview = reviews[1] || {};
  const secondReviewerName = (secondReview.name || secondReview.author || '').trim();
  const secondReviewText = (secondReview.text || '').substring(0, 150);"""

        code = code.replace(old_review, new_review)

        # Add reviewer fields to the output
        old_output = "      top_review_quote: reviewText,"
        new_output = """      top_review_quote: reviewText,
      top_reviewer_name: reviewerName,
      top_review_date: reviewDate,
      second_reviewer_name: secondReviewerName,
      second_review_quote: secondReviewText,"""

        code = code.replace(old_output, new_output)
        node['parameters']['jsCode'] = code
        print('Fixed: Filter & Normalise (reviewer names)')

    # Do the same for Filter & Normalise (Has Website)
    if node['name'] == 'Filter & Normalise (Has Website)':
        code = node['parameters']['jsCode']
        if 'reviewerName' not in code and 'reviews' in code.lower():
            code = code.replace(
                "  const reviewText = (d.reviews && d.reviews[0] && d.reviews[0].text)\n    ? d.reviews[0].text.substring(0, 200) : '';",
                """  const reviews = d.reviews || [];
  const topReview = reviews[0] || {};
  const reviewText = (topReview.text || '').substring(0, 200);
  const reviewerName = (topReview.name || topReview.author || '').trim();
  const reviewDate = topReview.publishedAtDate || topReview.publishAt || '';
  const secondReview = reviews[1] || {};
  const secondReviewerName = (secondReview.name || secondReview.author || '').trim();
  const secondReviewText = (secondReview.text || '').substring(0, 150);"""
            )
            if 'top_review_quote: reviewText,' in code:
                code = code.replace(
                    "      top_review_quote: reviewText,",
                    """      top_review_quote: reviewText,
      top_reviewer_name: reviewerName,
      top_review_date: reviewDate,
      second_reviewer_name: secondReviewerName,
      second_review_quote: secondReviewText,"""
                )
            node['parameters']['jsCode'] = code
            print('Fixed: Filter & Normalise (Has Website) (reviewer names)')

# ═══════════════════════════════════════════════════════════════
# Fix 2: Build Email Prompt A — better system prompt
# ═══════════════════════════════════════════════════════════════

PROMPT_A_CODE = r"""// Build Email Prompt — Pipeline A (No Website)
// Fast: no HTTP calls. Builds prompt with anti-slop framework.

const SYSTEM_PROMPT = `You are ghostwriting a cold email as Aaron, a web designer based in Perth who works with businesses across Australia. Aaron is a real person, not a company, not an agency. He texts like a normal bloke.

VOICE:
- Write exactly how a 28-year-old Aussie bloke would text a business owner he found online
- Short sentences. Some fragments. Like this.
- Use contractions always (I'm, you're, don't, it's, can't, won't)
- Typos are fine. Imperfect grammar is fine. Real humans don't proofread cold emails
- NEVER use em dashes. Use commas, full stops, or just start a new sentence
- NEVER use semicolons
- One thought per sentence. Don't chain ideas with dashes or colons

STRUCTURE:
- First line: something SPECIFIC about their business that proves you actually looked. Use a reviewer's first name, a specific review quote, their suburb, their trade, something concrete
- Middle: the pitch in 2-3 sentences. Keep it dead simple
- End: low-pressure CTA then "Cheers, Aaron" and his number

BANNED (instant fail if you use any):
- "I hope this email finds you well"
- "I was impressed by" or "I was blown away"
- "Please don't hesitate"
- "I noticed that" (too corporate - just state what you noticed)
- "leverage", "optimize", "streamline", "innovative", "solution", "synergy", "elevate"
- "reaching out" (say "figured I'd send you a message" or similar)
- "excited to", "passionate about", "love what you do"
- Em dashes (the long dash). Use a comma or full stop instead
- "Best regards", "Kind regards", "Sincerely"
- Exactly 3 bullet points
- The word "AI" or "Mycelium" anywhere

REQUIRED:
- Include one honest/self-deprecating bit: "might be a stretch", "figured I'd ask", "no worries if not", "bit random I know"
- End with: Cheers,\nAaron\n0498 201 788
- CTA must be casual: "interested?", "worth a look?", "want me to have a crack?"
- If you have a reviewer's name, work it in naturally: "saw [Name]'s review", "sounds like [Name] had a good experience"

EMAIL FOOTER (always include after sign-off):
---
If this isn't relevant, just reply stop and I won't contact you again.
Aaron Parton | Perth, WA

OUTPUT FORMAT (valid JSON only, no markdown, no code fences):
{"subject": "short subject line, lowercase, no clickbait", "body": "the full email body", "call_script": "what Aaron says if he calls instead (2-3 sentences, super casual)"}`;

const VARIANTS = [
  { name: 'reviewer_namedrop', instruction: 'If a reviewer name is available, mention them by first name as if you know them or came across them. "saw [Name] left you a great review" or "sounds like [Name] was stoked with your work". If no reviewer name, fall back to referencing their review count.' },
  { name: 'suburb_local', instruction: 'Reference their specific suburb and make it local. "saw you guys are in [suburb]" or "found you in [suburb]". Talk about the area like you know it.' },
  { name: 'dead_simple', instruction: 'Absolute minimum words. 3-4 sentences total. The pitch is just: no website, I will build you one for free, interested? Nothing else.' },
  { name: 'free_offer_upfront', instruction: 'First sentence is the offer. "I will build [business] a free website, genuinely no catch." Then 1-2 sentences of context. Then CTA.' },
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
if (lead.second_review_quote) parts.push(`Their review: "${lead.second_review_quote}"`);
if (lead.website_is_facebook) parts.push('Currently using Facebook as their website');
if (lead.phone) parts.push(`Phone: ${lead.phone}`);
parts.push(`Score: ${lead.score}/10`);

const userPrompt = `Write a cold email. Angle: ${variant.instruction}\n\nLEAD:\n${parts.join('\n')}\n\nRemember: no em dashes, no AI mentions, sound like a real person. Output valid JSON only.`;

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
      temperature: 0.85,
      max_tokens: 500,
    }),
  }
};"""

# ═══════════════════════════════════════════════════════════════
# Fix 3: Build Email Prompt B — better system prompt
# ═══════════════════════════════════════════════════════════════

PROMPT_B_CODE = r"""// Build Email Prompt — Pipeline B (DIY Website upgrade pitch)
// Fast: no HTTP calls. Builds prompt with anti-slop framework.

const SYSTEM_PROMPT = `You are ghostwriting a cold email as Aaron, a web designer based in Perth who works with businesses across Australia. Aaron is a real person, not a company. He texts like a normal bloke.

VOICE:
- Write exactly how a 28-year-old Aussie bloke would text a business owner he found online
- Short sentences. Some fragments. Like this.
- Use contractions always (I'm, you're, don't, it's, can't, won't)
- Typos are fine. Imperfect grammar is fine. Real humans don't proofread cold emails
- NEVER use em dashes. Use commas, full stops, or just start a new sentence
- NEVER use semicolons
- One thought per sentence

STRUCTURE:
- First line: something SPECIFIC about their website issue that proves you actually checked. Their PageSpeed score, their platform, a specific problem
- Middle: what this is costing them in plain english (not jargon)
- End: low-pressure CTA then "Cheers, Aaron" and his number

BANNED (instant fail):
- "I hope this email finds you well"
- "I was impressed by" or "I was blown away"
- "Please don't hesitate"
- "I noticed that" (just state what you noticed)
- "leverage", "optimize", "streamline", "innovative", "solution", "synergy", "elevate"
- "reaching out" (say "figured I'd send you a message" or similar)
- "excited to", "passionate about", "love what you do"
- Em dashes. Use comma or full stop instead
- "Best regards", "Kind regards", "Sincerely"
- Exactly 3 bullet points
- The word "AI" or "Mycelium" anywhere

REQUIRED:
- Include one honest bit: "might be a stretch", "figured I'd ask", "no worries if not"
- End with: Cheers,\nAaron\n0498 201 788
- CTA: "interested?", "worth a look?", "want me to show you what it'd look like?"
- Reference ACTUAL numbers from the audit. Don't make up PageSpeed scores

EMAIL FOOTER:
---
If this isn't relevant, just reply stop and I won't contact you again.
Aaron Parton | Perth, WA

OUTPUT FORMAT (valid JSON only, no markdown, no code fences):
{"subject": "short subject, lowercase, references their specific issue", "body": "full email body with real audit data", "call_script": "what Aaron says if he calls (2-3 sentences, casual, references the audit)"}`;

const VARIANTS = [
  { name: 'speed_score', instruction: 'Lead with their exact PageSpeed score. "your site scored X out of 100 on Google speed test". Make it tangible, not jargony.' },
  { name: 'mobile_issue', instruction: 'Focus on mobile. Most customers search on phones. Reference their mobile score if available.' },
  { name: 'competitor_compare', instruction: 'Their competitors have faster sites. Frame as falling behind, not a scare tactic.' },
  { name: 'money_loss', instruction: 'Frame as money lost. "about 40% of people leave before your page loads". If running Google Ads, mention ad spend being wasted on a slow site.' },
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
if (lead.has_ssl === false) parts.push('No SSL (browser shows "Not Secure")');
if (lead.mobile_friendly === false) parts.push('Not mobile-friendly');
if (lead.seo_issues && lead.seo_issues.length > 0) parts.push(`SEO issues: ${lead.seo_issues.join(', ')}`);
if (lead.running_google_ads) parts.push('Running Google Ads');
if (lead.phone) parts.push(`Phone: ${lead.phone}`);
parts.push(`Score: ${lead.score}/10`);

const userPrompt = `Write an upgrade-pitch email. Angle: ${variant.instruction}\n\nLEAD:\n${parts.join('\n')}\n\nNo em dashes, no AI mentions, sound human. Valid JSON only.`;

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
      temperature: 0.85,
      max_tokens: 500,
    }),
  }
};"""

# ═══════════════════════════════════════════════════════════════
# Fix 4: Parse nodes — strip em dashes from output
# ═══════════════════════════════════════════════════════════════

PARSE_A_CODE = r"""// Parse OpenAI Response — Pipeline A
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

// Post-process: strip em dashes, en dashes, and "Mycelium AI" references
function cleanText(text) {
  if (!text) return '';
  return text
    .replace(/\u2014/g, ',')   // em dash to comma
    .replace(/\u2013/g, '-')   // en dash to hyphen
    .replace(/\s*[—–]\s*/g, ', ')  // any remaining dashes
    .replace(/Mycelium\s*AI/gi, '')
    .replace(/\|\s*Mycelium[^|]*/gi, '')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

emailData.subject = cleanText(emailData.subject);
emailData.body = cleanText(emailData.body);
emailData.call_script = cleanText(emailData.call_script);

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
    why: `${lead.score}/10, ${whySummary}`,
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
    top_reviewer_name: lead.top_reviewer_name,
    found_on_sources: lead.found_on_sources,
    place_id: lead.place_id,
    abn: lead.abn,
  }
};"""

PARSE_B_CODE = r"""// Parse OpenAI Response — Pipeline B
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

function cleanText(text) {
  if (!text) return '';
  return text
    .replace(/\u2014/g, ',')
    .replace(/\u2013/g, '-')
    .replace(/\s*[—–]\s*/g, ', ')
    .replace(/Mycelium\s*AI/gi, '')
    .replace(/\|\s*Mycelium[^|]*/gi, '')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

emailData.subject = cleanText(emailData.subject);
emailData.body = cleanText(emailData.body);
emailData.call_script = cleanText(emailData.call_script);

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
    why: `${lead.score}/10, ${whySummary}`,
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

# ═══════════════════════════════════════════════════════════════
# Apply all fixes
# ═══════════════════════════════════════════════════════════════

for node in wf['nodes']:
    name = node['name']
    if name == 'Build Email Prompt A':
        node['parameters']['jsCode'] = PROMPT_A_CODE
        print('Fixed: Build Email Prompt A (new anti-slop prompt, reviewer names)')
    elif name == 'Build Email Prompt B':
        node['parameters']['jsCode'] = PROMPT_B_CODE
        print('Fixed: Build Email Prompt B (new anti-slop prompt)')
    elif name == 'Parse Email A':
        node['parameters']['jsCode'] = PARSE_A_CODE
        print('Fixed: Parse Email A (em dash strip, no Mycelium)')
    elif name == 'Parse Email B':
        node['parameters']['jsCode'] = PARSE_B_CODE
        print('Fixed: Parse Email B (em dash strip, no Mycelium)')

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
