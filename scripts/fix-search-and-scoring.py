"""Expand Apify search to all business types + broaden scoring categories.
- Apify: 12 trade searches → 50+ business category searches
- Scorer: rename HIGH_VALUE_TRADES → SERVICE_BUSINESSES, expand list, keep +1 boost
"""
import json, urllib.request, sys, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

N8N_API_KEY = os.environ['N8N_API_KEY']
N8N_API_URL = os.environ['N8N_API_URL']
APIFY_TOKEN = os.environ['APIFY_API_TOKEN']
WF_ID = '3qqw96oRGpyqxt57'

req = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': N8N_API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())

# ── Expanded search categories ──
# Service businesses (priority) + all other business types
SEARCH_TERMS = [
    # === TRADES (high priority) ===
    "plumber", "electrician", "builder", "landscaper",
    "painter", "roofer", "pest control", "air conditioning",
    "fencer", "concreter", "carpenter", "tiler",
    "handyman", "glazier", "garage door", "solar installer",
    "demolition", "excavation", "pool builder", "bore drilling",
    # === OTHER SERVICES ===
    "mechanic", "panel beater", "auto electrician", "car detailing",
    "locksmith", "removalist", "storage", "skip bin",
    "tree removal", "lawn mowing", "garden maintenance",
    "pressure washing", "gutter cleaning", "window cleaning",
    # === HEALTH & BEAUTY ===
    "hairdresser", "barber", "beauty salon", "nail salon",
    "massage therapist", "physiotherapist", "chiropractor",
    "dentist", "personal trainer", "gym", "yoga studio",
    "dog grooming", "veterinarian",
    # === FOOD & HOSPITALITY ===
    "cafe", "restaurant", "bakery", "catering",
    "food truck", "butcher",
    # === PROFESSIONAL SERVICES ===
    "accountant", "bookkeeper", "mortgage broker",
    "real estate agent", "photographer", "videographer",
    "graphic designer", "music teacher", "tutor",
    # === RETAIL ===
    "florist", "pet store", "pharmacy",
]

# ── Update Apify node ──
apify_body = {
    "searchStringsArray": [f"{term} Perth WA" for term in SEARCH_TERMS],
    "locationQuery": "Perth, Western Australia",
    "maxCrawledPlacesPerSearch": 50,
    "language": "en",
    "deeperCityScrape": False,
    "onlyDataFromSearchPage": False,
    "skipClosedPlaces": True,
}

# ── Updated scorer with expanded service list ──
# SERVICE_BUSINESSES replaces HIGH_VALUE_TRADES — broader, same +1 boost
SERVICE_BUSINESSES_JS = """const SERVICE_BUSINESSES = [
  // Trades (core)
  'plumber', 'electrician', 'builder', 'roofer', 'concreter',
  'landscaper', 'pool', 'painter', 'fencer', 'carpenter',
  'pest control', 'cleaner', 'air conditioning', 'solar',
  'bore', 'drilling', 'excavation', 'demolition',
  'tiler', 'tiling', 'glazier', 'glass', 'garage door',
  'handyman', 'cabinet', 'kitchen', 'bathroom',
  // Auto
  'mechanic', 'panel beater', 'auto electri', 'car detail', 'smash repair',
  // Home services
  'locksmith', 'removalist', 'tree', 'lawn', 'garden', 'mowing',
  'pressure wash', 'gutter', 'window clean', 'skip bin',
  // Health & beauty
  'hairdresser', 'barber', 'beauty', 'nail salon', 'massage',
  'physiotherap', 'chiropract', 'dentist', 'personal train',
  'dog groom', 'veterinar', 'groomer',
  // Professional
  'accountant', 'bookkeeper', 'mortgage', 'real estate',
  'photograph', 'videograph',
];"""

fixes = []

for node in wf['nodes']:
    name = node['name']

    # Update Apify search
    if name == 'Apify: Google Maps (No Website)':
        node['parameters']['jsonBody'] = json.dumps(apify_body)
        fixes.append(f'{name} ({len(SEARCH_TERMS)} categories)')

    # Update Lead Scorer A
    elif name == 'Lead Scorer A':
        code = node['parameters']['jsCode']
        # Replace the old HIGH_VALUE_TRADES array
        old_block_start = "const HIGH_VALUE_TRADES = ["
        old_block_end = "];"
        if old_block_start in code:
            start_idx = code.index(old_block_start)
            # Find the matching ];
            end_idx = code.index(old_block_end, start_idx) + len(old_block_end)
            code = code[:start_idx] + SERVICE_BUSINESSES_JS + code[end_idx:]
            # Replace all references
            code = code.replace('HIGH_VALUE_TRADES', 'SERVICE_BUSINESSES')
            code = code.replace('high_value_category', 'service_business')
            code = code.replace("'+1 (high-value trade)'", "'+1 (service-based business)'")
            node['parameters']['jsCode'] = code
            fixes.append('Lead Scorer A')

    # Update Lead Scorer B
    elif name == 'Lead Scorer B':
        code = node['parameters']['jsCode']
        old_block_start = "const HIGH_VALUE_TRADES = ["
        if old_block_start in code:
            start_idx = code.index(old_block_start)
            end_idx = code.index("];", start_idx) + 2
            code = code[:start_idx] + SERVICE_BUSINESSES_JS + code[end_idx:]
            code = code.replace('HIGH_VALUE_TRADES', 'SERVICE_BUSINESSES')
            code = code.replace('high_value_category', 'service_business')
            code = code.replace("'+1 (high-value trade)'", "'+1 (service-based business)'")
            node['parameters']['jsCode'] = code
            fixes.append('Lead Scorer B')

print(f'Fixed {len(fixes)} nodes: {fixes}')

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
