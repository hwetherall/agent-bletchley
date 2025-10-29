-- Initial database schema for Agent Bletchley
-- Run this migration in your Supabase SQL editor

-- Research jobs table
CREATE TABLE IF NOT EXISTS research_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    progress DECIMAL(5, 2) DEFAULT 0.0 CHECK (progress >= 0.0 AND progress <= 100.0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    report TEXT,
    error TEXT,
    context JSONB DEFAULT '{}'::jsonb
);

-- Research iterations table
CREATE TABLE IF NOT EXISTS research_iterations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES research_jobs(id) ON DELETE CASCADE,
    step INTEGER NOT NULL,
    action TEXT NOT NULL,
    results JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_job_step UNIQUE (job_id, step)
);

-- Research sources table
CREATE TABLE IF NOT EXISTS research_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES research_jobs(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT,
    snippet TEXT,
    content TEXT,
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(job_id, url)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_research_jobs_status ON research_jobs(status);
CREATE INDEX IF NOT EXISTS idx_research_jobs_created_at ON research_jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_research_iterations_job_id ON research_iterations(job_id);
CREATE INDEX IF NOT EXISTS idx_research_sources_job_id ON research_sources(job_id);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to update updated_at on research_jobs
CREATE TRIGGER update_research_jobs_updated_at
    BEFORE UPDATE ON research_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE research_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_iterations ENABLE ROW LEVEL SECURITY;
ALTER TABLE research_sources ENABLE ROW LEVEL SECURITY;

-- TODO: Create RLS policies based on your authentication requirements
-- Example policy (adjust as needed):
-- CREATE POLICY "Users can view their own research jobs"
--     ON research_jobs FOR SELECT
--     USING (auth.uid() = user_id);
--
-- CREATE POLICY "Users can create research jobs"
--     ON research_jobs FOR INSERT
--     WITH CHECK (true);
--
-- CREATE POLICY "Users can update their own research jobs"
--     ON research_jobs FOR UPDATE
--     USING (auth.uid() = user_id);

