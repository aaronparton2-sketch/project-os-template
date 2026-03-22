"""Fix all n8n Pipeline A/B code nodes:
1. Filter & Normalise: d.url is Google Maps URL, not business website — only check d.website
2. Filter & Normalise (Has Website): same fix
3. Top 10 Leads: loosen filter for testing (score 3+ instead of 6+, no email required)
"""
import json, urllib.request, sys

API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNjE4ODEyNC02YzNiLTQxZDktODdhMS01MDljNmIzOTVkZmMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzcxNjQxODY1fQ.IWzbpXkITsoUvqLLpROW3hQ3PvGo_11D0yLjqRUVaXM'
WF_ID = '3qqw96oRGpyqxt57'

req = urllib.request.Request(
    f'https://aaronparton2.app.n8n.cloud/api/v1/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())

fixes = []

POSTCODE_CLASSIFIER = '''const CBD_POSTCODES = new Set(['6000', '6001', '6003', '6004', '6005']);
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
'''

FILTER_NORMALISE_A = POSTCODE_CLASSIFIER + '''
// Filter & Normalise - Pipeline A (No Website leads)
// compass/crawler-google-places fields:
//   title, website, url (Google Maps URL - NOT the business website!),
//   phone, phoneUnformatted, address, city, neighborhood, postalCode,
//   categoryName, totalScore, reviewsCount, placeId, email, reviews

const items = $input.all();
if (items.length === 0) return [];

const filtered = items.filter(item => {
  const d = item.json;
  // ONLY check d.website - d.url is the Google Maps listing URL (every biz has one)
  const bizWebsite = (d.website || '').toLowerCase().trim();
  // Keep if: no website, or website is just Facebook
  return !bizWebsite || bizWebsite.includes('facebook.com');
});

return filtered.map(item => {
  const d = item.json;
  const bizWebsite = (d.website || '').toLowerCase().trim();
  const pc = (d.postalCode || d.postcode || '').trim();
  const email = d.email || '';
  const phone = (d.phone || d.phoneUnformatted || '').trim();
  const reviewText = (d.reviews && d.reviews[0] && d.reviews[0].text)
    ? d.reviews[0].text.substring(0, 200) : '';

  return {
    json: {
      business_name: (d.title || d.name || '').trim(),
      phone: phone,
      email: email,
      category: (d.categoryName || d.category || '').trim(),
      address: (d.address || d.street || '').trim(),
      suburb: (d.city || d.neighborhood || d.suburb || '').trim(),
      postcode: pc,
      state: 'WA',
      website: bizWebsite,
      pipeline: 'no_website',
      address_type: classifyPostcode(pc),
      source: 'google_maps',
      google_reviews: parseInt(d.reviewsCount || d.reviews || 0) || 0,
      google_rating: parseFloat(d.totalScore || d.rating || 0) || null,
      website_is_facebook: bizWebsite.includes('facebook.com'),
      top_review_quote: reviewText,
      found_on_sources: ['google_maps'],
      email_source: email ? 'google_maps' : null,
      email_source_url: d.url || '',
      place_id: d.placeId || '',
      abn: null,
    }
  };
});'''

FILTER_NORMALISE_B = POSTCODE_CLASSIFIER + '''
// Filter & Normalise - Pipeline B (Has Website leads)
// ONLY check d.website - d.url is the Google Maps listing URL
const items = $input.all();
if (items.length === 0) return [];

return items.filter(item => {
  const d = item.json;
  const bizWebsite = (d.website || '').toLowerCase().trim();
  return bizWebsite && !bizWebsite.includes('facebook.com');
}).map(item => {
  const d = item.json;
  const pc = (d.postalCode || d.postcode || '').trim();
  return {
    json: {
      business_name: (d.title || d.name || '').trim(),
      phone: (d.phone || d.phoneUnformatted || '').trim(),
      email: d.email || '',
      category: (d.categoryName || d.category || '').trim(),
      address: (d.address || d.street || '').trim(),
      suburb: (d.city || d.neighborhood || d.suburb || '').trim(),
      postcode: pc,
      state: 'WA',
      website: (d.website || '').trim(),
      pipeline: 'diy_website',
      address_type: classifyPostcode(pc),
      source: 'google_maps',
      google_reviews: parseInt(d.reviewsCount || d.reviews || 0) || 0,
      google_rating: parseFloat(d.totalScore || d.rating || 0) || null,
      found_on_sources: ['google_maps'],
      email_source: d.email ? 'google_maps' : null,
      email_source_url: d.url || '',
      place_id: d.placeId || '',
    }
  };
});'''

TOP_10_CODE = '''// Top leads by score. Lowered to 3+ for testing (raise to 6+ for production).
// Email not required for testing - most Google Maps leads lack emails.
const allItems = $input.all();
if (allItems.length === 0) return [];

const leads = allItems
  .map(item => item.json)
  .filter(lead => lead.score >= 3)
  .sort((a, b) => b.score - a.score)
  .slice(0, 20);

return leads.map(lead => ({json: lead}));'''

for node in wf['nodes']:
    name = node['name']
    if name == 'Filter & Normalise':
        node['parameters']['jsCode'] = FILTER_NORMALISE_A
        fixes.append(name)
    elif name == 'Filter & Normalise (Has Website)':
        node['parameters']['jsCode'] = FILTER_NORMALISE_B
        fixes.append(name)
    elif name in ('Top 10 Leads (Score 6+)', 'Top 10 Leads (Score 6+)1'):
        node['parameters']['jsCode'] = TOP_10_CODE
        fixes.append(name)

print(f"Fixed {len(fixes)} nodes: {fixes}")

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
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()[:500]}")
    sys.exit(1)
