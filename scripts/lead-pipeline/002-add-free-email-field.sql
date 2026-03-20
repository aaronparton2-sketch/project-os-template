-- Migration: Add uses_free_email column to leads table
-- Run in Supabase Dashboard → SQL Editor → New Query → Paste → Run

ALTER TABLE leads ADD COLUMN IF NOT EXISTS uses_free_email BOOLEAN DEFAULT FALSE;

-- Also add found_on_sources for multi-source tracking
ALTER TABLE leads ADD COLUMN IF NOT EXISTS found_on_sources TEXT[] DEFAULT '{}';
