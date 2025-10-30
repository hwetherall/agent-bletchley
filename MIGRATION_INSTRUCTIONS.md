# Running Supabase Migration via Dashboard

## Step-by-Step Instructions

### Step 1: Access Supabase Dashboard
1. Go to: https://supabase.com/dashboard
2. Log in to your account (if not already logged in)

### Step 2: Select Your Project
1. In the project list, find and click on: **pdkyyrvikbnizgtmzzhz**
   - Or look for your project name if it's different

### Step 3: Open SQL Editor
1. In the **left sidebar**, find and click: **"SQL Editor"** (it has a database icon)
2. You'll see a query editor interface

### Step 4: Create New Query
1. Click the **"New Query"** button at the top (or click the "+" icon if available)
2. This opens a blank SQL editor pane

### Step 5: Copy and Paste the Migration SQL
Copy the entire SQL below and paste it into the editor:

```sql
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
```

### Step 6: Run the Migration
1. Review the SQL to make sure it's all there
2. Click the **"Run"** button (usually green, in the bottom right)
   - OR press **Ctrl+Enter** (Windows) or **Cmd+Enter** (Mac)
3. Wait for execution to complete (usually takes a few seconds)

### Step 7: Verify Success
You should see:
- ✅ **Success message** at the bottom (like "Success. No rows returned")
- ✅ No error messages in red
- ✅ A message indicating how many statements were executed

### Step 8: Verify Tables Were Created
1. In the left sidebar, click **"Table Editor"**
2. You should now see three new tables:
   - `research_jobs`
   - `research_iterations`
   - `research_sources`

## What This Migration Does

This migration creates:
- ✅ **research_jobs** table - Stores research job information (query, status, progress, report)
- ✅ **research_iterations** table - Tracks each step/iteration of the research process
- ✅ **research_sources** table - Stores URLs and content of research sources
- ✅ **Indexes** - For faster queries
- ✅ **Auto-update trigger** - Automatically updates `updated_at` timestamps
- ✅ **Row Level Security (RLS)** - Enabled on all tables (you'll need to add policies later)

## Troubleshooting

**If you see errors:**
- Make sure you copied the entire SQL (all 81 lines)
- Check that there are no syntax errors
- Ensure you're connected to the correct project
- Some statements might show warnings if tables already exist (that's okay - the `IF NOT EXISTS` clause handles it)

**If tables don't appear:**
- Refresh the Table Editor page
- Check the SQL Editor output for any error messages
- Make sure the migration completed successfully

## Next Steps

After running this migration, you may want to:
1. Create RLS policies (see the commented examples in the SQL)
2. Test inserting a sample research job
3. Verify the trigger works by updating a job

