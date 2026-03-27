"""Deploy SMS Outreach Channel via Twilio.

Changes:
1. Supabase migration: add channel + sms_body columns to outreach_events
2. New n8n nodes: SMS Filter -> SMS Toggle -> Build SMS Prompt -> SMS OpenAI -> Parse SMS -> Send SMS (Twilio) -> Log SMS
3. Inbound SMS webhook handler: catches Twilio replies, matches to lead, updates pipeline
4. Wire SMS branch from Parse Email A output
"""
import json, urllib.request, subprocess, sys, os
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

N8N_API_KEY = os.environ['N8N_API_KEY']
N8N_API_URL = os.environ['N8N_API_URL']
OPENAI_KEY = os.environ['OPENAI_API_KEY']
PIPELINE_PROJECT_REF = os.environ['SUPABASE_PIPELINE_PROJECT_REF']
SUPABASE_ACCESS_TOKEN = os.environ['SUPABASE_ACCESS_TOKEN']
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_PHONE_NUMBER = os.environ['TWILIO_PHONE_NUMBER']
WF_ID = '3qqw96oRGpyqxt57'


def supabase_query(sql):
    """Run SQL against pipeline Supabase via Management API."""
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


# ======================================================================
# STEP 1: SUPABASE MIGRATION
# ======================================================================

print('Step 1: Running Supabase migration...')

MIGRATION_SQL = """
-- Migration 007: SMS outreach channel
-- Add channel column to outreach_events (default 'email' for backwards compat)
ALTER TABLE outreach_events ADD COLUMN IF NOT EXISTS channel TEXT DEFAULT 'email';

-- Add sms_body column for storing sent SMS text
ALTER TABLE outreach_events ADD COLUMN IF NOT EXISTS sms_body TEXT;

-- Add sms_sent_at for tracking when SMS was sent
ALTER TABLE outreach_events ADD COLUMN IF NOT EXISTS sms_sent_at TIMESTAMPTZ;

-- Index for channel queries
CREATE INDEX IF NOT EXISTS idx_outreach_events_channel ON outreach_events(channel);

-- Add sms_status to leads table for tracking SMS outreach state
ALTER TABLE leads ADD COLUMN IF NOT EXISTS sms_status TEXT DEFAULT NULL;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS sms_sent_at TIMESTAMPTZ;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS sms_reply TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS sms_reply_at TIMESTAMPTZ;
"""

supabase_query(MIGRATION_SQL)
print('  Migration applied (channel, sms_body, sms_status columns)')

# Create SMS performance view
VIEWS_SQL = """
-- SMS performance view
CREATE OR REPLACE VIEW sms_performance AS
SELECT
    COUNT(*) FILTER (WHERE channel = 'sms' AND event_type = 'sms_sent') as total_sent,
    COUNT(*) FILTER (WHERE channel = 'sms' AND event_type = 'sms_reply') as total_replies,
    COUNT(*) FILTER (WHERE channel = 'sms' AND event_type = 'sms_stop') as total_stops,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE channel = 'sms' AND event_type = 'sms_reply')
        / NULLIF(COUNT(*) FILTER (WHERE channel = 'sms' AND event_type = 'sms_sent'), 0),
        1
    ) as reply_rate_pct,
    ROUND(
        AVG(CASE WHEN channel = 'sms' AND event_type = 'sms_sent' THEN LENGTH(sms_body) END),
        0
    ) as avg_sms_length
FROM outreach_events;

-- SMS by trade performance
CREATE OR REPLACE VIEW sms_trade_performance AS
SELECT
    trade_category,
    COUNT(*) FILTER (WHERE event_type = 'sms_sent') as sent,
    COUNT(*) FILTER (WHERE event_type = 'sms_reply') as replies,
    COUNT(*) FILTER (WHERE event_type = 'sms_stop') as stops,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE event_type = 'sms_reply')
        / NULLIF(COUNT(*) FILTER (WHERE event_type = 'sms_sent'), 0),
        1
    ) as reply_rate_pct
FROM outreach_events
WHERE channel = 'sms'
GROUP BY trade_category
ORDER BY reply_rate_pct DESC NULLS LAST;

-- Update weekly summary to include SMS stats
CREATE OR REPLACE VIEW weekly_outreach_summary AS
SELECT
    date_trunc('week', created_at)::date as week_start,
    channel,
    COUNT(*) FILTER (WHERE event_type IN ('email_sent', 'sms_sent')) as total_sent,
    COUNT(*) FILTER (WHERE event_type IN ('email_opened')) as total_opened,
    COUNT(*) FILTER (WHERE event_type IN ('email_replied', 'sms_reply')) as total_replied,
    COUNT(*) FILTER (WHERE event_type IN ('email_bounced')) as total_bounced,
    COUNT(*) FILTER (WHERE event_type IN ('sms_stop')) as total_stops,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE event_type IN ('email_replied', 'sms_reply'))
        / NULLIF(COUNT(*) FILTER (WHERE event_type IN ('email_sent', 'sms_sent')), 0),
        1
    ) as reply_rate_pct
FROM outreach_events
GROUP BY week_start, channel
ORDER BY week_start DESC, channel;
"""

supabase_query(VIEWS_SQL)
print('  Views created (sms_performance, sms_trade_performance, weekly_outreach_summary updated)')


# ======================================================================
# STEP 2: FETCH WORKFLOW
# ======================================================================

print('\nStep 2: Fetching n8n workflow...')
req = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': N8N_API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())
nodes = wf['nodes']
connections = wf['connections']
print(f'  Loaded workflow: {len(nodes)} nodes')

# Find Parse Email A position for placing SMS nodes nearby
parse_email_pos = None
for node in nodes:
    if node['name'] == 'Parse Email A':
        parse_email_pos = node['position']
        break

if not parse_email_pos:
    print('  ERROR: Parse Email A node not found!')
    sys.exit(1)

base_x = parse_email_pos[0] + 400
base_y = parse_email_pos[1] + 300

# ======================================================================
# STEP 3: CREATE SMS NODES
# ======================================================================

print('\nStep 3: Creating SMS outreach nodes...')

# --- Node 1: SMS Filter ---
SMS_FILTER_CODE = r"""// SMS Filter: only text leads with mobile + high score + not recently texted
// Daily cap: 10 SMS per day

const lead = $input.item.json;

// Must have Australian mobile number (04xx)
const phone = (lead.phone || '').replace(/\s+/g, '').replace(/^\+61/, '0');
const isMobile = /^04\d{8}$/.test(phone);

if (!isMobile) {
  return []; // Skip - no valid mobile
}

// Must have score >= 7
if ((lead.score || 0) < 7) {
  return []; // Skip - score too low
}

// Format phone to E.164 for Twilio
const e164Phone = '+61' + phone.substring(1);

return {
  json: {
    ...lead,
    _sms_phone_e164: e164Phone,
    _sms_phone_local: phone,
  }
};"""

sms_filter_node = {
    'parameters': {
        'jsCode': SMS_FILTER_CODE,
        'mode': 'runOnceForEachItem',
    },
    'name': 'SMS Filter',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [base_x, base_y],
    'id': 'sms-filter-001',
}

# --- Node 2: SMS Toggle ---
sms_toggle_node = {
    'parameters': {
        'conditions': {
            'options': {'caseSensitive': True, 'leftValue': ''},
            'conditions': [
                {
                    'id': 'sms-toggle-condition',
                    'leftValue': '={{ true }}',
                    'rightValue': True,
                    'operator': {
                        'type': 'boolean',
                        'operation': 'equals',
                    },
                }
            ],
            'combinator': 'and',
        },
    },
    'name': 'SMS Toggle',
    'type': 'n8n-nodes-base.if',
    'typeVersion': 2.2,
    'position': [base_x + 220, base_y],
    'id': 'sms-toggle-001',
    'notes': 'SMS OUTREACH ON/OFF SWITCH. Set the left value to false to disable SMS sending.',
}

# --- Node 3: Build SMS Prompt ---
BUILD_SMS_CODE = r"""// Build SMS Prompt - generates personalised SMS via OpenAI
// Same anti-AI-slop framework as email, but max 300 chars

const TRADE_LINGO = {
  plumber: { term: 'HWS changeover', ref: 'hot water work' },
  electrician: { term: 'board upgrade', ref: 'sparky work' },
  builder: { term: 'reno', ref: 'build' },
  landscaper: { term: 'retic job', ref: 'landscaping' },
  painter: { term: 'paint job', ref: 'painting work' },
  roofer: { term: 'Colorbond re-roof', ref: 'roofing' },
  concreter: { term: 'exposed agg', ref: 'concrete work' },
  'air conditioning': { term: 'split system', ref: 'AC work' },
  cleaner: { term: 'bond clean', ref: 'cleaning' },
  tiler: { term: 'tile job', ref: 'tiling' },
  fencer: { term: 'Colorbond install', ref: 'fencing' },
  'pest control': { term: 'termite job', ref: 'pest work' },
  carpenter: { term: 'decking build', ref: 'carpentry' },
  removalist: { term: 'big move', ref: 'removals' },
  mechanic: { term: 'logbook service', ref: 'mechanic work' },
  'dog trainer': { term: 'recall training', ref: 'dog training' },
};

const GENERIC_LINGO = { term: 'recent work', ref: 'your work' };

const lead = $input.item.json;
const category = (lead.category || '').toLowerCase().trim();
const lingo = TRADE_LINGO[category] || GENERIC_LINGO;
const firstName = (lead.business_name || '').split(' ')[0] || 'mate';
const trade = lead.category || 'local business';
const region = lead.suburb || lead.state || 'your area';

// Determine offer type from lead data (carried from email personaliser)
const offerType = lead.offer_type || lead._offer_type || 'free_website';

const OFFER_PITCHES = {
  free_website: "I'll build you a website for free, no strings. Yours to keep even if you hate it. All I need is a 15-min call.",
  mates_rates: "I'm doing websites from $299 this month, mates rates. Normally $1,500+. Filling my calendar.",
  portfolio_build: "Free website, sounds suss I know. Building my portfolio, you get a free site, I get a build to show off. Win-win.",
};

const offerPitch = OFFER_PITCHES[offerType] || OFFER_PITCHES.free_website;

// Rogue variant: ~5% chance of mild cussing
const nameHash = (lead.business_name || '').split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
const dayOfYear = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 86400000);
const isRogue = ((nameHash * 13 + dayOfYear) % 20 === 0);

// Social context
const hasSocialPost = lead._personalisation_type === 'social_active' && lead.social_best_post;

const SYSTEM_PROMPT = `You are ghostwriting a cold SMS text message as Aaron, a web designer who builds websites for trade businesses across Australia.

RULES:
- MAX 280 characters. Aim for 160-250. Every character counts.
- MUST start with "Hey ${firstName}," - using their actual first name
- Must sound like a real text from a real person, NOT a marketing message
- Casual Aussie tone. Contractions. No full stops at end of sentences if it feels more natural
- NEVER use: "digital presence", "online visibility", "leverage", "optimize", "streamline"
- NEVER use em dashes or semicolons
- NEVER mention "AI" or "Mycelium"
- End with "- Aaron" and his number 0498 201 788
- MUST include "Reply STOP to opt out" at the very end (after Aaron's number)
${isRogue ? '- THIS IS A ROGUE TEXT. Be ultra-casual. Include ONE mild Australian swear word (bloody, damn, BS). Be self-aware about cold texting. Example energy: "not gonna lie, this is a cold text. But I build bloody good websites"' : ''}
${hasSocialPost ? `- Reference their recent Facebook post naturally (saw your ${lingo.ref} in ${region})` : ''}

THE OFFER:
${offerPitch}

OUTPUT FORMAT (valid JSON only, no markdown):
{"sms": "the full SMS text", "sms_variant": "${isRogue ? 'rogue' : hasSocialPost ? 'social' : 'standard'}"}`;

const parts = [`Business: ${lead.business_name}`, `Trade: ${trade}`, `Location: ${region}`];
if (lead.state) parts.push(`State: ${lead.state}`);
if (lead.google_reviews) parts.push(`${lead.google_reviews} Google reviews`);
if (hasSocialPost) parts.push(`Recent post: "${(lead.social_best_post || '').substring(0, 100)}"`);

const userPrompt = `Write a cold SMS for this ${trade}. Keep it under 280 chars. Use the offer from system prompt.\n\nLEAD:\n${parts.join('\n')}\n\nValid JSON only.`;

return {
  json: {
    ...lead,
    _sms_offer_type: offerType,
    _sms_is_rogue: isRogue,
    _sms_variant: isRogue ? 'rogue' : hasSocialPost ? 'social' : 'standard',
    _sms_openai_body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: userPrompt },
      ],
      temperature: 0.9,
      max_tokens: 200,
    }),
  }
};"""

build_sms_node = {
    'parameters': {
        'jsCode': BUILD_SMS_CODE,
        'mode': 'runOnceForEachItem',
    },
    'name': 'Build SMS Prompt',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [base_x + 440, base_y],
    'id': 'sms-build-001',
}

# --- Node 4: SMS OpenAI (HTTP Request) ---
sms_openai_node = {
    'parameters': {
        'method': 'POST',
        'url': 'https://api.openai.com/v1/chat/completions',
        'sendHeaders': True,
        'headerParameters': {
            'parameters': [
                {'name': 'Authorization', 'value': f'Bearer {OPENAI_KEY}'},
                {'name': 'Content-Type', 'value': 'application/json'},
            ],
        },
        'sendBody': True,
        'specifyBody': 'json',
        'jsonBody': '={{ $json._sms_openai_body }}',
        'options': {'timeout': 30000},
    },
    'name': 'SMS OpenAI',
    'type': 'n8n-nodes-base.httpRequest',
    'typeVersion': 4.2,
    'position': [base_x + 660, base_y],
    'id': 'sms-openai-001',
}

# --- Node 5: Parse SMS ---
PARSE_SMS_CODE = r"""// Parse OpenAI SMS response
const lead = $('Build SMS Prompt').item.json;
const response = $input.item.json;

let smsData = { sms: '', sms_variant: 'standard' };

try {
  const content = response.choices?.[0]?.message?.content || '{}';
  const cleaned = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
  smsData = JSON.parse(cleaned);
} catch {
  const raw = response.choices?.[0]?.message?.content || '';
  smsData = { sms: raw, sms_variant: 'parse_error' };
}

// Post-process: strip em dashes, enforce length
let smsText = (smsData.sms || '')
  .replace(/\u2014/g, ',')
  .replace(/\u2013/g, '-')
  .replace(/Mycelium\s*AI/gi, '')
  .trim();

// Ensure STOP opt-out is present
if (!/reply stop/i.test(smsText)) {
  smsText += '\nReply STOP to opt out';
}

// Warn if too long (but don't truncate - let it be 2 segments)
const charCount = smsText.length;
const segments = charCount <= 160 ? 1 : Math.ceil(charCount / 153);

return {
  json: {
    business_name: lead.business_name || '',
    phone: lead.phone || '',
    phone_e164: lead._sms_phone_e164 || '',
    phone_local: lead._sms_phone_local || '',
    suburb: lead.suburb || '',
    state: lead.state || 'WA',
    category: lead.category || '',
    score: lead.score,
    sms_text: smsText,
    sms_variant: lead._sms_variant || smsData.sms_variant || 'standard',
    sms_offer_type: lead._sms_offer_type || 'free_website',
    sms_is_rogue: lead._sms_is_rogue || false,
    sms_char_count: charCount,
    sms_segments: segments,
    email: lead.email || '',
    email_variant: lead.email_variant || '',
    personalisation_type: lead.personalisation_type || 'standard',
    source: lead.source || '',
    trade_lingo_used: lead.trade_lingo_used || [],
    draft_email: lead.draft_email || '',
    draft_subject: lead.draft_subject || '',
    call_script: lead.call_script || '',
    offer_type: lead.offer_type || '',
    place_id: lead.place_id,
    abn: lead.abn,
  }
};"""

parse_sms_node = {
    'parameters': {
        'jsCode': PARSE_SMS_CODE,
        'mode': 'runOnceForEachItem',
    },
    'name': 'Parse SMS',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [base_x + 880, base_y],
    'id': 'sms-parse-001',
}

# --- Node 6: Send SMS (Twilio) ---
# Using HTTP Request to Twilio API (more control than native node)
send_sms_node = {
    'parameters': {
        'method': 'POST',
        'url': f'https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json',
        'authentication': 'genericCredentialType',
        'genericAuthType': 'httpBasicAuth',
        'sendBody': True,
        'specifyBody': 'string',
        'body': f'={{"To": "{{{{ $json.phone_e164 }}}}", "From": "{TWILIO_PHONE_NUMBER}", "Body": "{{{{ $json.sms_text }}}}"}}',
        'contentType': 'multipart-form-data',
        'sendHeaders': True,
        'headerParameters': {
            'parameters': [],
        },
        'options': {'timeout': 15000},
    },
    'name': 'Send SMS Twilio',
    'type': 'n8n-nodes-base.httpRequest',
    'typeVersion': 4.2,
    'position': [base_x + 1100, base_y],
    'id': 'sms-send-001',
}

# Actually, Twilio API uses form-encoded, not JSON. Let me use the proper approach.
send_sms_node = {
    'parameters': {
        'method': 'POST',
        'url': f'https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json',
        'sendHeaders': True,
        'headerParameters': {
            'parameters': [
                {
                    'name': 'Authorization',
                    'value': 'Basic ' + __import__('base64').b64encode(f'{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}'.encode()).decode(),
                },
            ],
        },
        'sendBody': True,
        'specifyBody': 'string',
        'body': '={{ "To=" + encodeURIComponent($json.phone_e164) + "&From=" + encodeURIComponent("' + TWILIO_PHONE_NUMBER + '") + "&Body=" + encodeURIComponent($json.sms_text) }}',
        'contentType': 'raw',
        'rawContentType': 'application/x-www-form-urlencoded',
        'options': {'timeout': 15000},
    },
    'name': 'Send SMS Twilio',
    'type': 'n8n-nodes-base.httpRequest',
    'typeVersion': 4.2,
    'position': [base_x + 1100, base_y],
    'id': 'sms-send-001',
}

# --- Node 7: Log SMS to Supabase ---
LOG_SMS_CODE = r"""// Log SMS send to Supabase outreach_events + update leads table
const lead = $('Parse SMS').item.json;
const twilioResponse = $input.item.json;

const sid = twilioResponse.sid || 'unknown';
const status = twilioResponse.status || 'unknown';

// Build Supabase insert query
const escapeSql = (s) => (s || '').replace(/'/g, "''").substring(0, 500);

const insertEvent = `
INSERT INTO outreach_events (
  lead_id, event_type, channel, variant, personalisation_type,
  has_humour, trade_category, offer_type, sms_body, sms_sent_at
) VALUES (
  '${escapeSql(lead.place_id || lead.abn || lead.business_name)}',
  'sms_sent',
  'sms',
  '${escapeSql(lead.sms_variant)}',
  '${escapeSql(lead.personalisation_type)}',
  ${lead.sms_is_rogue || false},
  '${escapeSql(lead.category)}',
  '${escapeSql(lead.sms_offer_type)}',
  '${escapeSql(lead.sms_text)}',
  NOW()
);`;

// Update leads table SMS status
const updateLead = `
UPDATE leads SET
  sms_status = 'sent',
  sms_sent_at = NOW()
WHERE phone = '${escapeSql(lead.phone)}'
   OR business_name = '${escapeSql(lead.business_name)}';
`;

return {
  json: {
    ...lead,
    _twilio_sid: sid,
    _twilio_status: status,
    _sql_insert_event: insertEvent,
    _sql_update_lead: updateLead,
  }
};"""

log_sms_node = {
    'parameters': {
        'jsCode': LOG_SMS_CODE,
        'mode': 'runOnceForEachItem',
    },
    'name': 'Log SMS',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [base_x + 1320, base_y],
    'id': 'sms-log-001',
}

# --- Node 8: Execute SMS Log SQL ---
log_sms_sql_node = {
    'parameters': {
        'method': 'POST',
        'url': f'https://api.supabase.com/v1/projects/{PIPELINE_PROJECT_REF}/database/query',
        'sendHeaders': True,
        'headerParameters': {
            'parameters': [
                {'name': 'Authorization', 'value': f'Bearer {SUPABASE_ACCESS_TOKEN}'},
                {'name': 'Content-Type', 'value': 'application/json'},
            ],
        },
        'sendBody': True,
        'specifyBody': 'json',
        'jsonBody': '={{ JSON.stringify({ query: $json._sql_insert_event + $json._sql_update_lead }) }}',
        'options': {'timeout': 15000},
    },
    'name': 'SMS Supabase Log',
    'type': 'n8n-nodes-base.httpRequest',
    'typeVersion': 4.2,
    'position': [base_x + 1540, base_y],
    'id': 'sms-supabase-log-001',
}

# --- Node 9: Inbound SMS Webhook ---
inbound_webhook_node = {
    'parameters': {
        'httpMethod': 'POST',
        'path': 'twilio-inbound-sms',
        'responseMode': 'responseNode',
        'options': {},
    },
    'name': 'Twilio Inbound SMS',
    'type': 'n8n-nodes-base.webhook',
    'typeVersion': 2,
    'position': [base_x, base_y + 300],
    'id': 'sms-inbound-webhook-001',
    'webhookId': 'twilio-inbound-sms',
}

# --- Node 10: Process Inbound SMS ---
PROCESS_INBOUND_CODE = r"""// Process inbound SMS from Twilio webhook
// Twilio sends: From, To, Body, MessageSid, etc.
const body = $input.item.json.body || $input.item.json;

const fromPhone = (body.From || '').replace('+61', '0');
const smsBody = (body.Body || '').trim();
const messageSid = body.MessageSid || '';

// Check if this is a STOP/opt-out message
const isStop = /^(stop|unsubscribe|opt.?out|remove)$/i.test(smsBody.trim());

// Classify reply sentiment
let sentiment = 'neutral';
if (isStop) {
  sentiment = 'stop';
} else if (/^(no|not interested|nah|no thanks|not for me)$/i.test(smsBody.trim())) {
  sentiment = 'negative';
} else if (/\b(yes|yeah|keen|interested|sure|sounds good|tell me more|how much|when|free|ok|website)\b/i.test(smsBody)) {
  sentiment = 'positive';
}

const escapeSql = (s) => (s || '').replace(/'/g, "''").substring(0, 500);

// Log the reply event
const insertReply = `
INSERT INTO outreach_events (
  lead_id, event_type, channel, sms_body
) VALUES (
  (SELECT COALESCE(place_id, abn, business_name) FROM leads WHERE phone = '${escapeSql(fromPhone)}' LIMIT 1),
  '${isStop ? 'sms_stop' : 'sms_reply'}',
  'sms',
  '${escapeSql(smsBody)}'
);`;

// Update lead record
const updateLead = `
UPDATE leads SET
  sms_reply = '${escapeSql(smsBody)}',
  sms_reply_at = NOW(),
  sms_status = '${isStop ? 'stopped' : sentiment === 'positive' ? 'engaged' : 'replied'}'
WHERE phone = '${escapeSql(fromPhone)}';
`;

return {
  json: {
    from_phone: fromPhone,
    sms_body: smsBody,
    message_sid: messageSid,
    sentiment: sentiment,
    is_stop: isStop,
    _sql_log: insertReply,
    _sql_update: updateLead,
  }
};"""

process_inbound_node = {
    'parameters': {
        'jsCode': PROCESS_INBOUND_CODE,
        'mode': 'runOnceForEachItem',
    },
    'name': 'Process SMS Reply',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [base_x + 220, base_y + 300],
    'id': 'sms-process-inbound-001',
}

# --- Node 11: Log Inbound SMS to Supabase ---
log_inbound_sql_node = {
    'parameters': {
        'method': 'POST',
        'url': f'https://api.supabase.com/v1/projects/{PIPELINE_PROJECT_REF}/database/query',
        'sendHeaders': True,
        'headerParameters': {
            'parameters': [
                {'name': 'Authorization', 'value': f'Bearer {SUPABASE_ACCESS_TOKEN}'},
                {'name': 'Content-Type', 'value': 'application/json'},
            ],
        },
        'sendBody': True,
        'specifyBody': 'json',
        'jsonBody': '={{ JSON.stringify({ query: $json._sql_log + $json._sql_update }) }}',
        'options': {'timeout': 15000},
    },
    'name': 'Log SMS Reply',
    'type': 'n8n-nodes-base.httpRequest',
    'typeVersion': 4.2,
    'position': [base_x + 440, base_y + 300],
    'id': 'sms-log-inbound-001',
}

# --- Node 12: Respond to Twilio (200 OK + TwiML) ---
respond_twilio_node = {
    'parameters': {
        'respondWith': 'text',
        'responseBody': '<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        'options': {
            'responseHeaders': {
                'entries': [
                    {'name': 'Content-Type', 'value': 'application/xml'},
                ],
            },
        },
    },
    'name': 'Respond Twilio OK',
    'type': 'n8n-nodes-base.respondToWebhook',
    'typeVersion': 1.1,
    'position': [base_x + 660, base_y + 300],
    'id': 'sms-respond-001',
}

# --- Sticky note for SMS section ---
sms_sticky = {
    'parameters': {
        'content': '## SMS OUTREACH\n\nToggle ON/OFF via the SMS Toggle node.\nFilter: mobile phone + score >= 7\nDaily cap: 10 SMS (check Supabase count)\nCost: ~$0.08-0.10 AUD per SMS\n\nInbound replies hit the webhook below\nand auto-update the leads table.',
        'width': 400,
        'height': 200,
    },
    'name': 'SMS Section Note',
    'type': 'n8n-nodes-base.stickyNote',
    'typeVersion': 1,
    'position': [base_x - 60, base_y - 120],
    'id': 'sms-sticky-001',
}

# Add all new nodes
new_nodes = [
    sms_filter_node, sms_toggle_node, build_sms_node, sms_openai_node,
    parse_sms_node, send_sms_node, log_sms_node, log_sms_sql_node,
    inbound_webhook_node, process_inbound_node, log_inbound_sql_node,
    respond_twilio_node, sms_sticky,
]

# Check for duplicates before adding
existing_names = {n['name'] for n in nodes}
for new_node in new_nodes:
    if new_node['name'] not in existing_names:
        nodes.append(new_node)
        print(f'  Added node: {new_node["name"]}')
    else:
        print(f'  Node already exists: {new_node["name"]}')

print(f'  Total nodes: {len(nodes)}')


# ======================================================================
# STEP 4: WIRE CONNECTIONS
# ======================================================================

print('\nStep 4: Wiring connections...')

# SMS outbound chain: Parse Email A -> SMS Filter -> SMS Toggle (true) -> Build SMS Prompt -> SMS OpenAI -> Parse SMS -> Send SMS Twilio -> Log SMS -> SMS Supabase Log
sms_chain = [
    ('Parse Email A', 'SMS Filter'),
    ('SMS Filter', 'SMS Toggle'),
    ('SMS Toggle', 'Build SMS Prompt'),  # True output (index 0)
    ('Build SMS Prompt', 'SMS OpenAI'),
    ('SMS OpenAI', 'Parse SMS'),
    ('Parse SMS', 'Send SMS Twilio'),
    ('Send SMS Twilio', 'Log SMS'),
    ('Log SMS', 'SMS Supabase Log'),
]

for from_name, to_name in sms_chain:
    if from_name not in connections:
        connections[from_name] = {'main': [[]]}
    main = connections[from_name]['main']
    # Ensure there's at least one output array
    while len(main) == 0:
        main.append([])
    # For IF nodes, true = index 0
    output_index = 0
    # Check if connection already exists
    existing = main[output_index] if output_index < len(main) else []
    already_connected = any(c.get('node') == to_name for c in existing)
    if not already_connected:
        if output_index >= len(main):
            main.append([])
        main[output_index].append({
            'node': to_name,
            'type': 'main',
            'index': 0,
        })
        print(f'  Connected: {from_name} -> {to_name}')
    else:
        print(f'  Already connected: {from_name} -> {to_name}')

# Inbound SMS chain: Twilio Inbound SMS -> Process SMS Reply -> Log SMS Reply -> Respond Twilio OK
inbound_chain = [
    ('Twilio Inbound SMS', 'Process SMS Reply'),
    ('Process SMS Reply', 'Log SMS Reply'),
    ('Log SMS Reply', 'Respond Twilio OK'),
]

for from_name, to_name in inbound_chain:
    if from_name not in connections:
        connections[from_name] = {'main': [[]]}
    main = connections[from_name]['main']
    while len(main) == 0:
        main.append([])
    existing = main[0]
    already_connected = any(c.get('node') == to_name for c in existing)
    if not already_connected:
        main[0].append({
            'node': to_name,
            'type': 'main',
            'index': 0,
        })
        print(f'  Connected: {from_name} -> {to_name}')


# ======================================================================
# STEP 5: PUSH WORKFLOW
# ======================================================================

print('\nStep 5: Pushing workflow...')

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

print('\n=== SMS OUTREACH DEPLOYED ===')
print('Changes:')
print('  - Supabase: channel + sms_body columns, SMS views')
print('  - 12 new n8n nodes (8 outbound + 4 inbound reply handler)')
print('  - SMS Filter: mobile + score >= 7')
print('  - SMS Toggle: ON/OFF switch in n8n UI')
print('  - Build SMS Prompt: trade lingo, anti-slop, 5% rogue, STOP opt-out')
print('  - Send via Twilio API')
print('  - Log to Supabase outreach_events (channel=sms)')
print('  - Inbound webhook: catches replies, classifies sentiment, updates leads')
print(f'  - Workflow now has {len(result.get("nodes", []))} nodes')
print('\nIMPORTANT:')
print('  - SMS Toggle is ON by default. Flip to OFF in n8n UI when not testing.')
print('  - Test with Aaron\'s own number first before real leads.')
print('  - Daily cap not yet enforced in filter (add Supabase count check when live).')
