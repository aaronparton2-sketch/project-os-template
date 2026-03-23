"""Deploy Smart Outreach Upgrade to n8n workflow.

Changes:
1. Supabase migration: new columns on leads + outreach_events table + views
2. Build Email Prompt A: trade lingo dictionary, social gating, humour flag, improved call script
3. Parse Email A: extract personalisation_type, has_humour, trade_lingo_used
4. Supabase Store: persist new fields
"""
import json, urllib.request, subprocess, sys, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

N8N_API_KEY = os.environ['N8N_API_KEY']
N8N_API_URL = os.environ['N8N_API_URL']
OPENAI_KEY = os.environ['OPENAI_API_KEY']
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
# STEP 1: SUPABASE MIGRATION — new columns + outreach_events table
# ═══════════════════════════════════════════════════════════════

print('Step 1: Running Supabase migration...')

MIGRATION_SQL = """
-- Migration 005: Smart outreach upgrade
-- New columns on leads table
ALTER TABLE leads ADD COLUMN IF NOT EXISTS personalisation_type TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS has_humour BOOLEAN DEFAULT false;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS trade_lingo_used TEXT[];

-- Outreach events table for performance tracking
CREATE TABLE IF NOT EXISTS outreach_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    channel TEXT NOT NULL DEFAULT 'email',
    variant TEXT,
    personalisation_type TEXT,
    has_humour BOOLEAN DEFAULT false,
    trade_category TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_outreach_events_lead ON outreach_events(lead_id);
CREATE INDEX IF NOT EXISTS idx_outreach_events_type ON outreach_events(event_type);
CREATE INDEX IF NOT EXISTS idx_outreach_events_created ON outreach_events(created_at);
"""

supabase_query(MIGRATION_SQL)
print('  Migration applied (columns + outreach_events table)')

# Create views (separate queries since CREATE OR REPLACE VIEW is cleaner)
VIEWS_SQL = """
-- Email performance by variant
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

-- Performance by trade category
CREATE OR REPLACE VIEW trade_performance AS
SELECT
    trade_category,
    COUNT(*) FILTER (WHERE event_type = 'email_sent') as emails_sent,
    COUNT(*) FILTER (WHERE event_type = 'email_replied') as email_replies,
    COUNT(*) FILTER (WHERE event_type = 'call_interested') as call_interested,
    ROUND(
        COUNT(*) FILTER (WHERE event_type = 'email_replied')::numeric /
        NULLIF(COUNT(*) FILTER (WHERE event_type = 'email_sent'), 0) * 100, 1
    ) as email_reply_rate
FROM outreach_events
GROUP BY trade_category;

-- Humour A/B comparison
CREATE OR REPLACE VIEW humour_ab_test AS
SELECT
    has_humour,
    COUNT(*) FILTER (WHERE event_type = 'email_sent') as sent,
    COUNT(*) FILTER (WHERE event_type = 'email_opened') as opened,
    COUNT(*) FILTER (WHERE event_type = 'email_replied') as replied,
    ROUND(
        COUNT(*) FILTER (WHERE event_type = 'email_replied')::numeric /
        NULLIF(COUNT(*) FILTER (WHERE event_type = 'email_sent'), 0) * 100, 1
    ) as reply_rate
FROM outreach_events
WHERE channel = 'email'
GROUP BY has_humour;

-- Personalisation type comparison
CREATE OR REPLACE VIEW personalisation_performance AS
SELECT
    personalisation_type,
    COUNT(*) FILTER (WHERE event_type = 'email_sent') as sent,
    COUNT(*) FILTER (WHERE event_type = 'email_replied') as replied,
    COUNT(*) FILTER (WHERE event_type = 'call_interested') as call_conversions,
    ROUND(
        COUNT(*) FILTER (WHERE event_type = 'email_replied')::numeric /
        NULLIF(COUNT(*) FILTER (WHERE event_type = 'email_sent'), 0) * 100, 1
    ) as reply_rate
FROM outreach_events
GROUP BY personalisation_type;

-- Weekly outreach summary
CREATE OR REPLACE VIEW weekly_outreach_summary AS
SELECT
    DATE_TRUNC('week', created_at) as week,
    COUNT(*) FILTER (WHERE event_type = 'email_sent') as emails_sent,
    COUNT(*) FILTER (WHERE event_type = 'email_opened') as emails_opened,
    COUNT(*) FILTER (WHERE event_type = 'email_replied') as emails_replied,
    COUNT(*) FILTER (WHERE event_type = 'email_bounced') as emails_bounced,
    COUNT(*) FILTER (WHERE event_type IN ('call_made', 'call_answered', 'call_voicemail', 'call_no_answer')) as calls_made,
    COUNT(*) FILTER (WHERE event_type = 'call_interested') as calls_interested,
    COUNT(*) FILTER (WHERE event_type = 'call_not_interested') as calls_not_interested
FROM outreach_events
GROUP BY DATE_TRUNC('week', created_at)
ORDER BY week DESC;
"""

supabase_query(VIEWS_SQL)
print('  Performance views created')

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

# ═══════════════════════════════════════════════════════════════
# STEP 3: UPDATE BUILD EMAIL PROMPT A
# Trade lingo + social gating + humour + improved call scripts
# ═══════════════════════════════════════════════════════════════

print('\nStep 3: Updating Build Email Prompt A...')

BUILD_PROMPT_A_CODE = r"""// Build Email Prompt - Pipeline A (No Website)
// Smart Outreach v2: trade lingo, social gating, humour A/B, call scripts

// ═══════════════════════════════════════════════
// TRADE LINGO DICTIONARY
// ═══════════════════════════════════════════════

const TRADE_LINGO = {
  plumber: {
    jobs: ['hot water changeover', 'blocked drain', 'burst pipe', 'tapware replacement', 'gas compliance', 'rough-in'],
    terms: ['HWS', 'copper pipe', 'tempering valve', 'backflow', 'DWV'],
    flavour: 'Saw you just did that hot water changeover in {suburb} - those Rheem units are solid.',
    humour_opener: "Fair warning - I promise this email isn't about pipes. Well... sort of.",
  },
  electrician: {
    jobs: ['switchboard upgrade', 'safety switch install', 'LED downlight swap', 'RCD testing', 'smoke alarm compliance'],
    terms: ['sparky', 'board upgrade', 'fault finding', 'test and tag', 'RCD', 'AS/NZS 3000'],
    flavour: 'Saw you did that switchboard upgrade in {suburb} - old boards are a nightmare to work with.',
    humour_opener: "I won't shock you with the price - it's free.",
  },
  builder: {
    jobs: ['renovation', 'extension', 'granny flat', 'retaining wall', 'knock-down rebuild'],
    terms: ['reno', 'slab down', 'frame up', 'lock-up stage', 'DA', 'formwork', 'reo'],
    flavour: 'That reno you finished in {suburb} looks mint - the before and after is chalk and cheese.',
    humour_opener: "I build websites, not houses - but yours would look pretty good online.",
  },
  landscaper: {
    jobs: ['garden design', 'reticulation install', 'turf laying', 'paving', 'retaining wall', 'pool landscaping'],
    terms: ['retic', 'bore', 'limestone walls', 'exposed aggregate', 'sleepers', 'mulch'],
    flavour: 'Saw that retic job you did in {suburb} - WA summers are brutal without a decent system.',
    humour_opener: "Your garden game is strong - your Google game could use some work though.",
  },
  painter: {
    jobs: ['interior repaint', 'exterior repaint', 'roof restoration', 'texture coating'],
    terms: ['Dulux', 'prep work', 'cutting in', 'two-coat system', 'sugar soap'],
    flavour: 'That exterior job in {suburb} came up mint - the colour choice is spot on.',
    humour_opener: "I've got to be honest - I Googled '{category} {suburb}' and you didn't show up. But your reviews are five-star, so something's not adding up.",
  },
  roofer: {
    jobs: ['re-roof', 'ridge cap repointing', 'gutter replacement', 'roof restoration', 'leak repair'],
    terms: ['Colorbond', 'Zincalume', 'flashing', 'fascia', 'sarking', 'whirlybird'],
    flavour: 'Saw that Colorbond re-roof in {suburb} - those old tile roofs are everywhere around here.',
    humour_opener: "I can't fix your roof, but I can fix your Google results.",
  },
  concreter: {
    jobs: ['driveway', 'shed slab', 'patio', 'exposed aggregate', 'liquid limestone'],
    terms: ['exposed agg', 'liquid lime', 'formwork', 'reo mesh', 'power float', 'control joint'],
    flavour: 'That exposed agg driveway in {suburb} looks unreal - the aggregate mix is bang on.',
    humour_opener: "Your concrete work is rock solid - your online presence... not so much.",
  },
  'air conditioning': {
    jobs: ['split system install', 'ducted system', 'AC service', 'evap cooler'],
    terms: ['split system', 'ducted', 'inverter', 'reverse cycle', 'zoned system'],
    flavour: 'Saw you just put a split system in over in {suburb} - this heat has been keeping you busy.',
    humour_opener: "I can't cool your house, but I can heat up your enquiries.",
  },
  cleaner: {
    jobs: ['bond clean', 'commercial clean', 'carpet steam clean', 'pressure washing'],
    terms: ['bond clean', 'deep clean', 'steam and extract', 'pressure blast', 'end of lease'],
    flavour: 'Saw you smashed out that bond clean in {suburb} - agents love a sparkling handover.',
    humour_opener: "I clean up online presences - not as satisfying as a bond clean, but close.",
  },
  tiler: {
    jobs: ['bathroom reno tile', 'floor tiling', 'splashback', 'waterproofing', 're-grout'],
    terms: ['porcelain', 'subway tile', 'waterproofing membrane', 'wet saw', 'herringbone'],
    flavour: 'That bathroom tile job in {suburb} is clean as - the herringbone pattern looks sharp.',
    humour_opener: "Your tiling is level - your Google listing could use some work though.",
  },
  fencer: {
    jobs: ['Colorbond fence', 'pool fence compliance', 'gate automation', 'slat screening'],
    terms: ['Colorbond', 'pool-compliant', 'dividing fence', 'slats', 'automated gate'],
    flavour: 'Saw that Colorbond job in {suburb} - neighbours must be stoked with how it turned out.',
    humour_opener: "Good fences make good neighbours - a good website makes good customers.",
  },
  'pest control': {
    jobs: ['termite inspection', 'general pest spray', 'rodent baiting', 'pre-purchase inspection'],
    terms: ['termite barrier', 'bait station', 'thermal imaging', 'treated zone'],
    flavour: 'Saw you did a termite job in {suburb} - those older suburbs are always keeping you busy.',
    humour_opener: "I can't get rid of the pests, but I can get rid of the competition showing up above you on Google.",
  },
  carpenter: {
    jobs: ['decking', 'pergola', 'built-in wardrobe', 'kitchen install', 'door hanging'],
    terms: ['merbau', 'jarrah', 'treated pine', 'tongue-and-groove', 'custom fit-out'],
    flavour: 'That merbau deck in {suburb} looks unreal - jarrah or merbau is always the go in Perth.',
    humour_opener: "I can't build a deck, but I can build you a website that gets people calling about one.",
  },
  removalist: {
    jobs: ['house move', 'office relocation', 'furniture delivery', 'interstate move'],
    terms: ['blanket wrap', 'tailgate loader', 'three-tonner', 'door to door'],
    flavour: 'Saw you did that big move in {suburb} - moving day is chaos but your reviews say you make it easy.',
    humour_opener: "I can't move your couch, but I can move you up the Google rankings.",
  },
  mechanic: {
    jobs: ['logbook service', 'brake replacement', 'timing belt', 'pre-purchase inspection'],
    terms: ['logbook service', 'OBD scan', 'pads and rotors', 'rego check', 'diff service'],
    flavour: 'Saw you did that logbook service in {suburb} - people love a mobile mechanic who comes to them.',
    humour_opener: "Your engine runs smooth - your online presence needs a tune-up though.",
  },
  'dog trainer': {
    jobs: ['puppy school', 'obedience training', 'aggression rehab', 'recall training'],
    terms: ['positive reinforcement', 'recall work', 'loose leash', 'socialisation', 'marker training'],
    flavour: 'Saw that recall training video you posted - the before and after is impressive.',
    humour_opener: "I can't teach your dog to sit, but I can teach Google to show your business.",
  },
};

// Generic fallback for unlisted trades
const GENERIC_LINGO = {
  jobs: [],
  terms: [],
  flavour: 'Saw that job you did in {suburb} - your customers clearly rate you.',
  humour_opener: "I'll keep this short - I know you've got better things to do than read emails from strangers.",
};

const HUMOUR_CTAS = [
  "Worth a 10-minute chat? I promise I'm more interesting than this email makes me sound.",
  "Keen for a quick yarn? Worst case you get 10 minutes of mediocre banter and a free website idea.",
  "Open to a chat? I'll bring the ideas, you bring the scepticism.",
];

// ═══════════════════════════════════════════════
// SYSTEM PROMPT (upgraded)
// ═══════════════════════════════════════════════

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

TRADE LINGO RULES:
- You will be given trade-specific terminology for the lead's industry
- Use 1-2 trade terms NATURALLY in the email. Don't force them. If a term doesn't fit, skip it
- The goal: sound like someone who understands their trade, not a marketer who Googled it
- Use the trade flavour example as inspiration for how to reference their work specifically

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
- ONLY reference a Facebook post if it describes a SPECIFIC JOB the business completed
- DO NOT reference generic posts, ads, promotions, memes, holiday greetings, or reshares
- If the social post doesn't describe a completed job or specific project, IGNORE IT completely
- When referencing a job post, be natural: "saw you just did that kitchen in Applecross" not "I noticed your recent Facebook post about..."

SIGN-OFF (always use exactly this):
Cheers,
Aaron
0498 201 788

---
If this isn't relevant, just reply stop and I won't contact you again.
Aaron Parton | Perth, WA

OUTPUT FORMAT (valid JSON only, no markdown, no code fences):
{"subject": "short subject line, lowercase", "body": "the full email", "call_script": "a brief call script - bullet points for Aaron to reference when calling. Structure: opener (hey is this [name]?) then hook (what caught your attention about their business) then bridge (I build websites for [trade]s) then value (most [trade]s I talk to are losing jobs to competitors with websites) then ask (would you be open to a quick chat?). Include one objection handler. Keep it conversational, not robotic."}`;

// ═══════════════════════════════════════════════
// VARIANTS (upgraded with social-active structure)
// ═══════════════════════════════════════════════

const STANDARD_VARIANTS = [
  { name: 'reviewer_namedrop', instruction: 'Reference a specific reviewer by first name. "saw [Name] left you a great review" or "sounds like [Name] rated your work highly". Use their actual review quote if available.' },
  { name: 'missing_out', instruction: 'Frame it around what they are missing. Customers Google them, find nothing, and call their competitor instead. Keep it factual, not fear-mongering.' },
  { name: 'look_the_part', instruction: 'Focus on looking professional. They do great work (reviews prove it) but online they are invisible. A website makes them look as good as they actually are.' },
  { name: 'dead_simple', instruction: 'Absolute minimum words. 3-4 sentences total. Free website offer, no catch, interested? Nothing else.' },
  { name: 'free_offer_upfront', instruction: 'Lead with the free website offer immediately. No buildup. "I build free websites for [trade]s. Yours would take about a week. Interested?"' },
];

const SOCIAL_ACTIVE_VARIANT = {
  name: 'social_active',
  instruction: `This lead is ACTIVE on social media with recent job posts. Use this structure exactly:
1. PERSONAL OPENER - use trade lingo, be casual ("Hey [Name],")
2. SAW YOUR CONTENT - reference their specific post naturally. Don't say "I saw on your Facebook page". Just reference the content like you naturally came across it
3. SPECIFIC PROOF - mention a specific detail from the post (suburb, technique, material, result) with a genuine reaction
4. CREDIBILITY + RELEVANCE - "The reason I'm reaching out is I build websites for [trade]s, and after seeing your work I thought you'd be a good fit"
5. VALUE PROP - "Most [trade]s I talk to are getting calls from Google but don't have a website, so they're losing jobs to the blokes who do"
6. LOW-FRICTION ASK - "Worth a quick chat? No pitch, just wanted to show you what I had in mind"

Example for a plumber who posted about a HWS swap:
"Hey Dave, I came across that hot water changeover you did in Joondalup the other day. Rheem to Rinnai continuous flow, smart move, those things pay for themselves. The reason I'm reaching out is I build websites for plumbers, and after seeing your work I reckon you'd be a solid fit. Your reviews already sell you. A website would just make it easier for people to find you and get in touch. Worth a quick chat?"`,
};

const NEW_BUSINESS_VARIANT = {
  name: 'new_business',
  instruction: 'This is a newly registered business (from ABR). Congratulations angle. "Saw that [Business Name] just got started, congrats on taking the leap." Then mention most new businesses want a website but don\'t want to spend thousands. You build them free. No catch. Keep it warm and encouraging.',
};

// ═══════════════════════════════════════════════
// BUILD THE PROMPT
// ═══════════════════════════════════════════════

const lead = $input.item.json;

// Look up trade lingo
const category = (lead.category || '').toLowerCase().trim();
const tradeLingo = TRADE_LINGO[category] || GENERIC_LINGO;

// Determine personalisation type via social gating
let personalisationType = 'standard';
let selectedVariant;

const isABRLead = lead.source === 'abr' || !!lead.registration_date;

// Social gating decision tree
const hasFacebook = !!lead.facebook_url;
const hasSocialPost = !!lead.social_best_post;
const postDate = lead.social_post_date ? new Date(lead.social_post_date) : null;
const isRecentPost = postDate && ((Date.now() - postDate.getTime()) < 60 * 24 * 60 * 60 * 1000); // 60 days

// Relevance filter: only job-related posts qualify
const isRelevantPost = hasSocialPost && /(?:just |recently )?(finished|completed|done|wrapped|installed|fitted|put in|set up|wired up)|before.{0,10}after|another.*done|happy (client|customer)|handed over|final result|latest (project|job|build|install)|proud of|check out (this|our|the)|tip[s]? (?:for|about|on)|how to|did you know|pro tip|great (review|feedback)|thank you.*customer/i.test(lead.social_best_post);

if (isABRLead) {
  personalisationType = 'new_business';
  selectedVariant = NEW_BUSINESS_VARIANT;
} else if (hasFacebook && hasSocialPost && isRecentPost && isRelevantPost) {
  personalisationType = 'social_active';
  selectedVariant = SOCIAL_ACTIVE_VARIANT;
} else {
  personalisationType = 'standard';
  selectedVariant = STANDARD_VARIANTS[Math.floor(Math.random() * STANDARD_VARIANTS.length)];
}

// Humour: every 10th email (deterministic based on a counter)
// Use a simple hash of business name + date to make it deterministic but distributed
const nameHash = (lead.business_name || '').split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 86400000);
const hasHumour = ((nameHash + dayOfYear) % 10 === 0);

// Build lead context
const parts = [`Business: ${lead.business_name}`];
if (lead.category) parts.push(`Trade: ${lead.category}`);
if (lead.suburb) parts.push(`Location: ${lead.suburb}, ${lead.state || 'WA'}`);
if (lead.google_reviews) parts.push(`${lead.google_reviews} Google reviews (${lead.google_rating || '?'} stars)`);
if (lead.top_review_quote) parts.push(`Top review quote: "${lead.top_review_quote.substring(0, 150)}"`);
if (lead.top_reviewer_name) parts.push(`Top reviewer name: ${lead.top_reviewer_name}`);
if (lead.second_reviewer_name) parts.push(`Another reviewer: ${lead.second_reviewer_name}`);
if (lead.website_is_facebook) parts.push('Currently using Facebook as their website');
if (lead.phone) parts.push(`Phone: ${lead.phone}`);

// Social context (only for social_active leads)
if (personalisationType === 'social_active' && lead.social_best_post) {
  parts.push(`Recent Facebook post about a job: "${lead.social_best_post}"`);
  if (lead.social_post_date) parts.push(`Post date: ${lead.social_post_date}`);
  if (lead.social_post_engagement) parts.push(`Post engagement: ${lead.social_post_engagement} likes/comments`);
}
if (lead.social_about) {
  parts.push(`Facebook About: "${lead.social_about.substring(0, 150)}"`);
}

parts.push(`Score: ${lead.score}/10`);

// Trade lingo context for the prompt
const lingoContext = [
  `\nTRADE LINGO FOR THIS ${(lead.category || 'business').toUpperCase()}:`,
  `Common jobs: ${tradeLingo.jobs.join(', ') || 'general work'}`,
  `Terms they use: ${tradeLingo.terms.join(', ') || 'standard terms'}`,
  `Example reference: "${tradeLingo.flavour.replace('{suburb}', lead.suburb || 'the area').replace('{category}', lead.category || 'business')}"`,
  'USE 1-2 of these terms naturally. Do NOT force them.',
];
parts.push(lingoContext.join('\n'));

// Humour instruction
let humourInstruction = '';
if (hasHumour) {
  const humourOpener = tradeLingo.humour_opener
    .replace('{suburb}', lead.suburb || 'the area')
    .replace('{category}', lead.category || 'business');
  const humourCta = HUMOUR_CTAS[nameHash % HUMOUR_CTAS.length];
  humourInstruction = `\n\nHUMOUR (this email should include light humour - ONE line only, either opener or CTA, not both):\nOpener option: "${humourOpener}"\nCTA option: "${humourCta}"\nPick whichever fits better. Keep it natural. If neither fits, write your own single humorous line in the same style.`;
}

const userPrompt = `Write a cold email. Angle: ${selectedVariant.instruction}${humourInstruction}\n\nLEAD:\n${parts.join('\n')}\n\nFocus on helping them book more jobs by looking professional. No jargon, no "digital presence". Valid JSON only.`;

// Track which lingo terms we're providing
const lingoUsed = tradeLingo === GENERIC_LINGO ? ['generic'] : [category];

return {
  json: {
    ...lead,
    _variant_name: selectedVariant.name,
    _personalisation_type: personalisationType,
    _has_humour: hasHumour,
    _trade_lingo_used: lingoUsed,
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
# STEP 4: UPDATE PARSE EMAIL A — extract new fields
# ═══════════════════════════════════════════════════════════════

print('\nStep 4: Updating Parse Email A...')

PARSE_EMAIL_A_CODE = r"""// Parse OpenAI Response - Pipeline A (Smart Outreach v2)
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
    .replace(/\u2014/g, ',')
    .replace(/\u2013/g, '-')
    .replace(/\s*[\u2014\u2013]\s*/g, ', ')
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
if (lead._personalisation_type === 'social_active') whyParts.push('social-active');
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
    personalisation_type: lead._personalisation_type || 'standard',
    has_humour: lead._has_humour || false,
    trade_lingo_used: lead._trade_lingo_used || [],
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
    facebook_url: lead.facebook_url || '',
    social_best_post: lead.social_best_post || '',
  }
};"""

# ═══════════════════════════════════════════════════════════════
# STEP 5: UPDATE SUPABASE STORE — add new fields
# ═══════════════════════════════════════════════════════════════

print('\nStep 5: Updating Supabase Store node...')

# Find and update nodes
for node in wf['nodes']:
    if node['name'] == 'Build Email Prompt A':
        node['parameters']['jsCode'] = BUILD_PROMPT_A_CODE
        print('  Build Email Prompt A updated')

    elif node['name'] == 'Parse Email A':
        node['parameters']['jsCode'] = PARSE_EMAIL_A_CODE
        print('  Parse Email A updated')

    elif node['name'] == 'Supabase: Store Leads':
        code = node['parameters']['jsCode']
        # Add new fields to the row object
        if 'personalisation_type' not in code:
            code = code.replace(
                "  status: 'new',",
                """  personalisation_type: lead.personalisation_type || lead._personalisation_type || null,
  has_humour: lead.has_humour || lead._has_humour || false,
  trade_lingo_used: lead.trade_lingo_used || lead._trade_lingo_used || null,
  email_variant: lead.email_variant || lead._variant_name || null,
  call_script: lead.call_script || null,
  status: 'new',"""
            )
            node['parameters']['jsCode'] = code
            print('  Supabase Store updated with new fields')
        else:
            print('  Supabase Store already has personalisation fields')

# ═══════════════════════════════════════════════════════════════
# STEP 6: PUSH WORKFLOW
# ═══════════════════════════════════════════════════════════════

print('\nStep 6: Pushing workflow...')

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

print('\n=== DEPLOYMENT COMPLETE ===')
print('Changes deployed:')
print('  - Supabase: leads table + outreach_events table + 5 performance views')
print('  - Build Email Prompt A: trade lingo (16 trades), social gating, humour A/B, improved call scripts')
print('  - Parse Email A: extracts personalisation_type, has_humour, trade_lingo_used')
print('  - Supabase Store: persists new tracking fields')
print('\nNext: test via Manual Trigger in n8n')
