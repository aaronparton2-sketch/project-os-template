-- Migration 004: Add website verification tracking fields
-- Run after 001, 002, 003 in Supabase SQL Editor
--
-- Tracks HOW each lead was verified (or not) for website existence.
-- Enables accuracy analysis: query leads marked 'none_found' and spot-check
-- whether the checker missed any websites.

ALTER TABLE leads ADD COLUMN website_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE leads ADD COLUMN website_check_method TEXT;
  -- Values: 'url_pattern', 'google_search', 'abn_whois', 'none_found', NULL (not yet checked)
ALTER TABLE leads ADD COLUMN website_check_url TEXT;
  -- The URL found by the checker (NULL if no website found)

CREATE INDEX idx_leads_website_verified ON leads(website_verified);
CREATE INDEX idx_leads_website_check_method ON leads(website_check_method)
  WHERE website_check_method IS NOT NULL;
