-- Create market_news table for autonomous market news
CREATE TABLE IF NOT EXISTS market_news (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('Economic', 'Supply', 'Mini')),
  analysis TEXT,
  analysis_am TEXT, -- Amharic translation for local users
  source_url TEXT,
  price_trend JSONB, -- Store price trend data {direction: 'up/down/stable', percentage: number, commodity: string}
  priority INTEGER DEFAULT 1 CHECK (priority >= 1 AND priority <= 5),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_market_news_category ON market_news(category);
CREATE INDEX idx_market_news_created_at ON market_news(created_at DESC);
CREATE INDEX idx_market_news_priority ON market_news(priority DESC);
CREATE INDEX idx_market_news_active ON market_news(is_active);

-- Add RLS policies for security
ALTER TABLE market_news ENABLE ROW LEVEL SECURITY;

-- Allow read access to all authenticated users
CREATE POLICY "Allow read access to authenticated users" ON market_news
  FOR SELECT USING (auth.role() = 'authenticated');

-- Allow insert access to service role only
CREATE POLICY "Allow insert access to service role" ON market_news
  FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- Allow update/delete access to service role only
CREATE POLICY "Allow update/delete access to service role" ON market_news
  FOR ALL USING (auth.role() = 'service_role');

-- Create function to automatically update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_market_news_updated_at
  BEFORE UPDATE ON market_news
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
