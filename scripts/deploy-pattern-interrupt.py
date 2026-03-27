"""Deploy Pattern Interrupt email variant (15%) + sharpen offer wording + fix dynamic sign-off.

Changes:
1. Build Email Prompt A: adds pattern_interrupt variant at 15% selection rate
2. Sharpens free_website offer pitch to proven close language
3. Fixes sign-off from hardcoded "Perth, WA" to dynamic state
"""
import json, urllib.request, sys, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

N8N_API_KEY = os.environ['N8N_API_KEY']
N8N_API_URL = os.environ['N8N_API_URL']
WF_ID = '3qqw96oRGpyqxt57'

# ======================================================================
# STEP 1: FETCH WORKFLOW
# ======================================================================

print('Step 1: Fetching n8n workflow...')
req = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': N8N_API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())
print(f'  Loaded workflow: {len(wf["nodes"])} nodes')

# ======================================================================
# STEP 2: UPDATE BUILD EMAIL PROMPT A
# ======================================================================

print('\nStep 2: Updating Build Email Prompt A...')

found_prompt = False
for node in wf['nodes']:
    if node['name'] == 'Build Email Prompt A':
        code = node['parameters']['jsCode']
        found_prompt = True

        # --- 2a: Add pattern_interrupt variant ---
        # Find the STANDARD_VARIANTS array and add pattern_interrupt
        if 'pattern_interrupt' not in code:
            old_variants = """  { name: 'free_offer_upfront', instruction: 'Lead with the offer immediately. No buildup. Direct pitch then ask.' },
];"""
            new_variants = """  { name: 'free_offer_upfront', instruction: 'Lead with the offer immediately. No buildup. Direct pitch then ask.' },
  { name: 'pattern_interrupt', instruction: `PATTERN INTERRUPT opener. You MUST start the email with ONE of these two openers (pick randomly):
OPENER A: "Hey {name}, chances you read this are slim, but I build websites for {trade} businesses and I reckon I can help."
OPENER B: "Hey {name}, I know you get 10 of these a day. But I'm a local Aussie who builds websites for {trade}s and I genuinely think I can help."
Replace {name} with the lead's first name (MANDATORY). Replace {trade} with their actual trade category. Do NOT mention any specific city unless the lead is in Perth metro.
After the opener, go straight into WHY you're reaching out (their reviews, their work, what you noticed) then the offer. Keep it under 5 sentences total after the opener.` },
];"""
            code = code.replace(old_variants, new_variants)
            print('  Added pattern_interrupt variant')
        else:
            print('  pattern_interrupt already exists')

        # --- 2b: Weighted variant selection (15% pattern_interrupt) ---
        old_selection = "  selectedVariant = STANDARD_VARIANTS[Math.floor(Math.random() * STANDARD_VARIANTS.length)];"
        new_selection = """  // 15% pattern_interrupt, 85% random from other variants
  const piVariant = STANDARD_VARIANTS.find(v => v.name === 'pattern_interrupt');
  const otherVariants = STANDARD_VARIANTS.filter(v => v.name !== 'pattern_interrupt');
  if (Math.random() < 0.15 && piVariant) {
    selectedVariant = piVariant;
  } else {
    selectedVariant = otherVariants[Math.floor(Math.random() * otherVariants.length)];
  }"""
        if 'piVariant' not in code:
            code = code.replace(old_selection, new_selection)
            print('  Added 15% weighted selection for pattern_interrupt')
        else:
            print('  Weighted selection already exists')

        # --- 2c: Sharpen free_website offer pitch ---
        old_pitch = "pitch: `Aaron builds the first site for free. Genuinely no catch. If they want more, they can upgrade later.`,"
        new_pitch = "pitch: `Let me build it, if you don't like it, it's yours anyway. All I need is to show you on a 15-min call. No strings attached, you keep the full website. If you want more down the track, we can chat about it then.`,"
        if 'All I need is to show you on a 15-min call' not in code:
            code = code.replace(old_pitch, new_pitch)
            print('  Sharpened free_website offer pitch')
        else:
            print('  Offer pitch already sharpened')

        # --- 2d: Fix sign-off from hardcoded Perth, WA to dynamic state ---
        old_signoff = "Aaron Parton | Perth, WA"
        new_signoff = 'Aaron Parton | ${(lead.state || "WA")}'
        if "Perth, WA" in code:
            code = code.replace(old_signoff, new_signoff)
            print('  Fixed sign-off to dynamic state')
        else:
            print('  Sign-off already dynamic')

        node['parameters']['jsCode'] = code
        break

if not found_prompt:
    print('  ERROR: Build Email Prompt A node not found!')
    sys.exit(1)

# ======================================================================
# STEP 3: PUSH WORKFLOW
# ======================================================================

print('\nStep 3: Pushing workflow...')

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

print('\n=== PATTERN INTERRUPT DEPLOYED ===')
print('Changes:')
print('  - pattern_interrupt variant added (15% of standard emails)')
print('  - free_website offer pitch sharpened to proven close language')
print('  - Sign-off uses dynamic state instead of hardcoded Perth, WA')
print('\nNext: run deploy-sms-outreach.py for SMS channel')
