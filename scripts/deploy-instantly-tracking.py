"""Deploy Instantly email tracking to n8n workflow.

Since Instantly webhooks require Hypergrowth plan (Aaron is on Growth),
we poll the Instantly API V2 every 6 hours to sync email events
(sent, opened, replied, bounced) to the outreach_events table.

Adds nodes:
1. Poll trigger (every 6 hours)
2. Query Instantly API (campaign analytics per lead)
3. Sync to outreach_events (Code node)
"""
import json, urllib.request, sys, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

N8N_API_KEY = os.environ['N8N_API_KEY']
N8N_API_URL = os.environ['N8N_API_URL']
INSTANTLY_API_KEY = os.environ['INSTANTLY_API_KEY']
PIPELINE_PROJECT_REF = os.environ['SUPABASE_PIPELINE_PROJECT_REF']
SUPABASE_ACCESS_TOKEN = os.environ['SUPABASE_ACCESS_TOKEN']
WF_ID = '3qqw96oRGpyqxt57'

req = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': N8N_API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())

# Check if already deployed
existing_names = {n['name'] for n in wf['nodes']}
if 'Poll Instantly Events' in existing_names:
    print('Instantly tracking already deployed, skipping.')
    sys.exit(0)

# ═══════════════════════════════════════════════════════════════
# QUERY INSTANTLY CAMPAIGNS — gets recent lead-level events
# ═══════════════════════════════════════════════════════════════

QUERY_INSTANTLY_CODE = f'''// Poll Instantly API V2 — get campaign analytics for lead-level events
// Runs every 6 hours to sync email events to outreach_events

const API_KEY = '{INSTANTLY_API_KEY}';
const BASE_URL = 'https://api.instantly.ai/api/v2';

// 1. List active campaigns
let campaigns;
try {{
  campaigns = await this.helpers.httpRequest({{
    method: 'GET',
    url: `${{BASE_URL}}/campaigns`,
    headers: {{
      'Authorization': `Bearer ${{API_KEY}}`,
      'Content-Type': 'application/json',
    }},
    qs: {{ limit: 10, status: 'active' }},
    timeout: 15000,
  }});
}} catch (e) {{
  return [{{ json: {{ error: e.message, _events: [] }} }}];
}}

const campaignList = campaigns?.data || campaigns || [];
if (!Array.isArray(campaignList) || campaignList.length === 0) {{
  return [{{ json: {{ _events: [], _message: 'No active campaigns found' }} }}];
}}

// 2. For each campaign, get lead-level status
const allEvents = [];
for (const campaign of campaignList) {{
  const campaignId = campaign.id;
  const campaignName = campaign.name || 'unknown';

  // Get leads with their status
  let skip = 0;
  const limit = 100;
  let hasMore = true;

  while (hasMore) {{
    try {{
      const leads = await this.helpers.httpRequest({{
        method: 'GET',
        url: `${{BASE_URL}}/leads`,
        headers: {{
          'Authorization': `Bearer ${{API_KEY}}`,
          'Content-Type': 'application/json',
        }},
        qs: {{
          campaign_id: campaignId,
          limit: limit,
          skip: skip,
        }},
        timeout: 15000,
      }});

      const leadList = leads?.data || leads || [];
      if (!Array.isArray(leadList) || leadList.length === 0) {{
        hasMore = false;
        break;
      }}

      for (const lead of leadList) {{
        // Map Instantly lead status to our event types
        const email = lead.email || '';
        const status = lead.status || '';
        const leadData = lead.lead_data || {{}};

        // Collect events based on status flags
        if (lead.is_sent || lead.sent_count > 0) {{
          allEvents.push({{
            email: email,
            event_type: 'email_sent',
            campaign_name: campaignName,
            variant: leadData.variant || null,
            personalisation_type: leadData.personalisation_type || null,
            has_humour: leadData.has_humour || false,
            trade_category: leadData.category || null,
          }});
        }}
        if (lead.is_opened || lead.open_count > 0) {{
          allEvents.push({{
            email: email,
            event_type: 'email_opened',
            campaign_name: campaignName,
            variant: leadData.variant || null,
            personalisation_type: leadData.personalisation_type || null,
            has_humour: leadData.has_humour || false,
            trade_category: leadData.category || null,
          }});
        }}
        if (lead.is_replied) {{
          allEvents.push({{
            email: email,
            event_type: 'email_replied',
            campaign_name: campaignName,
            variant: leadData.variant || null,
            personalisation_type: leadData.personalisation_type || null,
            has_humour: leadData.has_humour || false,
            trade_category: leadData.category || null,
          }});
        }}
        if (lead.is_bounced) {{
          allEvents.push({{
            email: email,
            event_type: 'email_bounced',
            campaign_name: campaignName,
            variant: leadData.variant || null,
            personalisation_type: leadData.personalisation_type || null,
            has_humour: leadData.has_humour || false,
            trade_category: leadData.category || null,
          }});
        }}
        if (lead.is_unsubscribed) {{
          allEvents.push({{
            email: email,
            event_type: 'email_unsubscribed',
            campaign_name: campaignName,
            variant: leadData.variant || null,
            personalisation_type: leadData.personalisation_type || null,
            has_humour: leadData.has_humour || false,
            trade_category: leadData.category || null,
          }});
        }}
      }}

      skip += limit;
      if (leadList.length < limit) hasMore = false;
    }} catch (e) {{
      hasMore = false;
    }}
  }}
}}

return [{{ json: {{ _events: allEvents, _count: allEvents.length }} }}];'''

# ═══════════════════════════════════════════════════════════════
# SYNC TO OUTREACH_EVENTS — upserts events to Supabase
# ═══════════════════════════════════════════════════════════════

SYNC_EVENTS_CODE = f'''// Sync Instantly events to outreach_events table
// Uses upsert logic: only insert events that don't already exist

const PROJECT_REF = '{PIPELINE_PROJECT_REF}';
const ACCESS_TOKEN = '{SUPABASE_ACCESS_TOKEN}';
const API_URL = `https://api.supabase.com/v1/projects/${{PROJECT_REF}}/database/query`;

const data = $input.item.json;
const events = data._events || [];

if (events.length === 0) {{
  return [{{ json: {{ _synced: 0, _message: 'No events to sync' }} }}];
}}

let synced = 0;
let skipped = 0;

for (const evt of events) {{
  // Find lead_id by email
  const findQuery = `SELECT id FROM leads WHERE email = '${{evt.email.replace(/'/g, "''")}}' LIMIT 1;`;

  let leadResult;
  try {{
    leadResult = await this.helpers.httpRequest({{
      method: 'POST',
      url: API_URL,
      headers: {{
        'Authorization': `Bearer ${{ACCESS_TOKEN}}`,
        'Content-Type': 'application/json',
      }},
      body: {{ query: findQuery }},
      timeout: 10000,
    }});
  }} catch {{
    skipped++;
    continue;
  }}

  const leadId = leadResult?.[0]?.id;
  if (!leadId) {{
    skipped++;
    continue;
  }}

  // Check if event already exists (prevent duplicates)
  const checkQuery = `SELECT id FROM outreach_events
    WHERE lead_id = '${{leadId}}' AND event_type = '${{evt.event_type}}' AND channel = 'email'
    LIMIT 1;`;

  let existing;
  try {{
    existing = await this.helpers.httpRequest({{
      method: 'POST',
      url: API_URL,
      headers: {{
        'Authorization': `Bearer ${{ACCESS_TOKEN}}`,
        'Content-Type': 'application/json',
      }},
      body: {{ query: checkQuery }},
      timeout: 10000,
    }});
  }} catch {{
    existing = [];
  }}

  if (existing && existing.length > 0) {{
    skipped++;
    continue; // Already recorded
  }}

  // Insert new event
  const variant = evt.variant ? `'${{evt.variant.replace(/'/g, "''")}}'` : 'NULL';
  const persType = evt.personalisation_type ? `'${{evt.personalisation_type}}'` : 'NULL';
  const tradeCat = evt.trade_category ? `'${{evt.trade_category.replace(/'/g, "''")}}'` : 'NULL';
  const humour = evt.has_humour ? 'true' : 'false';

  const insertQuery = `INSERT INTO outreach_events (lead_id, event_type, channel, variant, personalisation_type, has_humour, trade_category)
    VALUES ('${{leadId}}', '${{evt.event_type}}', 'email', ${{variant}}, ${{persType}}, ${{humour}}, ${{tradeCat}});`;

  try {{
    await this.helpers.httpRequest({{
      method: 'POST',
      url: API_URL,
      headers: {{
        'Authorization': `Bearer ${{ACCESS_TOKEN}}`,
        'Content-Type': 'application/json',
      }},
      body: {{ query: insertQuery }},
      timeout: 10000,
    }});
    synced++;
  }} catch {{
    skipped++;
  }}
}}

return [{{ json: {{ _synced: synced, _skipped: skipped, _total: events.length }} }}];'''

# ═══════════════════════════════════════════════════════════════
# ADD NODES
# ═══════════════════════════════════════════════════════════════

# Position below the weekly digest section
sticky5_pos = [0, 0]
for node in wf['nodes']:
    if node['name'] == 'Sticky Note5':
        sticky5_pos = node.get('position', [0, 1200])
        break

base_y = sticky5_pos[1] + 300

wf['nodes'].extend([
    {
        'name': 'Poll Instantly Events',
        'type': 'n8n-nodes-base.scheduleTrigger',
        'typeVersion': 1.2,
        'position': [sticky5_pos[0], base_y],
        'parameters': {
            'rule': {
                'interval': [{'field': 'hours', 'hoursInterval': 6}]
            }
        },
    },
    {
        'name': 'Query Instantly API',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [sticky5_pos[0] + 200, base_y],
        'parameters': {
            'mode': 'runOnceForAllItems',
            'jsCode': QUERY_INSTANTLY_CODE,
        },
    },
    {
        'name': 'Sync Events to Supabase',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [sticky5_pos[0] + 400, base_y],
        'parameters': {
            'mode': 'runOnceForAllItems',
            'jsCode': SYNC_EVENTS_CODE,
        },
    },
    {
        'name': 'Sticky Note6',
        'type': 'n8n-nodes-base.stickyNote',
        'typeVersion': 1,
        'position': [sticky5_pos[0] - 30, base_y - 60],
        'parameters': {
            'content': '## Section 7: Instantly Event Tracking\nPolls Instantly API every 6 hours.\nSyncs email events (sent/opened/replied/bounced)\nto outreach_events for performance views.',
            'width': 700,
            'height': 200,
        },
    },
])

# Wire connections
wf['connections']['Poll Instantly Events'] = {
    'main': [[{'node': 'Query Instantly API', 'type': 'main', 'index': 0}]]
}
wf['connections']['Query Instantly API'] = {
    'main': [[{'node': 'Sync Events to Supabase', 'type': 'main', 'index': 0}]]
}

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
    print(f'Instantly tracking deployed ({len(result.get("nodes", []))} nodes)')
except urllib.error.HTTPError as e:
    print(f'Error {e.code}: {e.read().decode()[:500]}')
    sys.exit(1)
