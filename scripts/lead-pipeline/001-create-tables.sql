-- Lead Pipeline: Supabase Table Setup
-- Run this in Supabase Dashboard → SQL Editor → New Query → Paste → Run
-- URL: https://supabase.com/dashboard/project/[your-project-ref]/sql/new

-- ============================================
-- TABLE 1: leads (main lead database)
-- ============================================

CREATE TABLE leads (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,

  -- Business info
  business_name TEXT NOT NULL,
  phone TEXT,
  email TEXT,
  category TEXT,
  address TEXT,
  suburb TEXT,
  postcode TEXT,
  state TEXT DEFAULT 'WA',
  website TEXT,

  -- Pipeline classification
  pipeline TEXT NOT NULL DEFAULT 'no_website',  -- 'no_website' or 'diy_website'
  source TEXT NOT NULL,  -- 'google_maps', 'abr', 'hipages', 'truelocal', 'yellowpages', 'facebook', 'expired_domain', 'google_ads_transparency', 'manual'

  -- Scoring signals (shared)
  google_reviews INTEGER DEFAULT 0,
  google_rating NUMERIC(2,1),
  hipages_jobs INTEGER DEFAULT 0,
  abn TEXT,
  registration_date DATE,
  has_meta_ads BOOLEAN DEFAULT FALSE,
  website_is_facebook BOOLEAN DEFAULT FALSE,

  -- DIY website signals (Pipeline B only)
  diy_platform TEXT,  -- 'wix', 'squarespace', 'weebly', 'wordpress_com', 'godaddy', 'jimdo'
  pagespeed_score INTEGER,  -- 0-100 desktop
  pagespeed_mobile INTEGER,  -- 0-100 mobile
  core_web_vitals JSONB,  -- {"lcp": 4.2, "fid": 0.3, "cls": 0.15}
  has_ssl BOOLEAN,
  has_meta_description BOOLEAN,
  has_h1 BOOLEAN,
  mobile_friendly BOOLEAN,
  seo_issues JSONB,  -- ["missing_meta_desc", "no_h1", "no_alt_text"]
  domain_expired BOOLEAN DEFAULT FALSE,
  running_google_ads BOOLEAN DEFAULT FALSE,

  -- Scoring
  score INTEGER DEFAULT 0,
  score_breakdown JSONB,

  -- Email discovery + verification
  email_source TEXT,  -- where the email was found (legal defence)
  email_source_url TEXT,  -- URL where email was published
  email_found_at TIMESTAMPTZ,
  email_verified BOOLEAN DEFAULT FALSE,
  email_verification_status TEXT,  -- 'valid', 'invalid', 'accept_all', 'unknown'

  -- Auto-email tracking
  email_sent BOOLEAN DEFAULT FALSE,
  email_variant TEXT,  -- A/B test variant name
  email_subject TEXT,
  email_body TEXT,
  call_script TEXT,
  emailed_at TIMESTAMPTZ,
  sending_domain TEXT,  -- which outreach domain sent the email
  instantly_lead_id TEXT,

  -- Pipeline tracking
  status TEXT DEFAULT 'new',
  -- Statuses: 'new', 'emailed', 'followed_up_1', 'followed_up_2', 'followed_up_3',
  --           'responded', 'call_booked', 'converted', 'no_response', 'not_interested', 'dead'
  notes TEXT,

  -- Follow-up tracking
  follow_up_count INTEGER DEFAULT 0,
  follow_up_due DATE,
  last_follow_up_at TIMESTAMPTZ,
  last_contact_date DATE,
  next_contact_date DATE,

  -- Competitor context (enrichment)
  competitors_with_website INTEGER,
  competitors_total INTEGER,
  top_review_quote TEXT,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  contacted_at TIMESTAMPTZ,
  responded_at TIMESTAMPTZ,
  converted_at TIMESTAMPTZ,

  -- Deduplication
  UNIQUE(phone),
  UNIQUE(abn)
);

-- Indexes for fast queries
CREATE INDEX idx_leads_created_status ON leads(created_at, status);
CREATE INDEX idx_leads_score ON leads(score DESC);
CREATE INDEX idx_leads_source ON leads(source);
CREATE INDEX idx_leads_pipeline ON leads(pipeline);
CREATE INDEX idx_leads_follow_up ON leads(follow_up_due) WHERE follow_up_due IS NOT NULL AND status IN ('emailed', 'followed_up_1', 'followed_up_2');
CREATE INDEX idx_leads_email_variant ON leads(email_variant) WHERE email_variant IS NOT NULL;
CREATE INDEX idx_leads_diy_platform ON leads(diy_platform) WHERE diy_platform IS NOT NULL;
CREATE INDEX idx_leads_next_contact ON leads(next_contact_date) WHERE next_contact_date IS NOT NULL;

-- Dedup fallback: when phone AND abn are both NULL, dedupe by name+suburb
CREATE UNIQUE INDEX idx_leads_name_suburb ON leads(lower(business_name), lower(suburb)) WHERE phone IS NULL AND abn IS NULL;


-- ============================================
-- TABLE 2: lead_pipeline_runs (daily run logs)
-- ============================================

CREATE TABLE lead_pipeline_runs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  run_date DATE NOT NULL,
  pipeline TEXT NOT NULL,  -- 'no_website', 'diy_website', 'follow_up'
  source TEXT NOT NULL,  -- which data source this run covers
  leads_found INTEGER DEFAULT 0,
  leads_new INTEGER DEFAULT 0,
  leads_duplicate INTEGER DEFAULT 0,
  emails_sent INTEGER DEFAULT 0,
  follow_ups_sent INTEGER DEFAULT 0,
  errors TEXT,
  run_duration_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================
-- TABLE 3: suppressed_emails (cross-domain blocklist)
-- ============================================

CREATE TABLE suppressed_emails (
  email TEXT PRIMARY KEY,
  reason TEXT NOT NULL,  -- 'unsubscribed', 'hard_bounce', 'spam_complaint', 'manual'
  source_domain TEXT,  -- which outreach domain triggered the suppression
  suppressed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_suppressed_email ON suppressed_emails(email);


-- ============================================
-- TABLE 4: email_audit_log (compliance trail)
-- ============================================

CREATE TABLE email_audit_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  lead_id UUID REFERENCES leads(id),
  email_to TEXT NOT NULL,
  email_from TEXT NOT NULL,
  email_subject TEXT,
  email_type TEXT NOT NULL,  -- 'cold_outreach', 'follow_up_1', 'follow_up_2', 'follow_up_3'
  pipeline TEXT,  -- 'no_website', 'diy_website'
  email_source TEXT,  -- where recipient's email was found
  email_source_url TEXT,  -- URL where email was published (legal defence)
  sending_domain TEXT,  -- which outreach domain sent it
  instantly_campaign_id TEXT,
  status TEXT DEFAULT 'sent',  -- 'sent', 'delivered', 'opened', 'replied', 'bounced', 'unsubscribed'
  bounce_type TEXT,  -- 'hard', 'soft', NULL
  sent_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_lead ON email_audit_log(lead_id);
CREATE INDEX idx_audit_email ON email_audit_log(email_to);
CREATE INDEX idx_audit_status ON email_audit_log(status);
CREATE INDEX idx_audit_sent ON email_audit_log(sent_at);
