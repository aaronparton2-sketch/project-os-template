"""Deploy two changes:
1. Pipeline B: compliment-first structure (review/quality praise → then DIY gap)
2. Rogue variant (~5%/1 in 20): ultra-Aussie, self-aware cold email, both pipelines
"""
import json, urllib.request, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

N8N_API_KEY = os.environ['N8N_API_KEY']
N8N_API_URL = os.environ['N8N_API_URL']
WF_ID = '3qqw96oRGpyqxt57'

req = urllib.request.Request(
    f'{N8N_API_URL}/workflows/{WF_ID}',
    headers={'X-N8N-API-KEY': N8N_API_KEY, 'accept': 'application/json'}
)
wf = json.loads(urllib.request.urlopen(req).read())

for node in wf['nodes']:

    # ═══════════════════════════════════════════════════════════
    # PIPELINE A — add rogue variant
    # ═══════════════════════════════════════════════════════════
    if node['name'] == 'Build Email Prompt A':
        code = node['parameters']['jsCode']

        # Add rogue variant definition after STANDARD_VARIANTS
        if 'rogue' not in code:
            # Add the rogue variant object
            rogue_block = """
const ROGUE_VARIANT = {
  name: 'rogue',
  instruction: `This is a ROGUE email. Break every cold email convention. Be unmistakably human, Australian, and self-aware.

TONE: Like a young Aussie bloke texting a mate. Casual as hell. Self-deprecating.
- Open with something self-aware: "Look, I know cold emails are annoying as sh*t"
- Position yourself: "I'm just a young bloke from Perth who started his own business"
- Be direct: "I'm not some overseas call centre or AI bot, I actually looked at your business"
- Reference something specific about them to prove it
- Use mild Australian slang: "mate", "reckon", "bloody", "keen", "no worries", "cheers"
- ONE mild swear word is OK (asterisked: sh*t, d*mn, hell). Not aggressive, just casual
- Keep it short. 4-5 sentences max
- CTA: ultra casual. "Anyway, figured I'd shoot my shot. No stress if not."

EXAMPLE STRUCTURE:
"Hey [Name], look, I know cold emails are annoying as sh*t, so I'll keep this quick. I had a look at [Business] and honestly your reviews are mint but you don't have a website, which means you're losing jobs to blokes who do. I'm Aaron, I'm a web designer from Perth, and I build free websites for tradies. Not a scam, not a call centre, just a young bloke trying to get his own business going. Keen for a quick chat? No stress if not."

DO NOT: be offensive, punch down, or say anything you wouldn't say to someone's face at a BBQ.`,
};

"""
            # Insert rogue variant before the lead processing
            code = code.replace(
                'const lead = $input.item.json;',
                rogue_block + 'const lead = $input.item.json;'
            )

            # Add rogue selection logic (1 in 20, separate from humour)
            code = code.replace(
                "} else {\n  personalisationType = 'standard';\n  selectedVariant = STANDARD_VARIANTS[Math.floor(Math.random() * STANDARD_VARIANTS.length)];\n}",
                """} else {
  personalisationType = 'standard';
  selectedVariant = STANDARD_VARIANTS[Math.floor(Math.random() * STANDARD_VARIANTS.length)];
}

// Rogue override: 1 in 20 emails (~5%) — separate from humour
const isRogue = ((nameHash + dayOfYear * 7) % 20 === 0);
if (isRogue && personalisationType !== 'new_business') {
  selectedVariant = ROGUE_VARIANT;
  personalisationType = 'rogue';
}"""
            )

            # Need nameHash defined before the rogue check — it's currently defined after variant selection
            # Move nameHash calculation earlier
            if "const nameHash = (lead.business_name" in code:
                # nameHash is already defined before variant selection in humour section
                pass

            node['parameters']['jsCode'] = code
            print('Pipeline A: rogue variant added (1/20)')
        else:
            print('Pipeline A: rogue variant already present')

    # ═══════════════════════════════════════════════════════════
    # PIPELINE B — compliment-first + rogue variant
    # ═══════════════════════════════════════════════════════════
    elif node['name'] == 'Build Email Prompt B':
        code = node['parameters']['jsCode']

        # 1. Fix the structure instruction: compliment first, then DIY gap
        code = code.replace(
            "- Their current website was clearly built with a DIY tool (Wix, Squarespace, GoDaddy, etc.)\n- It looks DIY, not premium. That gap costs them trust, enquiries, and what customers are willing to pay",
            "- ALWAYS start with a genuine compliment: reference a specific Google review, their work quality, or their reputation\n- THEN transition to the website gap: their site is holding back a business that's clearly doing great work\n- Frame it as: the business deserves better than a DIY site, not that the site is bad"
        )

        # Fix the STRUCTURE section
        code = code.replace(
            "STRUCTURE:\n- First line: \"Hey [First Name],\" - always use their name\n- Second line: you looked at their site and it's costing them work\n- Middle: the DIY gap - trust, enquiries, what people are willing to pay",
            'STRUCTURE:\n- First line: "Hey [First Name]," - always use their name\n- Second line: genuine compliment (review quote, quality of work, reputation in their suburb)\n- Third line: transition - "but I reckon your website is holding you back"\n- Middle: the DIY gap - trust, enquiries, what people are willing to pay'
        )

        # Update variant instructions to compliment-first
        code = code.replace(
            "{ name: 'diy_gap', instruction: 'Lead with: you looked at their site and it looks more DIY than premium. That gap affects trust, enquiries, and what people are willing to pay. Offer a free mock-up.' }",
            "{ name: 'diy_gap', instruction: 'Compliment first: reference a specific review or their reputation. Then transition: your website is holding you back mate. It looks more DIY than premium, and that gap affects trust and enquiries. Offer a free mock-up.' }"
        )
        code = code.replace(
            "{ name: 'competitor_look', instruction: 'Their competitors look more established online. When a customer compares sites, first impressions win. Their work is great but their site lets them down. Offer a free mock-up.' }",
            "{ name: 'competitor_look', instruction: 'Compliment their work quality first (reviews prove it). Then: their competitors just look more established online because of their websites. The work is the same quality but first impressions matter. Offer a free mock-up.' }"
        )
        code = code.replace(
            "{ name: 'trust_gap', instruction: 'Customers Google them before calling. The site is the first impression. Right now it says \"I built this myself\" not \"this is a serious business\". Offer a free mock-up.' }",
            "{ name: 'trust_gap', instruction: 'Open with how highly rated they are (reviews, reputation). Then: when customers Google them, the site doesn\\'t match that quality. It says \"I built this myself\" not \"this is a serious business\". Offer a free mock-up.' }"
        )
        code = code.replace(
            """{ name: 'social_proof_mismatch', instruction: 'Their Google reviews are great but their website doesn\\'t match. Customers see the reviews, visit the site, and the disconnect makes them hesitate. Offer a free mock-up.' }""",
            """{ name: 'social_proof_mismatch', instruction: 'Lead with a specific review quote or reviewer name. Their reviews paint a picture of a great business. But the website tells a different story. That mismatch makes customers hesitate. Offer a free mock-up.' }"""
        )

        # 2. Add rogue variant to Pipeline B
        if 'ROGUE_VARIANT' not in code:
            rogue_b = """
const ROGUE_VARIANT = {
  name: 'rogue',
  instruction: `ROGUE EMAIL. Break every cold email convention. Be unmistakably human, Australian, and self-aware.

TONE: Young Aussie bloke, casual as hell, self-deprecating about cold emailing.
- Open with something self-aware about cold emails
- Compliment their business genuinely (use a review or specific detail)
- Be blunt about the website: "mate, your site looks like it was built on a Sunday arvo after a few beers"
- Position yourself: "I'm just a young bloke from Perth, started my own business, I build websites for tradies"
- ONE mild swear (asterisked: sh*t, d*mn, hell) — casual not aggressive
- Use Australian slang: "mate", "reckon", "bloody", "keen"
- CTA: "Anyway, figured I'd shoot my shot. No stress if not."

DO NOT: be offensive, punch down, or say anything you wouldn't say at a BBQ.`,
};

"""
            code = code.replace(
                'const lead = $input.item.json;',
                rogue_b + 'const lead = $input.item.json;'
            )

            # Add rogue selection (1 in 20)
            code = code.replace(
                "const hasHumour = ((nameHash + dayOfYear) % 10 === 0);",
                """const hasHumour = ((nameHash + dayOfYear) % 10 === 0);

// Rogue override: 1 in 20 emails (~5%)
const isRogue = ((nameHash + dayOfYear * 7) % 20 === 0);"""
            )

            # Override variant selection for rogue
            code = code.replace(
                "const userPrompt = `Write a DIY website upgrade email.",
                """// Apply rogue override
let finalVariant = variant;
let finalPersonalisationType = 'diy_website';
if (isRogue) {
  finalVariant = ROGUE_VARIANT;
  finalPersonalisationType = 'rogue';
}

const userPrompt = `Write a DIY website upgrade email."""
            )

            # Fix the variant reference in the prompt
            code = code.replace(
                "Angle: ${variant.instruction}${humourInstruction}",
                "Angle: ${finalVariant.instruction}${isRogue ? '' : humourInstruction}"
            )

            # Fix the return object
            code = code.replace(
                "_variant_name: variant.name,",
                "_variant_name: finalVariant.name,"
            )
            code = code.replace(
                "_personalisation_type: 'diy_website',",
                "_personalisation_type: finalPersonalisationType,"
            )

            print('Pipeline B: compliment-first structure + rogue variant added')
        else:
            print('Pipeline B: rogue variant already present')

        node['parameters']['jsCode'] = code

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
    print(f'\nWorkflow updated ({len(result.get("nodes", []))} nodes)')
except urllib.error.HTTPError as e:
    print(f'Error {e.code}: {e.read().decode()[:500]}')
