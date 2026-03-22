"""Update the n8n Automated Lead Pipeline workflow with:
1. Website Checker node (between Filter & Normalise and Lead Scorer A)
2. Postcode classifier in Filter & Normalise
3. Residential scoring signal in Lead Scorer A
"""
import json, urllib.request, sys

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNjE4ODEyNC02YzNiLTQxZDktODdhMS01MDljNmIzOTVkZmMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzcxNjQxODY1fQ.IWzbpXkITsoUvqLLpROW3hQ3PvGo_11D0yLjqRUVaXM"
BASE = "https://aaronparton2.app.n8n.cloud/api/v1"
WF_ID = "3qqw96oRGpyqxt57"

# Get current workflow
req = urllib.request.Request(
    f"{BASE}/workflows/{WF_ID}",
    headers={"X-N8N-API-KEY": API_KEY, "accept": "application/json"}
)
wf = json.loads(urllib.request.urlopen(req).read())
print(f"Loaded workflow: {wf['name']} ({len(wf['nodes'])} nodes)")

# === 1. Add Website Checker node ===
WEBSITE_CHECKER_CODE = r"""// Website Existence Checker - Layer 1: URL Pattern Check
// Checks if "no website" leads actually have a website.
// If found: reclassify to Pipeline B (diy_website).

function toSlug(name) {
  return (name || '').toLowerCase()
    .replace(/[\u2019\u2018'`]/g, '')
    .replace(/&/g, 'and')
    .replace(/\bpty\b/g, '').replace(/\bltd\b/g, '')
    .replace(/[^a-z0-9]+/g, '').trim();
}

async function checkUrlPatterns(businessName, suburb) {
  const slug = toSlug(businessName);
  if (!slug || slug.length < 3) return { found: false };
  const suburbSlug = toSlug(suburb);

  const patterns = [`${slug}.com.au`, `${slug}.au`, `${slug}.com`];
  if (suburbSlug && slug.length < 20) {
    patterns.push(`${slug}${suburbSlug}.com.au`);
    patterns.push(`${slug}perth.com.au`);
  }

  for (const domain of patterns) {
    for (const proto of ['https', 'http']) {
      try {
        const resp = await fetch(`${proto}://${domain}`, {
          method: 'HEAD', redirect: 'follow',
          signal: AbortSignal.timeout(5000),
        });
        if (resp.ok || (resp.status >= 300 && resp.status < 400)) {
          const html = await fetch(`${proto}://${domain}`, {
            redirect: 'follow', signal: AbortSignal.timeout(5000),
          }).then(r => r.text());
          const isParked = /domain.{0,20}(for sale|available|expired)|buy this domain|parked.{0,10}(domain|page)|coming soon|under construction/i.test(html);
          if (!isParked && html.length > 2000) {
            return { found: true, url: `${proto}://${domain}`, method: 'url_pattern' };
          }
        }
      } catch (e) { continue; }
    }
  }
  return { found: false };
}

const results = [];
for (const item of $input.all()) {
  const lead = item.json;
  if (lead.website && !lead.website.includes('facebook.com')) {
    results.push({ json: { ...lead, website_verified: true, website_check_method: 'already_has_website' } });
    continue;
  }
  const check = await checkUrlPatterns(lead.business_name, lead.suburb);
  if (check.found) {
    results.push({ json: { ...lead, website: check.url, website_verified: true,
      website_check_method: check.method, website_check_url: check.url, pipeline: 'diy_website' } });
  } else {
    results.push({ json: { ...lead, website_verified: true, website_check_method: 'none_found', pipeline: 'no_website' } });
  }
}
return results;"""

# Check if Website Checker already exists
checker_exists = any(n['name'] == 'Website Checker' for n in wf['nodes'])
if not checker_exists:
    wf['nodes'].append({
        "parameters": {"jsCode": WEBSITE_CHECKER_CODE},
        "id": "website-checker-1",
        "name": "Website Checker",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [232, -176]
    })
    print("Added Website Checker node")
else:
    print("Website Checker already exists")

# === 2. Add Postcode Classifier to Filter & Normalise ===
POSTCODE_CLASSIFIER = """// --- Postcode Classifier (credit: Aaron's girlfriend) ---
const CBD_POSTCODES = new Set(['6000', '6001', '6003', '6004', '6005']);
const COMMERCIAL_POSTCODES = new Set([
  '6017', '6021', '6053', '6054', '6055', '6065', '6090',
  '6100', '6104', '6105', '6106', '6107', '6109', '6112',
  '6154', '6155', '6163', '6164', '6165', '6166', '6168'
]);
function classifyPostcode(pc) {
  if (!pc) return 'unknown';
  pc = String(pc).trim();
  if (CBD_POSTCODES.has(pc)) return 'cbd';
  if (COMMERCIAL_POSTCODES.has(pc)) return 'commercial';
  return 'residential';
}
// --- End Postcode Classifier ---

"""

for node in wf['nodes']:
    if node['name'] == 'Filter & Normalise':
        code = node['parameters'].get('jsCode', '')
        if 'classifyPostcode' not in code:
            code = POSTCODE_CLASSIFIER + code
            # Add address_type to normalised output
            if 'address_type' not in code:
                code = code.replace(
                    "pipeline: 'no_website'",
                    "pipeline: 'no_website',\n      address_type: classifyPostcode(postcode)"
                )
            node['parameters']['jsCode'] = code
            print(f"Updated Filter & Normalise with postcode classifier")
        else:
            print("Filter & Normalise already has postcode classifier")

# === 3. Update Lead Scorer A with residential signal ===
RESIDENTIAL_SIGNAL = """
  // Signal 8: Residential address (credit: Aaron's girlfriend)
  if (lead.address_type === 'residential') {
    score += 2;
    breakdown.residential = '+2 (residential address - likely owner-operated)';
  }
"""

for node in wf['nodes']:
    if node['name'] == 'Lead Scorer A':
        code = node['parameters'].get('jsCode', '')
        if 'residential' not in code and 'address_type' not in code:
            code = code.replace(
                "return { ...lead, score: Math.min(score, 10), score_breakdown: breakdown };",
                RESIDENTIAL_SIGNAL + "\n  return { ...lead, score: Math.min(score, 10), score_breakdown: breakdown };"
            )
            node['parameters']['jsCode'] = code
            print("Updated Lead Scorer A with residential signal")
        else:
            print("Lead Scorer A already has residential signal")

# === 4. Rewire connections ===
# Old: Filter & Normalise -> Lead Scorer A
# New: Filter & Normalise -> Website Checker -> Lead Scorer A

if not checker_exists:
    wf['connections']['Filter & Normalise'] = {
        "main": [[{"node": "Website Checker", "type": "main", "index": 0}]]
    }
    wf['connections']['Website Checker'] = {
        "main": [[{"node": "Lead Scorer A", "type": "main", "index": 0}]]
    }
    print("Rewired: Filter & Normalise -> Website Checker -> Lead Scorer A")

# === 5. Push updated workflow ===
# n8n PUT only accepts specific fields
allowed = {'name', 'nodes', 'connections', 'settings'}
wf = {k: v for k, v in wf.items() if k in allowed}

data = json.dumps(wf).encode()
req = urllib.request.Request(
    f"{BASE}/workflows/{WF_ID}",
    data=data,
    headers={"Content-Type": "application/json", "X-N8N-API-KEY": API_KEY},
    method='PUT'
)
try:
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    print(f"\nWorkflow updated successfully! ({len(result.get('nodes', []))} nodes)")

    # Verify connections
    conns = result.get('connections', {})
    if 'Filter & Normalise' in conns:
        targets = conns['Filter & Normalise']['main'][0]
        print(f"Filter & Normalise -> {[t['node'] for t in targets]}")
    if 'Website Checker' in conns:
        targets = conns['Website Checker']['main'][0]
        print(f"Website Checker -> {[t['node'] for t in targets]}")
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"Error {e.code}: {error_body[:500]}")
    sys.exit(1)
