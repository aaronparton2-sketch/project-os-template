-- Migration: Add address_type column for residential address scoring
-- Run this in Supabase Dashboard → SQL Editor → New Query → Paste → Run
-- URL: https://supabase.com/dashboard/project/[your-project-ref]/sql/new
--
-- Values: 'residential', 'commercial', 'cbd', 'unknown'
-- Residential = suburban Perth (default for most postcodes)
-- Commercial = known industrial/commercial zones (Welshpool, Malaga, Osborne Park, etc.)
-- CBD = Perth city centre (6000-6005)
-- Unknown = no postcode available
--
-- Insight credit: Aaron's girlfriend — businesses at residential addresses
-- are more likely to be owner-operated and need marketing help.

ALTER TABLE leads ADD COLUMN address_type TEXT DEFAULT 'unknown';

CREATE INDEX idx_leads_address_type ON leads(address_type);

-- Backfill existing leads based on postcode (if any exist)
UPDATE leads SET address_type = CASE
  WHEN postcode IN ('6000', '6001', '6003', '6004', '6005') THEN 'cbd'
  WHEN postcode IN (
    '6017', '6021', '6053', '6054', '6055', '6065', '6090',
    '6100', '6104', '6105', '6106', '6107', '6109', '6112',
    '6154', '6155', '6163', '6164', '6165', '6166', '6168'
  ) THEN 'commercial'
  WHEN postcode IS NOT NULL THEN 'residential'
  ELSE 'unknown'
END
WHERE address_type = 'unknown' OR address_type IS NULL;
