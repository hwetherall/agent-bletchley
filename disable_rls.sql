-- Disable Row Level Security on all research tables
-- This allows all operations without requiring RLS policies
-- Suitable for development/testing when authentication is not yet implemented

ALTER TABLE research_jobs DISABLE ROW LEVEL SECURITY;

ALTER TABLE research_iterations DISABLE ROW LEVEL SECURITY;

ALTER TABLE research_sources DISABLE ROW LEVEL SECURITY;

