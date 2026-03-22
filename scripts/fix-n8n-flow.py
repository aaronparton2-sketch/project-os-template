"""Restructure Pipeline A flow:
- ALL scored leads get personalised emails (for Instantly mass outreach)
- Top leads (score 6+) flagged separately for cold calling digest
- Log captures everything

Old: Scorer -> Top 10 -> AI Personaliser -> Log
New: Scorer -> AI Personaliser (all leads) -> Log (all leads)
     The "Top 10" node becomes "Flag Top Leads for Calling" and just adds a flag
"""
import json, urllib.request, sys

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNjE4ODEyNC02YzNiLTQxZDktODdhMS01MDljNmIzOTVkZmMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzcxNjQxODY1fQ.IWzbpXkITsoUvqLLpROW3hQ3PvGo_11D0yLjqRUVaXM'
WF_ID = '3qqw96oRGpyqxt57'

req = urllib.request.Request(
    f'https://aaronparton2.app.n8n.cloud/api/v1/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())

# === 1. Rename and repurpose "Top 10 Leads" to tag leads instead of filtering ===
for node in wf['nodes']:
    if node['name'] == 'Top 10 Leads (Score 6+)':
        node['name'] = 'Tag & Pass All Leads'
        node['parameters']['jsCode'] = '''// Tag all leads: priority_call for score 6+, email_only for the rest.
// ALL leads pass through — none are filtered out.
// Instantly will email everyone. Digest will show priority_call leads for Aaron to phone.
const allItems = $input.all();
if (allItems.length === 0) return [];

return allItems.map(item => {
  const lead = item.json;
  const tier = (lead.score >= 6) ? 'priority_call' : 'email_only';
  return {
    json: {
      ...lead,
      outreach_tier: tier,
    }
  };
}).sort((a, b) => b.json.score - a.json.score);'''

    # Pipeline B version too
    if node['name'] == 'Top 10 Leads (Score 6+)1':
        node['name'] = 'Tag & Pass All Leads B'
        node['parameters']['jsCode'] = '''// Tag all Pipeline B leads: priority_call for score 6+, email_only for the rest.
const allItems = $input.all();
if (allItems.length === 0) return [];

return allItems.map(item => {
  const lead = item.json;
  const tier = (lead.score >= 6) ? 'priority_call' : 'email_only';
  return {
    json: {
      ...lead,
      outreach_tier: tier,
    }
  };
}).sort((a, b) => b.json.score - a.json.score);'''

# === 2. Update Log Pipeline Run to show summary with tiers ===
for node in wf['nodes']:
    if node['name'] == 'Log Pipeline Run':
        node['parameters']['jsCode'] = '''// Log pipeline stats with tier breakdown
const items = $input.all();
if (items.length === 0) return [{ json: { summary: { pipeline: 'no_website', leads_processed: 0, note: 'No leads this run' } } }];

const now = new Date();
const leads = items.map(i => i.json);
const priorityCalls = leads.filter(l => l.outreach_tier === 'priority_call');
const emailOnly = leads.filter(l => l.outreach_tier === 'email_only');

return [{
  json: {
    summary: {
      pipeline: 'no_website',
      run_date: now.toISOString().split('T')[0],
      total_leads: leads.length,
      priority_call_leads: priorityCalls.length,
      email_only_leads: emailOnly.length,
      avg_score: (leads.reduce((s, l) => s + (l.score || 0), 0) / leads.length).toFixed(1),
      timestamp: now.toISOString(),
    },
    priority_call_leads: priorityCalls.map(l => ({
      name: l.business_name,
      phone: l.phone,
      suburb: l.suburb,
      category: l.category,
      score: l.score,
      score_breakdown: l.score_breakdown,
      address_type: l.address_type,
      google_reviews: l.google_reviews,
      call_script: l.call_script || 'No script generated yet',
    })),
    all_leads: leads,
  }
}];'''

    if node['name'] == 'Log Pipeline Run1':
        node['parameters']['jsCode'] = '''// Log Pipeline B stats with tier breakdown
const items = $input.all();
if (items.length === 0) return [{ json: { summary: { pipeline: 'diy_website', leads_processed: 0 } } }];

const now = new Date();
const leads = items.map(i => i.json);
const priorityCalls = leads.filter(l => l.outreach_tier === 'priority_call');

return [{
  json: {
    summary: {
      pipeline: 'diy_website',
      run_date: now.toISOString().split('T')[0],
      total_leads: leads.length,
      priority_call_leads: priorityCalls.length,
      email_only_leads: leads.length - priorityCalls.length,
      timestamp: now.toISOString(),
    },
    priority_call_leads: priorityCalls.map(l => ({
      name: l.business_name,
      phone: l.phone,
      suburb: l.suburb,
      score: l.score,
      diy_platform: l.diy_platform,
      pagespeed_score: l.pagespeed_score,
    })),
    all_leads: leads,
  }
}];'''

# === 3. Fix connections — rename keys to match new node names ===
conns = wf['connections']

# Rename connection keys
if 'Lead Scorer A' in conns:
    targets = conns['Lead Scorer A']['main'][0]
    for t in targets:
        if t['node'] == 'Top 10 Leads (Score 6+)':
            t['node'] = 'Tag & Pass All Leads'

if 'Top 10 Leads (Score 6+)' in conns:
    conns['Tag & Pass All Leads'] = conns.pop('Top 10 Leads (Score 6+)')

if 'Lead Scorer B' in conns:
    targets = conns['Lead Scorer B']['main'][0]
    for t in targets:
        if t['node'] == 'Top 10 Leads (Score 6+)1':
            t['node'] = 'Tag & Pass All Leads B'

if 'Top 10 Leads (Score 6+)1' in conns:
    conns['Tag & Pass All Leads B'] = conns.pop('Top 10 Leads (Score 6+)1')

# Fix downstream connections
if 'Tag & Pass All Leads' in conns:
    targets = conns['Tag & Pass All Leads']['main'][0]
    for t in targets:
        if t['node'] == 'AI Email Personaliser':
            pass  # Already correct

if 'Tag & Pass All Leads B' in conns:
    targets = conns['Tag & Pass All Leads B']['main'][0]
    for t in targets:
        if t['node'] == 'AI Email Personaliser1':
            pass  # Already correct

print("Restructured flow:")
print("  Scorer -> Tag & Pass All Leads (ALL leads, tagged priority_call/email_only)")
print("  -> AI Personaliser (generates emails for ALL)")
print("  -> Log (captures everything with tier breakdown)")

# Push update
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

    # Verify flow
    c = result.get('connections', {})
    for source in ['Lead Scorer A', 'Tag & Pass All Leads', 'AI Email Personaliser']:
        if source in c:
            targets = [t['node'] for t in c[source]['main'][0]]
            print(f"  {source} -> {targets}")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()[:500]}")
    sys.exit(1)
