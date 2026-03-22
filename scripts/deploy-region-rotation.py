"""Deploy auto-region rotation to n8n workflow.

Changes:
1. Add Region Picker node (queries Supabase for next region)
2. Make Apify search dynamic (uses region from picker)
3. Update Filter & Normalise to use dynamic state
4. Add national postcode classifier to scorers
5. Add Update Region Status node at end of pipeline
6. Update Supabase Store to include region field
7. Rewire connections: Triggers -> Region Picker -> Apify -> rest of pipeline
"""
import json, urllib.request, sys, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

N8N_API_KEY = os.environ['N8N_API_KEY']
N8N_API_URL = os.environ['N8N_API_URL']
OPENAI_KEY = os.environ['OPENAI_API_KEY']
APIFY_TOKEN = os.environ['APIFY_API_TOKEN']
PIPELINE_PROJECT_REF = os.environ['SUPABASE_PIPELINE_PROJECT_REF']
SUPABASE_ACCESS_TOKEN = os.environ['SUPABASE_ACCESS_TOKEN']
WF_ID = '3qqw96oRGpyqxt57'

req = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': N8N_API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())

# ═══════════════════════════════════════════════════════════════
# REGION PICKER — queries Supabase Management API for next region
# ═══════════════════════════════════════════════════════════════

REGION_PICKER_CODE = f'''// Region Picker — queries Supabase for next region to scrape
// Returns region data for all downstream nodes to use

const PROJECT_REF = '{PIPELINE_PROJECT_REF}';
const ACCESS_TOKEN = '{SUPABASE_ACCESS_TOKEN}';
const API_URL = `https://api.supabase.com/v1/projects/${{PROJECT_REF}}/database/query`;

// Find next available region
const pickQuery = `SELECT id, name, state, priority, scrape_count
  FROM regions
  WHERE status IN ('pending', 'scraped')
  AND (cooldown_until IS NULL OR cooldown_until < NOW())
  ORDER BY priority ASC, last_scraped_at ASC NULLS FIRST
  LIMIT 1;`;

const pickResult = await this.helpers.httpRequest({{
  method: 'POST',
  url: API_URL,
  headers: {{
    'Authorization': `Bearer ${{ACCESS_TOKEN}}`,
    'Content-Type': 'application/json',
  }},
  body: {{ query: pickQuery }},
  timeout: 15000,
}});

if (!pickResult || pickResult.length === 0) {{
  // No regions available — all exhausted or on cooldown
  return [{{ json: {{ _no_region: true, _skip: true }} }}];
}}

const region = pickResult[0];

// Mark region as in_progress
const markQuery = `UPDATE regions SET status = 'in_progress', updated_at = NOW() WHERE id = ${{region.id}};`;
await this.helpers.httpRequest({{
  method: 'POST',
  url: API_URL,
  headers: {{
    'Authorization': `Bearer ${{ACCESS_TOKEN}}`,
    'Content-Type': 'application/json',
  }},
  body: {{ query: markQuery }},
  timeout: 10000,
}});

return [{{
  json: {{
    _region_id: region.id,
    _region_name: region.name,
    _region_state: region.state,
    _region_priority: region.priority,
    _region_scrape_count: region.scrape_count,
  }}
}}];'''

# ═══════════════════════════════════════════════════════════════
# NATIONAL POSTCODE CLASSIFIER — replaces Perth-only version
# ═══════════════════════════════════════════════════════════════

NATIONAL_POSTCODE_FN = '''
// National postcode classifier — all Australian states
const CBD_POSTCODES = new Set([
  // WA
  '6000', '6001', '6003', '6004', '6005',
  // NSW
  '2000', '2001',
  // VIC
  '3000', '3001',
  // QLD
  '4000', '4001',
  // SA
  '5000', '5001',
  // TAS
  '7000', '7001',
  // NT
  '0800', '0801',
  // ACT
  '2600', '2601',
]);
const COMMERCIAL_POSTCODES = new Set([
  // WA
  '6017', '6021', '6053', '6054', '6055', '6065', '6090',
  '6100', '6104', '6105', '6106', '6107', '6109', '6112',
  '6154', '6155', '6163', '6164', '6165', '6166', '6168',
  // NSW (major industrial)
  '2020', '2164', '2165', '2190', '2200',
  // VIC (major industrial)
  '3175', '3029', '3030', '3064',
  // QLD
  '4108', '4110', '4172', '4173',
]);
function classifyPostcode(pc) {
  if (!pc) return 'unknown';
  pc = String(pc).trim();
  if (CBD_POSTCODES.has(pc)) return 'cbd';
  if (COMMERCIAL_POSTCODES.has(pc)) return 'commercial';
  return 'residential';
}'''

# ═══════════════════════════════════════════════════════════════
# UPDATE REGION STATUS — runs at end of pipeline
# ═══════════════════════════════════════════════════════════════

UPDATE_REGION_CODE = f'''// Update Region Status — marks region as scraped/exhausted after pipeline run
const items = $input.all();
if (items.length === 0) return items;

// Get region ID from the first item (all items have same region)
const regionId = items[0].json._region_id || items[0].json.region_id;
if (!regionId) return items; // no region tracking

const totalLeads = items.length;
const newLeads = items.filter(i => i.json._db_status === 'stored').length;
const dupes = items.filter(i => i.json._db_status === 'duplicate').length;

const PROJECT_REF = '{PIPELINE_PROJECT_REF}';
const ACCESS_TOKEN = '{SUPABASE_ACCESS_TOKEN}';
const API_URL = `https://api.supabase.com/v1/projects/${{PROJECT_REF}}/database/query`;

// Determine status
let newStatus = 'scraped';
let cooldownClause = '';
if (newLeads < 5) {{
  newStatus = 'exhausted';
  cooldownClause = ", cooldown_until = NOW() + INTERVAL '90 days'";
}}

const query = `UPDATE regions SET
  status = '${{newStatus}}',
  leads_found = leads_found + ${{totalLeads}},
  new_leads_found = ${{newLeads}},
  scrape_count = scrape_count + 1,
  last_scraped_at = NOW(),
  updated_at = NOW()
  ${{cooldownClause}}
  WHERE id = ${{regionId}};`;

try {{
  await this.helpers.httpRequest({{
    method: 'POST',
    url: API_URL,
    headers: {{
      'Authorization': `Bearer ${{ACCESS_TOKEN}}`,
      'Content-Type': 'application/json',
    }},
    body: {{ query }},
    timeout: 10000,
  }});
}} catch (err) {{
  // Don't fail the pipeline if region update fails
}}

return [{{
  json: {{
    headline: `${{totalLeads}} leads | ${{newLeads}} new | ${{dupes}} dupes | Region: ${{items[0].json._region_name || 'unknown'}} (${{newStatus}})`,
    region_status: newStatus,
    total_leads: totalLeads,
    new_leads: newLeads,
    duplicates: dupes,
  }}
}}];'''

# ═══════════════════════════════════════════════════════════════
# APPLY CHANGES TO WORKFLOW
# ═══════════════════════════════════════════════════════════════

fixes = []

# 1. Add Region Picker node
wf['nodes'].append({
    'name': 'Region Picker',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [-350, -176],
    'parameters': {
        'mode': 'runOnceForAllItems',
        'jsCode': REGION_PICKER_CODE,
    },
})
fixes.append('Region Picker (new)')

# 2. Update Apify node — make search dynamic using expression
for node in wf['nodes']:
    name = node['name']

    if name == 'Apify: Google Maps (No Website)':
        # Read current search terms from the existing config
        current_body = json.loads(node['parameters'].get('jsonBody', '{}'))
        search_terms = current_body.get('searchStringsArray', [])
        # Strip " Perth WA" from existing terms to get base categories
        base_categories = []
        for term in search_terms:
            clean = term.replace(' Perth WA', '').replace(' Perth', '').strip()
            if clean and clean not in base_categories:
                base_categories.append(clean)

        # Change URL to use expression for the body
        # The Apify node will read region from the previous node's output
        node['parameters']['url'] = f'https://api.apify.com/v2/acts/compass~crawler-google-places/run-sync-get-dataset-items?token={APIFY_TOKEN}'
        # Use n8n expression to build dynamic body
        node['parameters']['jsonBody'] = '={{ JSON.stringify({ searchStringsArray: ' + json.dumps(base_categories) + '.map(cat => cat + " " + $json._region_name), locationQuery: $json._region_name, maxCrawledPlacesPerSearch: 50, language: "en", deeperCityScrape: false, onlyDataFromSearchPage: false, skipClosedPlaces: true }) }}'
        fixes.append('Apify: dynamic region search')

    # 3. Update Filter & Normalise — dynamic state + pass region data
    elif name == 'Filter & Normalise':
        code = node['parameters']['jsCode']
        # Replace hardcoded state
        code = code.replace("state: 'WA'", "state: (d._region_state || 'WA')")
        # Add region fields to output
        code = code.replace(
            "      place_id: d.placeId || '',",
            "      place_id: d.placeId || '',\n      region: d._region_name || '',\n      _region_id: d._region_id || null,\n      _region_name: d._region_name || '',\n      _region_state: d._region_state || 'WA',"
        )
        # Replace Perth-only postcode classifier with national version
        old_classifier_start = "const CBD_POSTCODES = new Set(["
        if old_classifier_start in code:
            # Find end of classifyPostcode function
            idx_start = code.index(old_classifier_start)
            idx_end = code.index("return 'residential';\n}", idx_start) + len("return 'residential';\n}")
            code = code[:idx_start] + NATIONAL_POSTCODE_FN.strip() + code[idx_end:]
        node['parameters']['jsCode'] = code
        fixes.append('Filter & Normalise (dynamic state + national postcodes)')

    elif name == 'Filter & Normalise (Has Website)':
        code = node['parameters']['jsCode']
        code = code.replace("state: 'WA'", "state: (d._region_state || 'WA')")
        old_classifier_start = "const CBD_POSTCODES = new Set(["
        if old_classifier_start in code:
            idx_start = code.index(old_classifier_start)
            idx_end = code.index("return 'residential';\n}", idx_start) + len("return 'residential';\n}")
            code = code[:idx_start] + NATIONAL_POSTCODE_FN.strip() + code[idx_end:]
        node['parameters']['jsCode'] = code
        fixes.append('Filter & Normalise Has Website (dynamic state + national postcodes)')

    # 4. Update Lead Scorers — national postcode classifier
    elif name in ('Lead Scorer A', 'Lead Scorer B'):
        code = node['parameters']['jsCode']
        old_classifier_start = "const CBD_POSTCODES = new Set(["
        if old_classifier_start in code:
            idx_start = code.index(old_classifier_start)
            idx_end = code.index("return 'residential';\n}", idx_start) + len("return 'residential';\n}")
            code = code[:idx_start] + NATIONAL_POSTCODE_FN.strip() + code[idx_end:]
            node['parameters']['jsCode'] = code
            fixes.append(f'{name} (national postcodes)')

    # 5. Update Supabase Store — add region field
    elif name == 'Supabase: Store Leads':
        code = node['parameters']['jsCode']
        if "region:" not in code:
            code = code.replace(
                "  status: 'new',",
                "  region: lead.region || lead._region_name || null,\n  status: 'new',"
            )
            node['parameters']['jsCode'] = code
            fixes.append('Supabase: Store Leads (region field)')

# 6. Add Update Region Status node
wf['nodes'].append({
    'name': 'Update Region Status',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [1700, -176],
    'parameters': {
        'mode': 'runOnceForAllItems',
        'jsCode': UPDATE_REGION_CODE,
    },
})
fixes.append('Update Region Status (new)')

# ═══════════════════════════════════════════════════════════════
# REWIRE CONNECTIONS
# ═══════════════════════════════════════════════════════════════

conns = wf['connections']

# Triggers -> Region Picker -> Apify
conns['Daily 6am AWST'] = {
    'main': [[{'node': 'Region Picker', 'type': 'main', 'index': 0}]]
}
conns['Manual Trigger'] = {
    'main': [[{'node': 'Region Picker', 'type': 'main', 'index': 0}]]
}
conns['Region Picker'] = {
    'main': [[{'node': 'Apify: Google Maps (No Website)', 'type': 'main', 'index': 0}]]
}

# Log Pipeline Run -> Update Region Status (end of Pipeline A)
conns['Log Pipeline Run'] = {
    'main': [[{'node': 'Update Region Status', 'type': 'main', 'index': 0}]]
}

fixes.append('Connections rewired (Triggers -> Region Picker -> Apify)')

# ═══════════════════════════════════════════════════════════════
# PUSH
# ═══════════════════════════════════════════════════════════════

print(f'Applied {len(fixes)} changes:')
for f in fixes:
    print(f'  - {f}')

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
    sys.exit(1)
