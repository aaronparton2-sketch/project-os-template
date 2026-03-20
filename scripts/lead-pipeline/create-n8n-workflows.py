"""
Create n8n workflows for the lead pipeline via REST API.
Creates all workflows as INACTIVE — must be tested manually before activating.

Usage:
    python create-n8n-workflows.py
"""

import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv('N8N_API_URL')
API_KEY = os.getenv('N8N_API_KEY')

if not API_URL or not API_KEY:
    print("Error: N8N_API_URL and N8N_API_KEY must be set in .env")
    sys.exit(1)


def create_workflow(workflow_data):
    """Create a workflow via n8n REST API."""
    data = json.dumps(workflow_data).encode('utf-8')
    req = Request(
        f'{API_URL}/workflows',
        data=data,
        headers={'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urlopen(req) as resp:
            result = json.load(resp)
            print(f"  Created: {result['id']} | {result['name']}")
            return result['id']
    except HTTPError as e:
        body = e.read().decode()
        print(f"  Error {e.code}: {body[:200]}")
        return None
    except URLError as e:
        print(f"  Error: {e}")
        return None


def load_script(filename):
    """Load a JS script from the lead-pipeline folder."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, filename)
    with open(path, 'r') as f:
        return f.read()


# ============================================================
# WORKFLOW 1: Pipeline A — No Website Leads
# ============================================================
def build_pipeline_a():
    scorer_code = load_script('lead-scorer-a.js')
    personaliser_code = load_script('email-personaliser.js')

    return {
        "name": "Lead Pipeline A - No Website",
        "nodes": [
            {
                "parameters": {"rule": {"interval": [{"triggerAtHour": 6}]}},
                "id": "cron-a",
                "name": "Daily 6am AWST",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.2,
                "position": [0, 0]
            },
            {
                "parameters": {},
                "id": "manual-a",
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [0, 200]
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": "https://api.apify.com/v2/acts/apify~google-maps-scraper/runs",
                    "sendQuery": True,
                    "queryParameters": {"parameters": [{"name": "token", "value": "={{ $env.APIFY_API_TOKEN }}"}]},
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": json.dumps({
                        "searchStringsArray": [
                            "plumber Perth", "electrician Perth", "builder Perth",
                            "landscaper Perth", "cleaner Perth", "painter Perth",
                            "roofer Perth", "pest control Perth", "air conditioning Perth",
                            "fencer Perth", "concreter Perth", "carpenter Perth"
                        ],
                        "maxCrawledPlacesPerSearch": 50,
                        "language": "en",
                        "deeperCityScrape": False
                    }),
                    "options": {}
                },
                "id": "apify-gmaps-a",
                "name": "Apify: Google Maps (No Website)",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [300, 100]
            },
            {
                "parameters": {
                    "jsCode": """// Filter: businesses without a website (or Facebook-only)
// Then normalise to our lead schema
const items = $input.all();

const filtered = items.filter(item => {
  const d = item.json;
  const website = (d.website || d.url || '').toLowerCase().trim();
  // Keep if: no website, or website is just Facebook
  return !website || website.includes('facebook.com');
});

return filtered.map(item => {
  const d = item.json;
  const website = (d.website || d.url || '').toLowerCase().trim();

  // Try to extract email from the scraped data
  const email = d.email || '';

  return {
    json: {
      business_name: (d.title || d.name || '').trim(),
      phone: (d.phone || d.phoneNumber || '').trim(),
      email: email,
      category: (d.categoryName || d.category || '').trim(),
      address: (d.address || d.street || '').trim(),
      suburb: (d.city || d.suburb || '').trim(),
      postcode: (d.postalCode || d.postcode || '').trim(),
      state: 'WA',
      website: website,
      pipeline: 'no_website',
      source: 'google_maps',
      google_reviews: parseInt(d.reviewsCount || d.reviews || 0),
      google_rating: parseFloat(d.totalScore || d.rating || 0) || null,
      website_is_facebook: website.includes('facebook.com'),
      top_review_quote: '',
      found_on_sources: ['google_maps'],
      email_source: email ? 'google_maps' : null,
      email_source_url: d.placeUrl || d.url || '',
    }
  };
});"""
                },
                "id": "normalise-a",
                "name": "Filter & Normalise",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [600, 100]
            },
            {
                "parameters": {"jsCode": scorer_code},
                "id": "scorer-a",
                "name": "Lead Scorer A",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [900, 100]
            },
            {
                "parameters": {
                    "jsCode": """// Filter top leads: score 6+ with email
const leads = $input.all()
  .map(item => item.json)
  .filter(lead => lead.score >= 6 && lead.email)
  .sort((a, b) => b.score - a.score)
  .slice(0, 10);

return leads.map(lead => ({json: lead}));"""
                },
                "id": "top-leads-a",
                "name": "Top 10 Leads (Score 6+)",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1200, 100]
            },
            {
                "parameters": {"jsCode": personaliser_code},
                "id": "personaliser-a",
                "name": "AI Email Personaliser",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1500, 100]
            },
            {
                "parameters": {
                    "jsCode": """// Log pipeline stats
const items = $input.all();
const now = new Date();
return [{
  json: {
    summary: {
      pipeline: 'no_website',
      run_date: now.toISOString().split('T')[0],
      leads_processed: items.length,
      timestamp: now.toISOString()
    },
    leads: items.map(i => i.json)
  }
}];"""
                },
                "id": "log-a",
                "name": "Log Pipeline Run",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1800, 100]
            }
        ],
        "connections": {
            "Daily 6am AWST": {"main": [[{"node": "Apify: Google Maps (No Website)", "type": "main", "index": 0}]]},
            "Manual Trigger": {"main": [[{"node": "Apify: Google Maps (No Website)", "type": "main", "index": 0}]]},
            "Apify: Google Maps (No Website)": {"main": [[{"node": "Filter & Normalise", "type": "main", "index": 0}]]},
            "Filter & Normalise": {"main": [[{"node": "Lead Scorer A", "type": "main", "index": 0}]]},
            "Lead Scorer A": {"main": [[{"node": "Top 10 Leads (Score 6+)", "type": "main", "index": 0}]]},
            "Top 10 Leads (Score 6+)": {"main": [[{"node": "AI Email Personaliser", "type": "main", "index": 0}]]},
            "AI Email Personaliser": {"main": [[{"node": "Log Pipeline Run", "type": "main", "index": 0}]]}
        },
        "settings": {"executionOrder": "v1"},
        "staticData": None
    }


# ============================================================
# WORKFLOW 2: Pipeline B — DIY Website Leads
# ============================================================
def build_pipeline_b():
    scorer_code = load_script('lead-scorer-b.js')
    detector_code = load_script('platform-detector.js')
    personaliser_code = load_script('email-personaliser.js')

    return {
        "name": "Lead Pipeline B - DIY Website",
        "nodes": [
            {
                "parameters": {"rule": {"interval": [{"triggerAtHour": 6}]}},
                "id": "cron-b",
                "name": "Daily 6am AWST",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.2,
                "position": [0, 0]
            },
            {
                "parameters": {},
                "id": "manual-b",
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [0, 200]
            },
            {
                "parameters": {
                    "jsCode": """// Filter: businesses WITH a website (not Facebook)
// These go through platform detection
const items = $input.all();

return items.filter(item => {
  const d = item.json;
  const website = (d.website || d.url || '').toLowerCase().trim();
  return website && !website.includes('facebook.com');
}).map(item => {
  const d = item.json;
  return {
    json: {
      business_name: (d.title || d.name || '').trim(),
      phone: (d.phone || d.phoneNumber || '').trim(),
      email: d.email || '',
      category: (d.categoryName || d.category || '').trim(),
      address: (d.address || d.street || '').trim(),
      suburb: (d.city || d.suburb || '').trim(),
      postcode: (d.postalCode || d.postcode || '').trim(),
      state: 'WA',
      website: (d.website || d.url || '').trim(),
      pipeline: 'diy_website',
      source: 'google_maps',
      google_reviews: parseInt(d.reviewsCount || d.reviews || 0),
      google_rating: parseFloat(d.totalScore || d.rating || 0) || null,
      found_on_sources: ['google_maps'],
      email_source: d.email ? 'google_maps' : null,
      email_source_url: d.placeUrl || d.url || '',
    }
  };
});"""
                },
                "id": "normalise-b",
                "name": "Filter & Normalise (Has Website)",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [300, 100]
            },
            {
                "parameters": {"jsCode": detector_code},
                "id": "detector-b",
                "name": "Platform Detector",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [600, 100]
            },
            {
                "parameters": {
                    "jsCode": """// For each DIY site, call Google PageSpeed API
const results = [];
for (const item of $input.all()) {
  const lead = item.json;
  if (!lead.website) continue;

  try {
    const url = encodeURIComponent(lead.website.startsWith('http') ? lead.website : 'https://' + lead.website);
    const apiUrl = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=' + url + '&strategy=mobile&category=performance&category=seo';

    const response = await fetch(apiUrl, {signal: AbortSignal.timeout(15000)});
    const data = await response.json();

    const lh = data.lighthouseResult || {};
    const cats = lh.categories || {};
    const audits = lh.audits || {};

    const seoIssues = [];
    if (!audits['meta-description']?.score) seoIssues.push('missing_meta_desc');
    if (!audits['document-title']?.score) seoIssues.push('missing_title');
    if (audits['viewport']?.score === 0) seoIssues.push('no_viewport');
    if (audits['is-crawlable']?.score === 0) seoIssues.push('not_crawlable');

    results.push({
      json: {
        ...lead,
        pagespeed_score: Math.round((cats.performance?.score || 0) * 100),
        pagespeed_mobile: Math.round((cats.performance?.score || 0) * 100),
        has_ssl: lead.website.startsWith('https'),
        has_meta_description: !seoIssues.includes('missing_meta_desc'),
        has_h1: true,
        mobile_friendly: (cats.performance?.score || 0) > 0.5,
        seo_issues: seoIssues,
        core_web_vitals: {
          lcp: audits['largest-contentful-paint']?.numericValue / 1000 || null,
          fid: audits['max-potential-fid']?.numericValue / 1000 || null,
          cls: audits['cumulative-layout-shift']?.numericValue || null,
        }
      }
    });
  } catch (err) {
    // PageSpeed failed — still include lead but without audit data
    results.push({
      json: { ...lead, pagespeed_score: null, pagespeed_mobile: null }
    });
  }
}
return results;"""
                },
                "id": "pagespeed-b",
                "name": "Google PageSpeed Audit",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [900, 100]
            },
            {
                "parameters": {"jsCode": scorer_code},
                "id": "scorer-b",
                "name": "Lead Scorer B",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1200, 100]
            },
            {
                "parameters": {
                    "jsCode": """// Filter top leads: score 6+ with email
const leads = $input.all()
  .map(item => item.json)
  .filter(lead => lead.score >= 6 && lead.email)
  .sort((a, b) => b.score - a.score)
  .slice(0, 10);

return leads.map(lead => ({json: lead}));"""
                },
                "id": "top-leads-b",
                "name": "Top 10 Leads (Score 6+)",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1500, 100]
            },
            {
                "parameters": {"jsCode": personaliser_code},
                "id": "personaliser-b",
                "name": "AI Email Personaliser",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1800, 100]
            },
            {
                "parameters": {
                    "jsCode": """// Log pipeline stats
const items = $input.all();
const now = new Date();
return [{
  json: {
    summary: {
      pipeline: 'diy_website',
      run_date: now.toISOString().split('T')[0],
      leads_processed: items.length,
      timestamp: now.toISOString()
    },
    leads: items.map(i => i.json)
  }
}];"""
                },
                "id": "log-b",
                "name": "Log Pipeline Run",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [2100, 100]
            }
        ],
        "connections": {
            "Daily 6am AWST": {"main": [[{"node": "Filter & Normalise (Has Website)", "type": "main", "index": 0}]]},
            "Manual Trigger": {"main": [[{"node": "Filter & Normalise (Has Website)", "type": "main", "index": 0}]]},
            "Filter & Normalise (Has Website)": {"main": [[{"node": "Platform Detector", "type": "main", "index": 0}]]},
            "Platform Detector": {"main": [[{"node": "Google PageSpeed Audit", "type": "main", "index": 0}]]},
            "Google PageSpeed Audit": {"main": [[{"node": "Lead Scorer B", "type": "main", "index": 0}]]},
            "Lead Scorer B": {"main": [[{"node": "Top 10 Leads (Score 6+)", "type": "main", "index": 0}]]},
            "Top 10 Leads (Score 6+)": {"main": [[{"node": "AI Email Personaliser", "type": "main", "index": 0}]]},
            "AI Email Personaliser": {"main": [[{"node": "Log Pipeline Run", "type": "main", "index": 0}]]}
        },
        "settings": {"executionOrder": "v1"},
        "staticData": None
    }


# ============================================================
# WORKFLOW 3: Follow-Up Sequence
# ============================================================
def build_follow_up():
    return {
        "name": "Lead Pipeline - Follow-Up Sequence",
        "nodes": [
            {
                "parameters": {"rule": {"interval": [{"triggerAtHour": 9}]}},
                "id": "cron-fu",
                "name": "Daily 9am AWST",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.2,
                "position": [0, 0]
            },
            {
                "parameters": {},
                "id": "manual-fu",
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [0, 200]
            },
            {
                "parameters": {
                    "jsCode": """// Query leads needing follow-up
// In production, this queries Supabase for:
// WHERE follow_up_due <= today
// AND responded_at IS NULL
// AND status IN ('emailed', 'followed_up_1', 'followed_up_2')
// For now, placeholder
return [{json: {message: 'Follow-up query placeholder - connect to Supabase'}}];"""
                },
                "id": "query-fu",
                "name": "Query Leads Needing Follow-Up",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [300, 100]
            },
            {
                "parameters": {
                    "jsCode": """// Determine follow-up stage and select template
const leads = $input.all();
const results = [];

for (const item of leads) {
  const lead = item.json;
  const count = lead.follow_up_count || 0;

  if (count >= 3) {
    // Mark as no_response — no more follow-ups
    results.push({json: {...lead, action: 'mark_no_response'}});
    continue;
  }

  const stages = [
    {stage: 1, days_until_next: 4, template: 'follow_up_1_day_3'},
    {stage: 2, days_until_next: 7, template: 'follow_up_2_day_7'},
    {stage: 3, days_until_next: null, template: 'follow_up_3_day_14'},
  ];

  const current = stages[count];
  results.push({
    json: {
      ...lead,
      action: 'send_follow_up',
      follow_up_stage: current.stage,
      follow_up_template: current.template,
      days_until_next: current.days_until_next,
    }
  });
}

return results;"""
                },
                "id": "determine-stage",
                "name": "Determine Follow-Up Stage",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [600, 100]
            },
            {
                "parameters": {
                    "jsCode": """// Generate follow-up email + push to Instantly
// Placeholder — connect OpenAI + Instantly API
const items = $input.all();
return items.map(item => ({
  json: {
    ...item.json,
    status: 'follow_up_generated',
    note: 'Connect to OpenAI for personalised follow-up + Instantly API to send'
  }
}));"""
                },
                "id": "generate-fu",
                "name": "Generate & Send Follow-Up",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [900, 100]
            }
        ],
        "connections": {
            "Daily 9am AWST": {"main": [[{"node": "Query Leads Needing Follow-Up", "type": "main", "index": 0}]]},
            "Manual Trigger": {"main": [[{"node": "Query Leads Needing Follow-Up", "type": "main", "index": 0}]]},
            "Query Leads Needing Follow-Up": {"main": [[{"node": "Determine Follow-Up Stage", "type": "main", "index": 0}]]},
            "Determine Follow-Up Stage": {"main": [[{"node": "Generate & Send Follow-Up", "type": "main", "index": 0}]]}
        },
        "settings": {"executionOrder": "v1"},
        "staticData": None
    }


# ============================================================
# WORKFLOW 4: Daily Digest Email
# ============================================================
def build_digest():
    return {
        "name": "Lead Pipeline - Daily Digest",
        "nodes": [
            {
                "parameters": {"rule": {"interval": [{"triggerAtHour": 8}]}},
                "id": "cron-digest",
                "name": "Daily 8am AWST",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.2,
                "position": [0, 0]
            },
            {
                "parameters": {},
                "id": "manual-digest",
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [0, 200]
            },
            {
                "parameters": {
                    "jsCode": """// Query today's emailed leads + follow-ups due from Supabase
// Placeholder — connect to Supabase
return [{json: {
  message: 'Connect to Supabase to pull today\\'s leads + follow-ups',
  sections: ['no_website_leads', 'diy_website_leads', 'follow_ups_due', 'pipeline_stats']
}}];"""
                },
                "id": "query-digest",
                "name": "Query Today's Data",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [300, 100]
            },
            {
                "parameters": {
                    "jsCode": """// Build HTML digest email
// This will be a formatted table with lead details, scores, phone numbers, call scripts
const data = $input.first().json;

const html = '<html><body>' +
  '<h2>Lead Pipeline Digest</h2>' +
  '<p>Morning! Here\\'s what the pipeline did while you slept:</p>' +
  '<h3>No-Website Leads Emailed</h3>' +
  '<p><em>Connect to Supabase for live data</em></p>' +
  '<h3>DIY-Website Leads Emailed</h3>' +
  '<p><em>Connect to Supabase for live data</em></p>' +
  '<h3>Follow-Ups Due Today</h3>' +
  '<p><em>Connect to Supabase for live data</em></p>' +
  '<h3>Pipeline Stats</h3>' +
  '<p><em>Connect to Supabase for live data</em></p>' +
  '</body></html>';

return [{json: {
  to: 'aaron@myceliumai.com.au',
  subject: 'Lead Pipeline Digest - ' + new Date().toLocaleDateString('en-AU'),
  html: html
}}];"""
                },
                "id": "build-digest",
                "name": "Build HTML Digest",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [600, 100]
            }
        ],
        "connections": {
            "Daily 8am AWST": {"main": [[{"node": "Query Today's Data", "type": "main", "index": 0}]]},
            "Manual Trigger": {"main": [[{"node": "Query Today's Data", "type": "main", "index": 0}]]},
            "Query Today's Data": {"main": [[{"node": "Build HTML Digest", "type": "main", "index": 0}]]}
        },
        "settings": {"executionOrder": "v1"},
        "staticData": None
    }


# ============================================================
# WORKFLOW 5: Health Check
# ============================================================
def build_health_check():
    health_code = load_script('health-check.js')
    return {
        "name": "Lead Pipeline - Health Check",
        "nodes": [
            {
                "parameters": {"rule": {"interval": [{"triggerAtHour": 19}]}},
                "id": "cron-health",
                "name": "Daily 7pm AWST",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.2,
                "position": [0, 0]
            },
            {
                "parameters": {},
                "id": "manual-health",
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [0, 200]
            },
            {
                "parameters": {
                    "jsCode": """// Query email_audit_log for last 7 days
// Placeholder — connect to Supabase
return [{json: {message: 'Connect to Supabase: SELECT * FROM email_audit_log WHERE sent_at > now() - interval 7 day'}}];"""
                },
                "id": "query-health",
                "name": "Query Audit Log (7 days)",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [300, 100]
            },
            {
                "parameters": {"jsCode": health_code},
                "id": "check-health",
                "name": "Calculate Health Metrics",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [600, 100]
            },
            {
                "parameters": {
                    "jsCode": """// If unhealthy, pause Instantly campaigns + alert Aaron
const health = $input.first().json;

if (health.action === 'pause') {
  // TODO: Call Instantly API to pause campaigns
  // POST /api/v1/campaign/pause
  return [{json: {
    ...health,
    alert_to: 'aaron@myceliumai.com.au',
    alert_subject: 'PIPELINE AUTO-PAUSED: ' + health.alerts.join('; '),
    alert_sent: true
  }}];
}

return [{json: {...health, alert_sent: false}}];"""
                },
                "id": "act-health",
                "name": "Auto-Pause if Unhealthy",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [900, 100]
            }
        ],
        "connections": {
            "Daily 7pm AWST": {"main": [[{"node": "Query Audit Log (7 days)", "type": "main", "index": 0}]]},
            "Manual Trigger": {"main": [[{"node": "Query Audit Log (7 days)", "type": "main", "index": 0}]]},
            "Query Audit Log (7 days)": {"main": [[{"node": "Calculate Health Metrics", "type": "main", "index": 0}]]},
            "Calculate Health Metrics": {"main": [[{"node": "Auto-Pause if Unhealthy", "type": "main", "index": 0}]]}
        },
        "settings": {"executionOrder": "v1"},
        "staticData": None
    }


# ============================================================
# CREATE ALL WORKFLOWS
# ============================================================
if __name__ == '__main__':
    print("Creating n8n workflows for Lead Pipeline...")
    print("All workflows created as INACTIVE — test manually before activating.\n")

    workflows = [
        ("Pipeline A", build_pipeline_a),
        ("Pipeline B", build_pipeline_b),
        ("Follow-Up Sequence", build_follow_up),
        ("Daily Digest", build_digest),
        ("Health Check", build_health_check),
    ]

    created_ids = []
    for name, builder in workflows:
        print(f"[{name}]")
        wf = builder()
        wf_id = create_workflow(wf)
        if wf_id:
            created_ids.append((name, wf_id))
        print()

    print("=" * 50)
    print("Summary:")
    for name, wf_id in created_ids:
        print(f"  {name}: {wf_id}")
    print(f"\nCreated {len(created_ids)}/{len(workflows)} workflows")
    print("All INACTIVE — open n8n and test with Manual Trigger before activating cron schedules.")
