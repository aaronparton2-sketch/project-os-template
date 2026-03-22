"""Seed Australian regions into Supabase regions table. Uses curl to avoid Cloudflare blocking."""
import json, subprocess, os, sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / '.env')

PROJECT_REF = os.environ['SUPABASE_PIPELINE_PROJECT_REF']
ACCESS_TOKEN = os.environ['SUPABASE_ACCESS_TOKEN']
API_URL = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"

REGIONS = [
    # Tier 1 (priority 10): Perth metro sub-regions
    ("Perth CBD, Western Australia", "WA", 10),
    ("Fremantle, Western Australia", "WA", 10),
    ("Joondalup, Western Australia", "WA", 10),
    ("Rockingham, Western Australia", "WA", 10),
    ("Midland, Western Australia", "WA", 10),
    ("Armadale, Western Australia", "WA", 10),
    ("Wanneroo, Western Australia", "WA", 10),
    ("Stirling, Western Australia", "WA", 10),
    ("Cockburn, Western Australia", "WA", 10),
    ("Canning, Western Australia", "WA", 10),
    ("Morley, Western Australia", "WA", 10),
    ("Scarborough, Western Australia", "WA", 10),
    ("Osborne Park, Western Australia", "WA", 10),
    ("Balcatta, Western Australia", "WA", 10),
    ("Belmont, Western Australia", "WA", 10),
    # Tier 2 (priority 15): WA regional
    ("Mandurah, Western Australia", "WA", 15),
    ("Bunbury, Western Australia", "WA", 15),
    ("Geraldton, Western Australia", "WA", 15),
    ("Kalgoorlie, Western Australia", "WA", 15),
    ("Albany, Western Australia", "WA", 15),
    ("Broome, Western Australia", "WA", 15),
    ("Karratha, Western Australia", "WA", 15),
    ("Port Hedland, Western Australia", "WA", 15),
    ("Busselton, Western Australia", "WA", 15),
    ("Esperance, Western Australia", "WA", 15),
    ("Carnarvon, Western Australia", "WA", 15),
    ("Northam, Western Australia", "WA", 15),
    ("Kununurra, Western Australia", "WA", 15),
    ("Margaret River, Western Australia", "WA", 15),
    ("Dunsborough, Western Australia", "WA", 15),
    # Tier 3 (priority 20): Regional Australia
    ("Toowoomba, Queensland", "QLD", 20),
    ("Bendigo, Victoria", "VIC", 20),
    ("Ballarat, Victoria", "VIC", 20),
    ("Cairns, Queensland", "QLD", 20),
    ("Townsville, Queensland", "QLD", 20),
    ("Launceston, Tasmania", "TAS", 20),
    ("Orange, New South Wales", "NSW", 20),
    ("Wagga Wagga, New South Wales", "NSW", 20),
    ("Albury, New South Wales", "NSW", 20),
    ("Shepparton, Victoria", "VIC", 20),
    ("Mackay, Queensland", "QLD", 20),
    ("Rockhampton, Queensland", "QLD", 20),
    ("Gladstone, Queensland", "QLD", 20),
    ("Tamworth, New South Wales", "NSW", 20),
    ("Dubbo, New South Wales", "NSW", 20),
    ("Bathurst, New South Wales", "NSW", 20),
    ("Mildura, Victoria", "VIC", 20),
    ("Warrnambool, Victoria", "VIC", 20),
    ("Bundaberg, Queensland", "QLD", 20),
    ("Hervey Bay, Queensland", "QLD", 20),
    ("Lismore, New South Wales", "NSW", 20),
    ("Coffs Harbour, New South Wales", "NSW", 20),
    ("Port Macquarie, New South Wales", "NSW", 20),
    ("Grafton, New South Wales", "NSW", 20),
    ("Armidale, New South Wales", "NSW", 20),
    ("Broken Hill, New South Wales", "NSW", 20),
    ("Mount Gambier, South Australia", "SA", 20),
    ("Murray Bridge, South Australia", "SA", 20),
    ("Port Augusta, South Australia", "SA", 20),
    ("Port Lincoln, South Australia", "SA", 20),
    ("Whyalla, South Australia", "SA", 20),
    ("Devonport, Tasmania", "TAS", 20),
    ("Burnie, Tasmania", "TAS", 20),
    ("Alice Springs, Northern Territory", "NT", 20),
    ("Katherine, Northern Territory", "NT", 20),
    ("Traralgon, Victoria", "VIC", 20),
    ("Sale, Victoria", "VIC", 20),
    ("Horsham, Victoria", "VIC", 20),
    ("Echuca, Victoria", "VIC", 20),
    ("Swan Hill, Victoria", "VIC", 20),
    ("Wangaratta, Victoria", "VIC", 20),
    ("Benalla, Victoria", "VIC", 20),
    ("Bairnsdale, Victoria", "VIC", 20),
    ("Gympie, Queensland", "QLD", 20),
    ("Emerald, Queensland", "QLD", 20),
    ("Kingaroy, Queensland", "QLD", 20),
    ("Dalby, Queensland", "QLD", 20),
    ("Warwick, Queensland", "QLD", 20),
    ("Yeppoon, Queensland", "QLD", 20),
    ("Bowen, Queensland", "QLD", 20),
    ("Innisfail, Queensland", "QLD", 20),
    ("Atherton, Queensland", "QLD", 20),
    ("Mudgee, New South Wales", "NSW", 20),
    ("Lithgow, New South Wales", "NSW", 20),
    ("Young, New South Wales", "NSW", 20),
    ("Cowra, New South Wales", "NSW", 20),
    ("Griffith, New South Wales", "NSW", 20),
    ("Leeton, New South Wales", "NSW", 20),
    ("Goulburn, New South Wales", "NSW", 20),
    ("Nowra, New South Wales", "NSW", 20),
    ("Ulladulla, New South Wales", "NSW", 20),
    ("Batemans Bay, New South Wales", "NSW", 20),
    ("Queanbeyan, New South Wales", "NSW", 20),
    ("Cessnock, New South Wales", "NSW", 20),
    ("Muswellbrook, New South Wales", "NSW", 20),
    ("Singleton, New South Wales", "NSW", 20),
    ("Forster, New South Wales", "NSW", 20),
    ("Taree, New South Wales", "NSW", 20),
    ("Kempsey, New South Wales", "NSW", 20),
    ("Victor Harbor, South Australia", "SA", 20),
    ("Gawler, South Australia", "SA", 20),
    ("Mount Barker, South Australia", "SA", 20),
    ("Barossa Valley, South Australia", "SA", 20),
    # Tier 4 (priority 30): Outer metro / satellite cities
    ("Geelong, Victoria", "VIC", 30),
    ("Wollongong, New South Wales", "NSW", 30),
    ("Newcastle, New South Wales", "NSW", 30),
    ("Gold Coast, Queensland", "QLD", 30),
    ("Sunshine Coast, Queensland", "QLD", 30),
    ("Central Coast, New South Wales", "NSW", 30),
    ("Ipswich, Queensland", "QLD", 30),
    ("Logan, Queensland", "QLD", 30),
    ("Penrith, New South Wales", "NSW", 30),
    ("Campbelltown, New South Wales", "NSW", 30),
    ("Blacktown, New South Wales", "NSW", 30),
    ("Liverpool, New South Wales", "NSW", 30),
    ("Frankston, Victoria", "VIC", 30),
    ("Dandenong, Victoria", "VIC", 30),
    ("Werribee, Victoria", "VIC", 30),
    ("Melton, Victoria", "VIC", 30),
    ("Sunbury, Victoria", "VIC", 30),
    ("Mornington Peninsula, Victoria", "VIC", 30),
    ("Redcliffe, Queensland", "QLD", 30),
    ("Caboolture, Queensland", "QLD", 30),
    ("Caloundra, Queensland", "QLD", 30),
    ("Noosa, Queensland", "QLD", 30),
    ("Springfield, Queensland", "QLD", 30),
    ("Cranbourne, Victoria", "VIC", 30),
    ("Pakenham, Victoria", "VIC", 30),
    # Tier 5 (priority 40): Capital city metros
    ("Melbourne, Victoria", "VIC", 40),
    ("Sydney, New South Wales", "NSW", 40),
    ("Brisbane, Queensland", "QLD", 40),
    ("Adelaide, South Australia", "SA", 40),
    ("Hobart, Tasmania", "TAS", 40),
    ("Darwin, Northern Territory", "NT", 40),
    ("Canberra, Australian Capital Territory", "ACT", 40),
]

def run_query(query):
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", API_URL,
         "-H", f"Authorization: Bearer {ACCESS_TOKEN}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps({"query": query})],
        capture_output=True, text=True
    )
    return result.stdout

# Insert in batches of 15
BATCH_SIZE = 15
total = 0
for i in range(0, len(REGIONS), BATCH_SIZE):
    batch = REGIONS[i:i + BATCH_SIZE]
    values = ", ".join(
        f"('{name}', '{state}', {priority})"
        for name, state, priority in batch
    )
    query = f"INSERT INTO regions (name, state, priority) VALUES {values} ON CONFLICT (name) DO NOTHING;"
    run_query(query)
    total += len(batch)
    print(f"  Batch {i // BATCH_SIZE + 1}: {len(batch)} regions")

print(f"Seeded {total} regions total")

# Verify
result = json.loads(run_query(
    "SELECT priority, state, count(*) as n FROM regions GROUP BY priority, state ORDER BY priority, state;"
))
print("\nRegions by tier:")
for row in result:
    tier = {10: 'Perth metro', 15: 'WA regional', 20: 'Regional AU', 30: 'Outer metro', 40: 'Capital city'}.get(row['priority'], '?')
    print(f"  {tier:15s} | {row['state']:5s} | {row['n']} regions")
