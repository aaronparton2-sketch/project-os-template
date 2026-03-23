# Trade Lingo Reference

Australian trade-specific language used in cold outreach emails. The system injects 1-2 terms per email to sound like someone who understands the trade.

**Rule:** Subtle, not forced. If a term doesn't fit naturally, skip it.

---

## Trades Covered (16 + generic fallback)

| Trade | Key Terms | Example Jobs | Email Flavour Example |
|-------|-----------|-------------|----------------------|
| **Plumber** | HWS, copper pipe, tempering valve, backflow, DWV | Hot water changeover, blocked drain, burst pipe, gas compliance | "Saw you just did that hot water changeover in [suburb]" |
| **Electrician** | Sparky, board upgrade, fault finding, test and tag, RCD | Switchboard upgrade, safety switch install, RCD testing | "Saw you did that switchboard upgrade in [suburb]" |
| **Builder** | Reno, slab down, frame up, lock-up stage, DA, formwork | Renovation, extension, granny flat, retaining wall | "That reno you finished in [suburb] looks mint" |
| **Landscaper** | Retic, bore, limestone walls, exposed agg, sleepers | Reticulation install, turf laying, paving, pool landscaping | "Saw that retic job you did in [suburb]" |
| **Painter** | Dulux, prep work, cutting in, two-coat system | Interior/exterior repaint, roof restoration | "That exterior job in [suburb] came up mint" |
| **Roofer** | Colorbond, Zincalume, flashing, fascia, sarking | Re-roof, ridge cap repointing, gutter replacement | "Saw that Colorbond re-roof in [suburb]" |
| **Concreter** | Exposed agg, liquid lime, formwork, reo mesh, power float | Driveway, shed slab, exposed aggregate | "That exposed agg driveway in [suburb] looks unreal" |
| **Air Con** | Split system, ducted, inverter, reverse cycle, zones | Split system install, ducted system, AC service | "Saw you just put a split system in over in [suburb]" |
| **Cleaner** | Bond clean, deep clean, steam and extract, pressure blast | End-of-lease clean, commercial clean, carpet steam | "Saw you smashed out that bond clean in [suburb]" |
| **Tiler** | Porcelain, subway tile, waterproofing membrane, herringbone | Bathroom reno, splashback, re-grout | "That bathroom tile job in [suburb] is clean as" |
| **Fencer** | Colorbond, pool-compliant, dividing fence, slats | Colorbond fence, pool fence compliance, gate automation | "Saw that Colorbond job in [suburb]" |
| **Pest Control** | Termite barrier, bait station, thermal imaging, treated zone | Termite inspection, general pest spray, pre-purchase | "Saw you did a termite job in [suburb]" |
| **Carpenter** | Merbau, jarrah, treated pine, tongue-and-groove | Decking, pergola, wardrobe, kitchen install | "That merbau deck in [suburb] looks unreal" |
| **Removalist** | Blanket wrap, tailgate loader, three-tonner | House move, office relocation, interstate move | "Saw you did that big move in [suburb]" |
| **Mechanic** | Logbook service, OBD scan, pads and rotors, rego check | Logbook service, brake replacement, timing belt | "Saw you did that logbook service in [suburb]" |
| **Dog Trainer** | Positive reinforcement, recall work, loose leash, socialisation | Puppy school, obedience, aggression rehab | "Saw that recall training video you posted" |

### Generic Fallback
For trades not listed: "Saw that job you did in [suburb] - your customers clearly rate you."

---

## Humour Lines (~10% of emails)

Trade-specific humour openers (one line, either in opener or CTA):

| Trade | Humour Opener |
|-------|--------------|
| Plumber | "Fair warning - I promise this email isn't about pipes. Well... sort of." |
| Electrician | "I won't shock you with the price - it's free." |
| Builder | "I build websites, not houses - but yours would look pretty good online." |
| Landscaper | "Your garden game is strong - your Google game could use some work though." |
| Roofer | "I can't fix your roof, but I can fix your Google results." |
| Concreter | "Your concrete work is rock solid - your online presence... not so much." |
| Cleaner | "I clean up online presences - not as satisfying as a bond clean, but close." |
| Generic | "I'll keep this short - I know you've got better things to do than read emails from strangers." |

**CTA humour options:**
- "Worth a 10-minute chat? I promise I'm more interesting than this email makes me sound."
- "Keen for a quick yarn? Worst case you get 10 minutes of mediocre banter and a free website idea."
- "Open to a chat? I'll bring the ideas, you bring the scepticism."

---

## How It Works in the Pipeline

1. Lead's `category` field is matched against the trade lingo dictionary
2. Matching trade terms + flavour example are injected into the OpenAI prompt
3. OpenAI is instructed to use 1-2 terms naturally (not force them)
4. Every 10th email gets a humour line (tracked via `has_humour` flag)
5. Performance tracked in `outreach_events` table with views for A/B analysis
