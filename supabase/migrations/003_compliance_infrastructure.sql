-- Compliance Infrastructure Migration for Worldmine
-- This migration creates all tables required for 2026 global financial standards compliance

-- KYC Profiles Table
CREATE TABLE IF NOT EXISTS kyc_profiles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  tier INTEGER NOT NULL CHECK (tier IN (1, 2, 3)),
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  id_verification JSONB,
  liveness_check JSONB,
  proof_of_address JSONB,
  last_sanctions_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  sanctions_status TEXT DEFAULT 'clear' CHECK (sanctions_status IN ('clear', 'flagged', 'blocked')),
  risk_score INTEGER DEFAULT 0 CHECK (risk_score >= 0 AND risk_score <= 100),
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'suspended')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sanctions Screening Results Table
CREATE TABLE IF NOT EXISTS sanctions_screening_results (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  screened_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  matches JSONB NOT NULL DEFAULT '[]'::jsonb,
  status TEXT NOT NULL CHECK (status IN ('clear', 'flagged', 'blocked')),
  requires_manual_review BOOLEAN DEFAULT FALSE,
  screening_version TEXT DEFAULT 'v1.0',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transaction Monitoring Table
CREATE TABLE IF NOT EXISTS transaction_monitoring (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  transaction_id UUID REFERENCES transactions(id) ON DELETE CASCADE NOT NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  amount DECIMAL(20,8) NOT NULL,
  currency TEXT NOT NULL DEFAULT 'USD',
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  risk_factors JSONB NOT NULL,
  risk_score INTEGER DEFAULT 0 CHECK (risk_score >= 0 AND risk_score <= 100),
  status TEXT NOT NULL CHECK (status IN ('approved', 'flagged', 'blocked')),
  requires_manual_review BOOLEAN DEFAULT FALSE,
  reason TEXT,
  reviewed_by UUID REFERENCES auth.users(id),
  reviewed_at TIMESTAMP WITH TIME ZONE,
  review_notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- E-Signature Compliance Logs Table
CREATE TABLE IF NOT EXISTS esignature_compliance_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE NOT NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ip_address INET NOT NULL,
  user_agent TEXT NOT NULL,
  biometric_hash TEXT NOT NULL,
  contract_sha256 TEXT NOT NULL,
  terms_version TEXT NOT NULL,
  consent_given BOOLEAN DEFAULT TRUE,
  non_repudiation_data JSONB NOT NULL,
  verification_status TEXT DEFAULT 'verified' CHECK (verification_status IN ('verified', 'failed', 'disputed')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- GDPR Data Export Requests Table
CREATE TABLE IF NOT EXISTS gdpr_data_export_requests (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  export_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  personal_data JSONB,
  format TEXT DEFAULT 'json' CHECK (format IN ('json', 'csv')),
  status TEXT DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'failed')),
  download_url TEXT,
  expires_at TIMESTAMP WITH TIME ZONE,
  request_ip INET,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- GDPR Account Deletion Requests Table
CREATE TABLE IF NOT EXISTS gdpr_deletion_requests (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  reason TEXT,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'cancelled')),
  requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  scheduled_for TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  processed_by UUID REFERENCES auth.users(id),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Consent Logs Table
CREATE TABLE IF NOT EXISTS consent_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  consent_type TEXT NOT NULL CHECK (consent_type IN ('terms_of_service', 'privacy_policy', 'contract_terms', 'marketing')),
  version TEXT NOT NULL,
  consent_given BOOLEAN NOT NULL,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ip_address INET NOT NULL,
  user_agent TEXT NOT NULL,
  method TEXT NOT NULL CHECK (method IN ('click', 'biometric', 'electronic_signature')),
  withdrawal_date TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Compliance Audit Log Table
CREATE TABLE IF NOT EXISTS compliance_audit_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  action TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('kyc', 'sanctions', 'transaction', 'data_protection', 'esignature', 'pci')),
  severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
  details JSONB NOT NULL DEFAULT '{}'::jsonb,
  ip_address INET,
  user_agent TEXT,
  outcome TEXT CHECK (outcome IN ('success', 'failure', 'flagged')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Compliance Alerts Table
CREATE TABLE IF NOT EXISTS compliance_alerts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  alert_type TEXT NOT NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  details JSONB NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
  status TEXT DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'false_positive')),
  assigned_to UUID REFERENCES auth.users(id),
  resolved_by UUID REFERENCES auth.users(id),
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolution_notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tokenized Payments Table (PCI DSS Compliance)
CREATE TABLE IF NOT EXISTS tokenized_payments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  token TEXT NOT NULL,
  last4 TEXT NOT NULL,
  expiry_month TEXT NOT NULL,
  expiry_year TEXT NOT NULL,
  card_brand TEXT NOT NULL,
  token_expiry TIMESTAMP WITH TIME ZONE,
  is_default BOOLEAN DEFAULT FALSE,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'expired', 'revoked')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scheduled Deletions Table (GDPR Right to Erasure)
CREATE TABLE IF NOT EXISTS scheduled_deletions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
  status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'processing', 'completed', 'failed')),
  data_categories TEXT[] NOT NULL,
  retention_exceptions TEXT[] DEFAULT '{}',
  processed_at TIMESTAMP WITH TIME ZONE,
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance Metrics Table (for compliance monitoring)
CREATE TABLE IF NOT EXISTS performance_metrics (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  metric_type TEXT NOT NULL,
  metric_value DECIMAL(15,4) NOT NULL,
  metric_unit TEXT,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  additional_data JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_kyc_profiles_user_id ON kyc_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_kyc_profiles_status ON kyc_profiles(status);
CREATE INDEX IF NOT EXISTS idx_kyc_profiles_sanctions_status ON kyc_profiles(sanctions_status);
CREATE INDEX IF NOT EXISTS idx_sanctions_screening_user_id ON sanctions_screening_results(user_id);
CREATE INDEX IF NOT EXISTS idx_sanctions_screening_status ON sanctions_screening_results(status);
CREATE INDEX IF NOT EXISTS idx_transaction_monitoring_user_id ON transaction_monitoring(user_id);
CREATE INDEX IF NOT EXISTS idx_transaction_monitoring_status ON transaction_monitoring(status);
CREATE INDEX IF NOT EXISTS idx_transaction_monitoring_timestamp ON transaction_monitoring(timestamp);
CREATE INDEX IF NOT EXISTS idx_esignature_logs_contract_id ON esignature_compliance_logs(contract_id);
CREATE INDEX IF NOT EXISTS idx_esignature_logs_user_id ON esignature_compliance_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_gdpr_exports_user_id ON gdpr_data_export_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_gdpr_deletions_user_id ON gdpr_deletion_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_consent_logs_user_id ON consent_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_consent_logs_type ON consent_logs(consent_type);
CREATE INDEX IF NOT EXISTS idx_compliance_audit_user_id ON compliance_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_compliance_audit_category ON compliance_audit_log(category);
CREATE INDEX IF NOT EXISTS idx_compliance_audit_severity ON compliance_audit_log(severity);
CREATE INDEX IF NOT EXISTS idx_compliance_audit_created_at ON compliance_audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_compliance_alerts_user_id ON compliance_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_compliance_alerts_status ON compliance_alerts(status);
CREATE INDEX IF NOT EXISTS idx_compliance_alerts_severity ON compliance_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_tokenized_payments_user_id ON tokenized_payments(user_id);
CREATE INDEX IF NOT EXISTS idx_tokenized_payments_token ON tokenized_payments(token);
CREATE INDEX IF NOT EXISTS idx_scheduled_deletions_user_id ON scheduled_deletions(user_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_deletions_scheduled_for ON scheduled_deletions(scheduled_for);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_type ON performance_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp);

-- Enable Row Level Security (RLS)
ALTER TABLE kyc_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE sanctions_screening_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE transaction_monitoring ENABLE ROW LEVEL SECURITY;
ALTER TABLE esignature_compliance_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE gdpr_data_export_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE gdpr_deletion_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE consent_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE tokenized_payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE scheduled_deletions ENABLE ROW LEVEL SECURITY;

-- RLS Policies - Admin-only access for compliance tables
CREATE POLICY "Admin only KYC profiles access" ON kyc_profiles
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

CREATE POLICY "Admin only sanctions screening access" ON sanctions_screening_results
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

CREATE POLICY "Admin only transaction monitoring access" ON transaction_monitoring
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

CREATE POLICY "Admin only esignature logs access" ON esignature_compliance_logs
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

CREATE POLICY "Admin only GDPR exports access" ON gdpr_data_export_requests
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

CREATE POLICY "Admin only GDPR deletions access" ON gdpr_deletion_requests
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

CREATE POLICY "Admin only consent logs access" ON consent_logs
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

CREATE POLICY "Admin only compliance audit access" ON compliance_audit_log
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

CREATE POLICY "Admin only compliance alerts access" ON compliance_alerts
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

CREATE POLICY "User own tokenized payments access" ON tokenized_payments
  FOR ALL
  USING (auth.uid() = user_id OR auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = user_id OR auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

CREATE POLICY "Admin only scheduled deletions access" ON scheduled_deletions
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- User-specific consent logs access
CREATE POLICY "User own consent logs access" ON consent_logs
  FOR SELECT
  USING (auth.uid() = user_id);

-- User own GDPR requests access
CREATE POLICY "User own GDPR exports access" ON gdpr_data_export_requests
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "User own GDPR deletions access" ON gdpr_deletion_requests
  FOR SELECT
  USING (auth.uid() = user_id);

-- Create Updated At Trigger Function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create Triggers
CREATE TRIGGER update_kyc_profiles_updated_at BEFORE UPDATE ON kyc_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create Compliance Monitoring Functions
CREATE OR REPLACE FUNCTION check_transaction_compliance(p_user_id UUID, p_amount DECIMAL)
RETURNS TABLE(
  is_compliant BOOLEAN,
  tier_limit DECIMAL,
  current_tier INTEGER,
  requires_review BOOLEAN,
  reason TEXT
) AS $$
DECLARE
  user_tier INTEGER;
  tier_limit_value DECIMAL;
  exceeds_limit BOOLEAN;
BEGIN
  -- Get user's KYC tier
  SELECT tier INTO user_tier FROM kyc_profiles WHERE user_id = p_user_id AND status = 'approved';
  
  IF user_tier IS NULL THEN
    RETURN QUERY SELECT FALSE, 0, 0, TRUE, 'KYC not completed or approved'::TEXT;
    RETURN;
  END IF;
  
  -- Get tier limits
  CASE user_tier
    WHEN 1 THEN tier_limit_value := 1000;
    WHEN 2 THEN tier_limit_value := 10000;
    WHEN 3 THEN tier_limit_value := 50000;
    ELSE tier_limit_value := 0;
  END CASE;
  
  exceeds_limit := p_amount > tier_limit_value;
  
  RETURN QUERY 
  SELECT 
    NOT exceeds_limit,
    tier_limit_value,
    user_tier,
    exceeds_limit OR p_amount > 3000,
    CASE 
      WHEN exceeds_limit THEN 'Amount exceeds tier limit of $' || tier_limit_value
      WHEN p_amount > 3000 THEN 'Amount exceeds NBE limit of $3000'
      ELSE 'Transaction compliant'
    END::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Create Sanctions Screening Function
CREATE OR REPLACE FUNCTION screen_user_for_sanctions(p_user_id UUID)
RETURNS TABLE(
  is_clear BOOLEAN,
  flagged_count INTEGER,
  requires_review BOOLEAN,
  screening_result JSONB
) AS $$
DECLARE
  last_screening TIMESTAMP WITH TIME ZONE;
  screening_interval INTERVAL := '24 hours';
  needs_screening BOOLEAN;
  flagged_count_value INTEGER := 0;
BEGIN
  -- Check if user needs screening
  SELECT MAX(screened_at) INTO last_screening 
  FROM sanctions_screening_results 
  WHERE user_id = p_user_id;
  
  needs_screening := last_screening IS NULL OR (NOW() - last_screening) > screening_interval;
  
  IF needs_screening THEN
    -- Simulate sanctions screening (in production, integrate with real APIs)
    INSERT INTO sanctions_screening_results (user_id, status, requires_manual_review)
    VALUES (p_user_id, 'clear', FALSE);
  END IF;
  
  -- Get latest screening result
  SELECT 
    (status = 'clear')::BOOLEAN,
    jsonb_array_length(matches)::INTEGER,
    requires_manual_review,
    to_jsonb(screening_results.*)
  INTO is_clear, flagged_count_value, requires_review, screening_result
  FROM sanctions_screening_results 
  WHERE user_id = p_user_id 
  ORDER BY screened_at DESC 
  LIMIT 1;
  
  RETURN QUERY SELECT is_clear, flagged_count_value, requires_review, screening_result;
END;
$$ LANGUAGE plpgsql;

-- Create GDPR Data Export Function
CREATE OR REPLACE FUNCTION export_user_data(p_user_id UUID, p_format TEXT DEFAULT 'json')
RETURNS UUID AS $$
DECLARE
  export_id UUID;
  user_data JSONB;
BEGIN
  -- Collect all user data
  SELECT jsonb_build_object(
    'profile', to_jsonb(up),
    'transactions', to_jsonb(array_agg(t)),
    'contracts', to_jsonb(array_agg(c)),
    'kyc_data', to_jsonb(k),
    'audit_logs', to_jsonb(array_agg(cal))
  ) INTO user_data
  FROM auth.users u
  LEFT JOIN user_profiles up ON u.id = up.user_id
  LEFT JOIN transactions t ON u.id = t.user_id
  LEFT JOIN contracts c ON (u.id = c.seller_id OR u.id = c.buyer_id)
  LEFT JOIN kyc_profiles k ON u.id = k.user_id
  LEFT JOIN compliance_audit_log cal ON u.id = cal.user_id
  WHERE u.id = p_user_id
  GROUP BY u.id, up.user_id, k.user_id;
  
  -- Create export record
  INSERT INTO gdpr_data_export_requests (
    user_id, 
    personal_data, 
    format, 
    status,
    expires_at
  ) VALUES (
    p_user_id,
    user_data,
    p_format,
    'completed',
    NOW() + INTERVAL '7 days'
  ) RETURNING id INTO export_id;
  
  -- Log export request
  INSERT INTO compliance_audit_log (
    user_id, 
    action, 
    category, 
    severity, 
    details,
    outcome
  ) VALUES (
    p_user_id,
    'data_export_requested',
    'data_protection',
    'medium',
    jsonb_build_object('format', p_format, 'export_id', export_id),
    'success'
  );
  
  RETURN export_id;
END;
$$ LANGUAGE plpgsql;

-- Create Account Deletion Function
CREATE OR REPLACE FUNCTION request_account_deletion(p_user_id UUID, p_reason TEXT)
RETURNS UUID AS $$
DECLARE
  deletion_id UUID;
  scheduled_date TIMESTAMP WITH TIME ZONE;
BEGIN
  -- Schedule deletion for 30 days from now (GDPR requirement)
  scheduled_date := NOW() + INTERVAL '30 days';
  
  -- Create deletion request
  INSERT INTO gdpr_deletion_requests (
    user_id,
    reason,
    scheduled_for,
    status
  ) VALUES (
    p_user_id,
    p_reason,
    scheduled_date,
    'pending'
  ) RETURNING id INTO deletion_id;
  
  -- Log deletion request
  INSERT INTO compliance_audit_log (
    user_id,
    action,
    category,
    severity,
    details,
    outcome
  ) VALUES (
    p_user_id,
    'account_deletion_requested',
    'data_protection',
    'high',
    jsonb_build_object('reason', p_reason, 'scheduled_for', scheduled_date),
    'success'
  );
  
  RETURN deletion_id;
END;
$$ LANGUAGE plpgsql;

-- Create Performance Metrics Collection Function
CREATE OR REPLACE FUNCTION collect_performance_metrics()
RETURNS VOID AS $$
BEGIN
  -- Collect KYC compliance metrics
  INSERT INTO performance_metrics (metric_type, metric_value, metric_unit, additional_data)
  SELECT 
    'kyc_compliant_users',
    COUNT(*)::DECIMAL,
    'count',
    jsonb_build_object('tier', tier, 'status', status)
  FROM kyc_profiles 
  WHERE status = 'approved';
  
  -- Collect transaction monitoring metrics
  INSERT INTO performance_metrics (metric_type, metric_value, metric_unit, additional_data)
  SELECT 
    'flagged_transactions',
    COUNT(*)::DECIMAL,
    'count',
    jsonb_build_object('severity', severity)
  FROM transaction_monitoring 
  WHERE status = 'flagged' AND created_at >= NOW() - INTERVAL '24 hours';
  
  -- Collect sanctions screening metrics
  INSERT INTO performance_metrics (metric_type, metric_value, metric_unit, additional_data)
  SELECT 
    'sanctions_screened',
    COUNT(*)::DECIMAL,
    'count',
    jsonb_build_object('status', status)
  FROM sanctions_screening_results 
  WHERE screened_at >= NOW() - INTERVAL '24 hours';
  
  -- Collect consent metrics
  INSERT INTO performance_metrics (metric_type, metric_value, metric_unit, additional_data)
  SELECT 
    'consent_given',
    COUNT(*)::DECIMAL,
    'count',
    jsonb_build_object('type', consent_type)
  FROM consent_logs 
  WHERE consent_given = TRUE AND created_at >= NOW() - INTERVAL '24 hours';
END;
$$ LANGUAGE plpgsql;

-- Create scheduled job for performance metrics (requires pg_cron extension)
-- SELECT cron.schedule('collect-metrics', '0 */6 * * *', 'SELECT collect_performance_metrics();');

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Create initial performance metrics record
INSERT INTO performance_metrics (metric_type, metric_value, metric_unit, additional_data)
VALUES ('system_initialized', 1, 'count', jsonb_build_object('timestamp', NOW()));

COMMENT ON TABLE kyc_profiles IS 'KYC verification profiles for compliance with Ethiopian regulations';
COMMENT ON TABLE sanctions_screening_results IS 'Results of sanctions screening against OFAC/UN lists';
COMMENT ON TABLE transaction_monitoring IS 'AI-driven transaction monitoring for AML compliance';
COMMENT ON TABLE esignature_compliance_logs IS 'E-signature compliance logs for Ethiopian Electronic Signature Proclamation';
COMMENT ON TABLE gdpr_data_export_requests IS 'GDPR data export requests and results';
COMMENT ON TABLE gdpr_deletion_requests IS 'GDPR right to erasure requests';
COMMENT ON TABLE consent_logs IS 'User consent tracking for GDPR compliance';
COMMENT ON TABLE compliance_audit_log IS 'Comprehensive audit trail for all compliance activities';
COMMENT ON TABLE compliance_alerts IS 'Compliance alerts requiring attention';
COMMENT ON TABLE tokenized_payments IS 'Tokenized payment information (PCI DSS compliant)';
COMMENT ON TABLE scheduled_deletions IS 'Scheduled data deletions for GDPR compliance';
COMMENT ON TABLE performance_metrics IS 'Performance metrics for compliance monitoring';
