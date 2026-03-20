// n8n Code Node: Website Platform Detector
// Input: leads with website URLs
// Output: leads with diy_platform field set (or null if professionally built)
//
// This runs as an n8n Code node. For each lead with a website,
// it makes an HTTP request and fingerprints the platform.
// Only leads with detected DIY platforms continue to Pipeline B.

// Platform signatures — checked against HTML source + headers
const PLATFORM_SIGNATURES = {
  wix: {
    html: [/wix\.com/i, /_wix_browser_sess/i, /wixsite\.com/i, /wix-warmup-data/i],
    headers: [/X-Wix-/i],
    generator: [/Wix\.com/i],
  },
  squarespace: {
    html: [/squarespace\.com/i, /sqsp/i, /static\.squarespace/i, /squarespace-cdn/i],
    headers: [/X-ServedBy.*squarespace/i],
    generator: [/Squarespace/i],
  },
  weebly: {
    html: [/weebly\.com/i, /editmysite\.com/i],
    headers: [],
    generator: [/Weebly/i],
  },
  wordpress_com: {
    // wordpress.COM (hosted/free) — not self-hosted wordpress.ORG
    html: [/s[0-9]\.wp\.com/i, /wordpress\.com/i, /wp-content\/themes\/starter/i],
    headers: [],
    generator: [/WordPress\.com/i],
  },
  godaddy: {
    html: [/godaddy\.com/i, /img1\.wsimg\.com/i, /secureserver\.net/i],
    headers: [],
    generator: [/GoDaddy/i],
  },
  jimdo: {
    html: [/jimdo\.com/i, /jimdosite\.com/i],
    headers: [],
    generator: [/Jimdo/i],
  },
  shopify: {
    // Shopify sites used as business websites (not just e-commerce)
    html: [/cdn\.shopify\.com/i, /myshopify\.com/i],
    headers: [/X-ShopId/i],
    generator: [],
  },
};

async function detectPlatform(url) {
  // Ensure URL has protocol
  if (!url.startsWith('http')) {
    url = 'https://' + url;
  }

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);

    const response = await fetch(url, {
      redirect: 'follow',
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      },
    });

    clearTimeout(timeout);

    const html = await response.text();
    const headersStr = JSON.stringify(Object.fromEntries(response.headers));

    // Extract meta generator tag
    const generatorMatch = html.match(
      /<meta[^>]*name=["']generator["'][^>]*content=["']([^"']+)["']/i
    );
    const generator = generatorMatch ? generatorMatch[1] : '';

    // Check each platform's signatures
    for (const [platform, sigs] of Object.entries(PLATFORM_SIGNATURES)) {
      const htmlMatch = sigs.html.some(regex => regex.test(html));
      const headerMatch = sigs.headers.some(regex => regex.test(headersStr));
      const genMatch = sigs.generator.some(regex => regex.test(generator));

      if (htmlMatch || headerMatch || genMatch) {
        return platform;
      }
    }

    return null; // Not a DIY platform — likely professionally built
  } catch (err) {
    // Site unreachable, SSL error, timeout — skip
    return null;
  }
}

// n8n Code node entry point
const results = [];

for (const item of $input.all()) {
  const lead = item.json;

  if (!lead.website) {
    // No website — skip (this shouldn't be in Pipeline B)
    continue;
  }

  const platform = await detectPlatform(lead.website);

  if (platform) {
    // DIY platform detected — include in Pipeline B
    results.push({
      json: {
        ...lead,
        diy_platform: platform,
      },
    });
  }
  // If platform is null, the site is professionally built — exclude from Pipeline B
}

return results;
