// n8n Code Node: AI Email Personaliser (Anti-AI-Slop Framework)
// Input: scored leads (score 6+) with enrichment data
// Output: leads with email_subject, email_body, call_script, email_variant
//
// Uses OpenAI gpt-4o-mini for cost efficiency (~$0.01 per 10 leads)
// Paste into n8n Code node. Requires OpenAI credentials in n8n.

const PIPELINE_A_SYSTEM_PROMPT = `You are writing a cold email from Aaron, a web designer in Perth, Western Australia.
Write like a real person texting a mate about business — not like a marketer.

RULES:
- Use contractions (I'm, you're, don't, it's)
- Max 5-6 sentences. Shorter is better.
- Start with something specific about THEIR business (a review quote, their suburb, a specific detail you found)
- Never start with "I" — start with "Your", "Found", "Noticed", or the business name
- Include one honest admission: "not sure if...", "might be a stretch...", "figured I'd reach out"
- End with "Cheers, Aaron" — never "Best regards" or "Sincerely"
- CTA must be low-commitment: "interested?" or "worth a look?" — never "schedule a call"
- No jargon: no "leverage", "optimize", "streamline", "innovative", "solution", "synergy"
- No emoji
- Vary sentence length — not all the same rhythm
- One sentence can be a fragment. That's fine.
- Sound like a tradie who's good with computers, not a marketing agency
- NEVER use "I hope this email finds you well" or similar
- NEVER use "I was impressed by" — reference something specific instead
- NEVER use "Please don't hesitate to reach out"
- NEVER use exactly 3 bullet points
- NEVER use perfect grammar throughout — use natural fragments and contractions

CONTEXT: Aaron offers a free website to businesses without one. The pitch is simple — he'll build them a basic site for free, no strings. If they like it, he can do a professional version.

EMAIL FOOTER (always include):
---
If this isn't relevant, just reply "stop" and I won't contact you again.
Aaron Parton | Mycelium AI | Perth, WA

OUTPUT FORMAT (JSON):
{
  "subject": "the email subject line (short, no clickbait)",
  "body": "the email body (5-6 sentences max)",
  "call_script": "what Aaron should say when he calls this person (2-3 sentences, conversational)"
}`;

const PIPELINE_B_SYSTEM_PROMPT = `You are writing a cold email from Aaron, a web designer in Perth, Western Australia.
Write like a real person texting a mate about business — not like a marketer.

RULES:
- Use contractions (I'm, you're, don't, it's)
- Max 5-6 sentences. Shorter is better.
- Start with something specific about THEIR business (a review quote, their suburb, their PageSpeed score)
- Never start with "I" — start with "Your", "Found", "Noticed", or the business name
- Include one honest admission: "not sure if...", "might be a stretch...", "figured I'd reach out"
- End with "Cheers, Aaron" — never "Best regards" or "Sincerely"
- CTA must be low-commitment: "interested?" or "worth a look?" — never "schedule a call"
- No jargon: no "leverage", "optimize", "streamline", "innovative", "solution", "synergy"
- No emoji
- Vary sentence length — not all the same rhythm
- One sentence can be a fragment. That's fine.
- Sound like a tradie who's good with computers, not a marketing agency
- NEVER use "I hope this email finds you well" or similar
- NEVER use "I was impressed by" — reference something specific instead
- NEVER use "Please don't hesitate to reach out"
- NEVER use exactly 3 bullet points

CONTEXT: Aaron rebuilds websites for businesses that have a DIY site (Wix, Squarespace, etc.) that's slow or poorly built. He includes REAL data from their site audit — PageSpeed scores, specific issues found. The pitch is: your site is costing you customers, I can fix it.

EMAIL FOOTER (always include):
---
If this isn't relevant, just reply "stop" and I won't contact you again.
Aaron Parton | Mycelium AI | Perth, WA

OUTPUT FORMAT (JSON):
{
  "subject": "the email subject line (short, references their specific issue)",
  "body": "the email body (5-6 sentences max, includes actual PageSpeed score and specific issues)",
  "call_script": "what Aaron should say when he calls this person (2-3 sentences, references the audit data)"
}`;

// A/B test variants — different angles for the same pipeline
const VARIANTS = {
  no_website: [
    { name: 'review_quote', instruction: 'Lead with a specific Google review quote from their business.' },
    { name: 'competitor', instruction: 'Mention how many of their competitors in the area already have websites.' },
    { name: 'direct', instruction: 'Be super direct and short. 3-4 sentences max. No fluff.' },
    { name: 'free_offer', instruction: 'Lead with the free website offer immediately in the first sentence.' },
  ],
  diy_website: [
    { name: 'speed_score', instruction: 'Lead with their exact PageSpeed score and what it means for visitors.' },
    { name: 'mobile_issue', instruction: 'Focus on mobile experience — most of their customers search on phones.' },
    { name: 'competitor_compare', instruction: 'Mention that their competitors have faster/better sites.' },
    { name: 'money_loss', instruction: 'Frame it as money they are losing — "40% of visitors leave before your page loads".' },
  ],
};

function buildLeadContext(lead) {
  const parts = [];
  parts.push(`Business: ${lead.business_name}`);
  if (lead.category) parts.push(`Category: ${lead.category}`);
  if (lead.suburb) parts.push(`Location: ${lead.suburb}, WA`);
  if (lead.google_reviews) parts.push(`Google Reviews: ${lead.google_reviews} (${lead.google_rating || 'N/A'} stars)`);
  if (lead.top_review_quote) parts.push(`Best review quote: "${lead.top_review_quote}"`);
  if (lead.competitors_with_website) parts.push(`Competitors with websites: ${lead.competitors_with_website}/${lead.competitors_total || '?'}`);
  if (lead.hipages_jobs) parts.push(`HiPages jobs completed: ${lead.hipages_jobs}`);
  if (lead.website_is_facebook) parts.push('Currently using Facebook as their website');
  if (lead.uses_free_email && lead.email) parts.push(`Business email: ${lead.email} (using free email provider)`);

  // Pipeline B specific
  if (lead.diy_platform) parts.push(`Website platform: ${lead.diy_platform}`);
  if (lead.pagespeed_score !== null && lead.pagespeed_score !== undefined) parts.push(`PageSpeed desktop: ${lead.pagespeed_score}/100`);
  if (lead.pagespeed_mobile !== null && lead.pagespeed_mobile !== undefined) parts.push(`PageSpeed mobile: ${lead.pagespeed_mobile}/100`);
  if (lead.has_ssl === false) parts.push('No SSL certificate (browser shows "Not Secure")');
  if (lead.has_meta_description === false) parts.push('Missing meta description (invisible to Google)');
  if (lead.mobile_friendly === false) parts.push('Not mobile-friendly');
  if (lead.seo_issues && lead.seo_issues.length > 0) parts.push(`SEO issues: ${lead.seo_issues.join(', ')}`);
  if (lead.running_google_ads) parts.push('Currently running Google Ads (spending money on marketing)');
  if (lead.domain_expired) parts.push('Previous domain expired — had a website before');

  parts.push(`Score: ${lead.score}/10`);
  if (lead.score_breakdown) parts.push(`Score breakdown: ${JSON.stringify(lead.score_breakdown)}`);

  return parts.join('\n');
}

// n8n Code node entry point
// This node should be connected to an OpenAI node or use the HTTP Request node
// to call the OpenAI API. Below is the logic for generating the prompt per lead.

const results = [];

for (const item of $input.all()) {
  const lead = item.json;
  const pipeline = lead.pipeline || 'no_website';

  // Select system prompt based on pipeline
  const systemPrompt = pipeline === 'diy_website'
    ? PIPELINE_B_SYSTEM_PROMPT
    : PIPELINE_A_SYSTEM_PROMPT;

  // Pick a random A/B variant
  const variantPool = VARIANTS[pipeline] || VARIANTS.no_website;
  const variant = variantPool[Math.floor(Math.random() * variantPool.length)];

  // Build the user prompt with lead-specific context
  const leadContext = buildLeadContext(lead);
  const userPrompt = `Write a cold email for this lead. Use the ${variant.name} angle: ${variant.instruction}

LEAD DATA:
${leadContext}

Remember: output valid JSON with "subject", "body", and "call_script" fields.`;

  results.push({
    json: {
      ...lead,
      email_variant: variant.name,
      _ai_system_prompt: systemPrompt,
      _ai_user_prompt: userPrompt,
      _ai_model: 'gpt-4o-mini',
    },
  });
}

return results;
