"""Deploy weekly performance digest to n8n workflow.

Adds nodes:
1. Weekly Cron trigger (Sunday 6pm AWST)
2. Query Performance Data (Code) - queries Supabase performance views
3. Build Performance Email (Code) - formats into readable HTML email
4. Sticky Note for the section

All added to the existing consolidated workflow.
"""
import json, urllib.request, sys, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

N8N_API_KEY = os.environ['N8N_API_KEY']
N8N_API_URL = os.environ['N8N_API_URL']
PIPELINE_PROJECT_REF = os.environ['SUPABASE_PIPELINE_PROJECT_REF']
SUPABASE_ACCESS_TOKEN = os.environ['SUPABASE_ACCESS_TOKEN']
WF_ID = '3qqw96oRGpyqxt57'

req = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': N8N_API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())

# ═══════════════════════════════════════════════════════════════
# QUERY PERFORMANCE DATA
# ═══════════════════════════════════════════════════════════════

QUERY_PERF_CODE = f'''// Query Performance Data — pulls from Supabase views
const PROJECT_REF = '{PIPELINE_PROJECT_REF}';
const ACCESS_TOKEN = '{SUPABASE_ACCESS_TOKEN}';
const API_URL = `https://api.supabase.com/v1/projects/${{PROJECT_REF}}/database/query`;

async function query(sql) {{
  try {{
    return await this.helpers.httpRequest({{
      method: 'POST',
      url: API_URL,
      headers: {{
        'Authorization': `Bearer ${{ACCESS_TOKEN}}`,
        'Content-Type': 'application/json',
      }},
      body: {{ query: sql }},
      timeout: 15000,
    }});
  }} catch (e) {{
    return [];
  }}
}}

// Pull all performance data
const [weekly, variants, trades, humour, personalisation] = await Promise.all([
  query("SELECT * FROM weekly_outreach_summary WHERE week >= NOW() - INTERVAL '7 days' LIMIT 1;"),
  query("SELECT * FROM email_variant_performance ORDER BY reply_rate DESC NULLS LAST;"),
  query("SELECT * FROM trade_performance ORDER BY email_reply_rate DESC NULLS LAST LIMIT 10;"),
  query("SELECT * FROM humour_ab_test;"),
  query("SELECT * FROM personalisation_performance;"),
]);

return [{{
  json: {{
    weekly: weekly || [],
    variants: variants || [],
    trades: trades || [],
    humour: humour || [],
    personalisation: personalisation || [],
    generated_at: new Date().toISOString(),
  }}
}}];'''

# ═══════════════════════════════════════════════════════════════
# BUILD PERFORMANCE EMAIL
# ═══════════════════════════════════════════════════════════════

BUILD_PERF_EMAIL_CODE = r"""// Build Performance Email — formats data into readable HTML
const data = $input.item.json;
const w = data.weekly?.[0] || {};

const now = new Date();
const weekStart = new Date(now);
weekStart.setDate(weekStart.getDate() - 7);
const dateRange = `${weekStart.toLocaleDateString('en-AU')} - ${now.toLocaleDateString('en-AU')}`;

let html = `<h2>Weekly Outreach Report</h2><p style="color:#666">${dateRange}</p>`;

// Email summary
html += `<h3>Emails</h3><table style="border-collapse:collapse;width:100%">
<tr style="background:#f0f0f0"><td style="padding:8px"><b>Sent</b></td><td style="padding:8px">${w.emails_sent || 0}</td></tr>
<tr><td style="padding:8px"><b>Opened</b></td><td style="padding:8px">${w.emails_opened || 0} (${w.emails_sent ? Math.round((w.emails_opened||0)/w.emails_sent*100) : 0}%)</td></tr>
<tr style="background:#f0f0f0"><td style="padding:8px"><b>Replied</b></td><td style="padding:8px">${w.emails_replied || 0} (${w.emails_sent ? Math.round((w.emails_replied||0)/w.emails_sent*100) : 0}%)</td></tr>
<tr><td style="padding:8px"><b>Bounced</b></td><td style="padding:8px">${w.emails_bounced || 0}</td></tr>
</table>`;

// Top variant
if (data.variants?.length > 0) {
  const top = data.variants[0];
  html += `<h3>Top Performing Variant</h3><p><b>${top.variant || 'unknown'}</b>: ${top.reply_rate || 0}% reply rate (${top.sent || 0} sent)</p>`;

  html += `<table style="border-collapse:collapse;width:100%"><tr style="background:#f0f0f0">
  <th style="padding:6px;text-align:left">Variant</th><th style="padding:6px">Sent</th><th style="padding:6px">Replied</th><th style="padding:6px">Rate</th></tr>`;
  for (const v of data.variants) {
    html += `<tr><td style="padding:6px">${v.variant}</td><td style="padding:6px;text-align:center">${v.sent}</td><td style="padding:6px;text-align:center">${v.replied}</td><td style="padding:6px;text-align:center">${v.reply_rate || 0}%</td></tr>`;
  }
  html += `</table>`;
}

// Top trade
if (data.trades?.length > 0) {
  const topTrade = data.trades[0];
  html += `<h3>Top Performing Trade</h3><p><b>${topTrade.trade_category || 'unknown'}</b>: ${topTrade.email_reply_rate || 0}% reply rate (${topTrade.emails_sent || 0} sent)</p>`;
}

// Humour A/B
if (data.humour?.length > 0) {
  html += `<h3>Humour A/B Test</h3><table style="border-collapse:collapse;width:100%">
  <tr style="background:#f0f0f0"><th style="padding:6px;text-align:left">Type</th><th style="padding:6px">Sent</th><th style="padding:6px">Replied</th><th style="padding:6px">Rate</th></tr>`;
  for (const h of data.humour) {
    const label = h.has_humour ? 'With humour' : 'Without humour';
    html += `<tr><td style="padding:6px">${label}</td><td style="padding:6px;text-align:center">${h.sent}</td><td style="padding:6px;text-align:center">${h.replied}</td><td style="padding:6px;text-align:center">${h.reply_rate || 0}%</td></tr>`;
  }
  html += `</table>`;
}

// Personalisation comparison
if (data.personalisation?.length > 0) {
  html += `<h3>Social vs Standard</h3><table style="border-collapse:collapse;width:100%">
  <tr style="background:#f0f0f0"><th style="padding:6px;text-align:left">Type</th><th style="padding:6px">Sent</th><th style="padding:6px">Replied</th><th style="padding:6px">Rate</th></tr>`;
  for (const p of data.personalisation) {
    html += `<tr><td style="padding:6px">${p.personalisation_type}</td><td style="padding:6px;text-align:center">${p.sent}</td><td style="padding:6px;text-align:center">${p.replied}</td><td style="padding:6px;text-align:center">${p.reply_rate || 0}%</td></tr>`;
  }
  html += `</table>`;
}

// Calls
if ((w.calls_made || 0) > 0) {
  html += `<h3>Calls</h3><p>Made: ${w.calls_made} | Interested: ${w.calls_interested || 0} | Not interested: ${w.calls_not_interested || 0}</p>`;
}

// Action items
html += `<h3>Action Items</h3><ul>`;
if (data.variants?.length > 0) {
  const worst = data.variants[data.variants.length - 1];
  if (worst.sent >= 20 && (worst.reply_rate || 0) === 0) {
    html += `<li>Consider killing <b>${worst.variant}</b> - 0% reply rate after ${worst.sent} sends</li>`;
  }
  const best = data.variants[0];
  if ((best.reply_rate || 0) > 10) {
    html += `<li>Double down on <b>${best.variant}</b> - ${best.reply_rate}% reply rate</li>`;
  }
}
if ((w.emails_bounced || 0) > (w.emails_sent || 1) * 0.05) {
  html += `<li>Bounce rate above 5% - check email verification</li>`;
}
html += `<li>Review and update trade lingo if any emails felt off</li>`;
html += `</ul>`;

html += `<p style="color:#999;font-size:12px">Generated ${data.generated_at}</p>`;

return [{
  json: {
    subject: `Weekly Outreach Report - ${dateRange}`,
    html: html,
    to: 'aaron@myceliumai.com.au',
  }
}];"""

# ═══════════════════════════════════════════════════════════════
# ADD NODES TO WORKFLOW
# ═══════════════════════════════════════════════════════════════

# Find a good position (below the health check section)
health_pos = [0, 0]
for node in wf['nodes']:
    if node['name'] == 'Sticky Note4':
        health_pos = node.get('position', [0, 800])
        break

base_y = health_pos[1] + 400

# Check if already deployed
existing_names = {n['name'] for n in wf['nodes']}
if 'Weekly 6pm AWST' in existing_names:
    print('Weekly digest already deployed, skipping.')
    sys.exit(0)

wf['nodes'].extend([
    {
        'name': 'Weekly 6pm AWST',
        'type': 'n8n-nodes-base.scheduleTrigger',
        'typeVersion': 1.2,
        'position': [health_pos[0], base_y],
        'parameters': {
            'rule': {
                'interval': [{'triggerAtDay': 0, 'triggerAtHour': 10}]  # Sunday 10:00 UTC = 6pm AWST
            }
        },
    },
    {
        'name': 'Query Performance Data',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [health_pos[0] + 200, base_y],
        'parameters': {
            'mode': 'runOnceForAllItems',
            'jsCode': QUERY_PERF_CODE,
        },
    },
    {
        'name': 'Build Performance Email',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [health_pos[0] + 400, base_y],
        'parameters': {
            'mode': 'runOnceForAllItems',
            'jsCode': BUILD_PERF_EMAIL_CODE,
        },
    },
    {
        'name': 'Sticky Note5',
        'type': 'n8n-nodes-base.stickyNote',
        'typeVersion': 1,
        'position': [health_pos[0] - 30, base_y - 60],
        'parameters': {
            'content': '## Section 6: Weekly Performance Digest\nSunday 6pm AWST - queries outreach_events views,\nformats into HTML email with variant/trade/humour stats.',
            'width': 700,
            'height': 200,
        },
    },
])

# Wire connections
wf['connections']['Weekly 6pm AWST'] = {
    'main': [[{'node': 'Query Performance Data', 'type': 'main', 'index': 0}]]
}
wf['connections']['Query Performance Data'] = {
    'main': [[{'node': 'Build Performance Email', 'type': 'main', 'index': 0}]]
}
# Note: Build Performance Email outputs email data but doesn't have a send node yet.
# The daily digest already has a Gmail send pattern we can extend later,
# or Aaron can connect it to the existing email send mechanism.

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
    print(f'Weekly digest deployed ({len(result.get("nodes", []))} nodes)')
except urllib.error.HTTPError as e:
    print(f'Error {e.code}: {e.read().decode()[:500]}')
    sys.exit(1)
