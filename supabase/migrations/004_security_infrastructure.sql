-- Multi-Layer Security Infrastructure Migration
-- Implements comprehensive security for fund withdrawals

-- Security Settings Table
CREATE TABLE IF NOT EXISTS security_settings (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  daily_withdrawal_limit DECIMAL(20,8) DEFAULT 10000.00 NOT NULL,
  require_secondary_approval BOOLEAN DEFAULT TRUE,
  require_biometric_reauth BOOLEAN DEFAULT TRUE,
  require_totp BOOLEAN DEFAULT FALSE,
  trusted_device_required BOOLEAN DEFAULT TRUE,
  email_verified BOOLEAN DEFAULT FALSE,
  totp_enabled BOOLEAN DEFAULT FALSE,
  biometric_enabled BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trusted Devices Table
CREATE TABLE IF NOT EXISTS trusted_devices (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  name TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  user_agent TEXT NOT NULL,
  ip_address INET NOT NULL,
  location JSONB NOT NULL,
  first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE,
  is_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Whitelisted Addresses Table
CREATE TABLE IF NOT EXISTS whitelisted_addresses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('bank_account', 'crypto_wallet')),
  name TEXT NOT NULL,
  address TEXT NOT NULL,
  bank_name TEXT,
  account_number TEXT,
  wallet_type TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_used TIMESTAMP WITH TIME ZONE,
  cooldown_until TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Security Holds Table
CREATE TABLE IF NOT EXISTS security_holds (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  reason TEXT NOT NULL CHECK (reason IN ('new_device', 'address_change', 'limit_exceeded', 'suspicious_activity')),
  amount DECIMAL(20,8),
  currency TEXT DEFAULT 'USD',
  address TEXT,
  device_fingerprint TEXT,
  hold_until TIMESTAMP WITH TIME ZONE NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolved_by UUID REFERENCES auth.users(id),
  notes TEXT,
  ip_address INET,
  user_agent TEXT,
  geolocation JSONB
);

-- Biometric Credentials Table
CREATE TABLE IF NOT EXISTS biometric_credentials (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  credential_id TEXT NOT NULL,
  public_key TEXT NOT NULL,
  device_fingerprint TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE,
  user_agent TEXT,
  ip_address INET
);

-- TOTP Secrets Table
CREATE TABLE IF NOT EXISTS totp_secrets (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  secret TEXT NOT NULL,
  backup_codes TEXT[],
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- TOTP Verification Logs Table
CREATE TABLE IF NOT EXISTS totp_verification_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  token TEXT NOT NULL,
  is_valid BOOLEAN NOT NULL,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Secondary Approvals Table
CREATE TABLE IF NOT EXISTS secondary_approvals (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  amount DECIMAL(20,8) NOT NULL,
  currency TEXT DEFAULT 'USD',
  address TEXT NOT NULL,
  address_type TEXT NOT NULL CHECK (address_type IN ('bank_account', 'crypto_wallet')),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  is_approved BOOLEAN DEFAULT FALSE,
  approved_at TIMESTAMP WITH TIME ZONE,
  approved_by UUID REFERENCES auth.users(id),
  approval_token TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  device_fingerprint TEXT,
  ip_address INET,
  user_agent TEXT,
  withdrawal_id UUID REFERENCES withdrawals(id)
);

-- Suspicious Activities Table
CREATE TABLE IF NOT EXISTS suspicious_activities (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  type TEXT NOT NULL,
  description TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
  ip_address INET NOT NULL,
  user_agent TEXT NOT NULL,
  geolocation JSONB,
  is_investigated BOOLEAN DEFAULT FALSE,
  investigated_at TIMESTAMP WITH TIME ZONE,
  investigated_by UUID REFERENCES auth.users(id),
  investigation_notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Security Admin Actions Table
CREATE TABLE IF NOT EXISTS security_admin_actions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  action_type TEXT NOT NULL CHECK (action_type IN ('resolve_hold', 'investigate_activity', 'approve_secondary', 'reject_secondary')),
  target_id TEXT NOT NULL,
  notes TEXT,
  admin_id UUID REFERENCES auth.users(id) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ip_address INET,
  user_agent TEXT
);

-- Withdrawal Attempts Table (for tracking failed attempts)
CREATE TABLE IF NOT EXISTS withdrawal_attempts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  amount DECIMAL(20,8) NOT NULL,
  currency TEXT DEFAULT 'USD',
  address TEXT NOT NULL,
  address_type TEXT NOT NULL CHECK (address_type IN ('bank_account', 'crypto_wallet')),
  idempotency_key TEXT NOT NULL,
  device_fingerprint TEXT NOT NULL,
  biometric_hash TEXT,
  totp_token TEXT,
  status TEXT NOT NULL CHECK (status IN ('pending', 'failed', 'blocked', 'held')),
  failure_reason TEXT,
  ip_address INET NOT NULL,
  user_agent TEXT NOT NULL,
  geolocation JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enhanced Withdrawals Table (add security columns)
ALTER TABLE withdrawals ADD COLUMN IF NOT EXISTS device_fingerprint TEXT;
ALTER TABLE withdrawals ADD COLUMN IF NOT EXISTS biometric_hash TEXT;
ALTER TABLE withdrawals ADD COLUMN IF NOT EXISTS totp_token TEXT;
ALTER TABLE withdrawals ADD COLUMN IF NOT EXISTS ip_address INET;
ALTER TABLE withdrawals ADD COLUMN IF NOT EXISTS user_agent TEXT;
ALTER TABLE withdrawals ADD COLUMN IF NOT EXISTS geolocation JSONB;
ALTER TABLE withdrawals ADD COLUMN IF NOT EXISTS security_checks_passed BOOLEAN DEFAULT FALSE;
ALTER TABLE withdrawals ADD COLUMN IF NOT EXISTS secondary_approval_required BOOLEAN DEFAULT FALSE;
ALTER TABLE withdrawals ADD COLUMN IF NOT EXISTS secondary_approval_id UUID REFERENCES secondary_approvals(id);

-- Withdrawal Audit Log Table
CREATE TABLE IF NOT EXISTS withdrawal_audit_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  transaction_id UUID NOT NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  amount DECIMAL(20,8) NOT NULL,
  currency TEXT DEFAULT 'USD',
  address TEXT NOT NULL,
  address_type TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'held', 'cancelled')),
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  device_fingerprint TEXT,
  ip_address INET,
  user_agent TEXT,
  geolocation JSONB,
  security_checks_passed BOOLEAN,
  admin_notes TEXT
);

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_security_settings_user_id ON security_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_trusted_devices_user_id ON trusted_devices(user_id);
CREATE INDEX IF NOT EXISTS idx_trusted_devices_fingerprint ON trusted_devices(fingerprint);
CREATE INDEX IF NOT EXISTS idx_trusted_devices_active ON trusted_devices(is_active);
CREATE INDEX IF NOT EXISTS idx_whitelisted_addresses_user_id ON whitelisted_addresses(user_id);
CREATE INDEX IF NOT EXISTS idx_whitelisted_addresses_address ON whitelisted_addresses(address);
CREATE INDEX IF NOT EXISTS idx_whitelisted_addresses_active ON whitelisted_addresses(is_active);
CREATE INDEX IF NOT EXISTS idx_security_holds_user_id ON security_holds(user_id);
CREATE INDEX IF NOT EXISTS idx_security_holds_active ON security_holds(is_active);
CREATE INDEX IF NOT EXISTS idx_security_holds_reason ON security_holds(reason);
CREATE INDEX IF NOT EXISTS idx_security_holds_until ON security_holds(hold_until);
CREATE INDEX IF NOT EXISTS idx_biometric_credentials_user_id ON biometric_credentials(user_id);
CREATE INDEX IF NOT EXISTS idx_biometric_credentials_active ON biometric_credentials(is_active);
CREATE INDEX IF NOT EXISTS idx_totp_secrets_user_id ON totp_secrets(user_id);
CREATE INDEX IF NOT EXISTS idx_totp_secrets_active ON totp_secrets(is_active);
CREATE INDEX IF NOT EXISTS idx_secondary_approvals_user_id ON secondary_approvals(user_id);
CREATE INDEX IF NOT EXISTS idx_secondary_approvals_token ON secondary_approvals(approval_token);
CREATE INDEX IF NOT EXISTS idx_secondary_approvals_expires ON secondary_approvals(expires_at);
CREATE INDEX IF NOT EXISTS idx_secondary_approvals_approved ON secondary_approvals(is_approved);
CREATE INDEX IF NOT EXISTS idx_suspicious_activities_user_id ON suspicious_activities(user_id);
CREATE INDEX IF NOT EXISTS idx_suspicious_activities_investigated ON suspicious_activities(is_investigated);
CREATE INDEX IF NOT EXISTS idx_suspicious_activities_severity ON suspicious_activities(severity);
CREATE INDEX IF NOT EXISTS idx_suspicious_activities_created ON suspicious_activities(created_at);
CREATE INDEX IF NOT EXISTS idx_admin_actions_admin_id ON security_admin_actions(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_type ON security_admin_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_admin_actions_created ON security_admin_actions(created_at);
CREATE INDEX IF NOT EXISTS idx_withdrawal_attempts_user_id ON withdrawal_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_withdrawal_attempts_status ON withdrawal_attempts(status);
CREATE INDEX IF NOT EXISTS idx_withdrawal_attempts_created ON withdrawal_attempts(created_at);
CREATE INDEX IF NOT EXISTS idx_withdrawal_audit_log_transaction_id ON withdrawal_audit_log(transaction_id);
CREATE INDEX IF NOT EXISTS idx_withdrawal_audit_log_user_id ON withdrawal_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_withdrawal_audit_log_status ON withdrawal_audit_log(status);
CREATE INDEX IF NOT EXISTS idx_withdrawal_audit_log_created ON withdrawal_audit_log(created_at);

-- Enable Row Level Security (RLS)
ALTER TABLE security_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE trusted_devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE whitelisted_addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_holds ENABLE ROW LEVEL SECURITY;
ALTER TABLE biometric_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE totp_secrets ENABLE ROW LEVEL SECURITY;
ALTER TABLE totp_verification_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE secondary_approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE suspicious_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_admin_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE withdrawal_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE withdrawal_audit_log ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Security Settings
CREATE POLICY "Users can view own security settings" ON security_settings
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own security settings" ON security_settings
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Admin can manage all security settings" ON security_settings
  FOR ALL USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- Trusted Devices
CREATE POLICY "Users can view own trusted devices" ON trusted_devices
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own trusted devices" ON trusted_devices
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own trusted devices" ON trusted_devices
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Admin can manage all trusted devices" ON trusted_devices
  FOR ALL USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- Whitelisted Addresses
CREATE POLICY "Users can view own whitelisted addresses" ON whitelisted_addresses
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own whitelisted addresses" ON whitelisted_addresses
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own whitelisted addresses" ON whitelisted_addresses
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Admin can manage all whitelisted addresses" ON whitelisted_addresses
  FOR ALL USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- Security Holds
CREATE POLICY "Users can view own security holds" ON security_holds
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Admin can manage all security holds" ON security_holds
  FOR ALL USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- Biometric Credentials
CREATE POLICY "Users can view own biometric credentials" ON biometric_credentials
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own biometric credentials" ON biometric_credentials
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own biometric credentials" ON biometric_credentials
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Admin can manage all biometric credentials" ON biometric_credentials
  FOR ALL USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- TOTP Secrets
CREATE POLICY "Users can view own TOTP secrets" ON totp_secrets
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own TOTP secrets" ON totp_secrets
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own TOTP secrets" ON totp_secrets
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Admin can manage all TOTP secrets" ON totp_secrets
  FOR ALL USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- Secondary Approvals
CREATE POLICY "Users can view own secondary approvals" ON secondary_approvals
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own secondary approvals" ON secondary_approvals
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Admin can manage all secondary approvals" ON secondary_approvals
  FOR ALL USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- Suspicious Activities
CREATE POLICY "Users can view own suspicious activities" ON suspicious_activities
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Admin can manage all suspicious activities" ON suspicious_activities
  FOR ALL USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- Security Admin Actions
CREATE POLICY "Admin can view own admin actions" ON security_admin_actions
  FOR SELECT USING (auth.uid() = admin_id);

CREATE POLICY "Admin can insert own admin actions" ON security_admin_actions
  FOR INSERT WITH CHECK (auth.uid() = admin_id);

-- Withdrawal Attempts
CREATE POLICY "Users can view own withdrawal attempts" ON withdrawal_attempts
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Admin can manage all withdrawal attempts" ON withdrawal_attempts
  FOR ALL USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- Withdrawal Audit Log
CREATE POLICY "Users can view own withdrawal audit logs" ON withdrawal_audit_log
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Admin can manage all withdrawal audit logs" ON withdrawal_audit_log
  FOR ALL USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- Create Functions

-- Process Withdrawal Transaction (Atomic Operation)
CREATE OR REPLACE FUNCTION process_withdrawal_transaction(
  p_user_id UUID,
  p_amount DECIMAL(20,8),
  p_currency TEXT,
  p_address TEXT,
  p_address_type TEXT,
  p_transaction_id UUID,
  p_idempotency_key TEXT,
  p_device_fingerprint TEXT,
  p_ip_address INET,
  p_user_agent TEXT,
  p_geolocation JSONB DEFAULT NULL
)
RETURNS TABLE(
  success BOOLEAN,
  transaction_id UUID,
  error_message TEXT
) AS $$
DECLARE
  current_balance DECIMAL(20,8);
  new_balance DECIMAL(20,8);
BEGIN
  -- Start transaction
  -- Lock the user's finances row to prevent concurrent modifications
  SELECT available_balance INTO current_balance
  FROM platform_finances
  FOR UPDATE;
  
  -- Check if sufficient balance
  IF current_balance < p_amount THEN
    RETURN QUERY SELECT FALSE, NULL, 'Insufficient balance'::TEXT;
  END IF;
  
  -- Calculate new balance
  new_balance := current_balance - p_amount;
  
  -- Update finances
  UPDATE platform_finances
  SET 
    available_balance = new_balance,
    total_withdrawn = total_withdrawn + p_amount,
    last_updated = NOW()
  WHERE available_balance = current_balance;
  
  -- Insert withdrawal record
  INSERT INTO withdrawals (
    id,
    user_id,
    amount,
    currency,
    withdrawal_address,
    address_type,
    status,
    idempotency_key,
    device_fingerprint,
    ip_address,
    user_agent,
    geolocation,
    security_checks_passed,
    created_at
  ) VALUES (
    p_transaction_id,
    p_user_id,
    p_amount,
    p_currency,
    p_address,
    p_address_type,
    'completed',
    p_idempotency_key,
    p_device_fingerprint,
    p_ip_address,
    p_user_agent,
    p_geolocation,
    TRUE,
    NOW()
  );
  
  -- Return success
  RETURN QUERY SELECT TRUE, p_transaction_id, NULL::TEXT;
  
EXCEPTION
  WHEN OTHERS THEN
    -- Rollback on error
    RETURN QUERY SELECT FALSE, NULL, SQLERRM::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Function to Check Device Trust
CREATE OR REPLACE FUNCTION is_device_trusted(
  p_user_id UUID,
  p_device_fingerprint TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
  device_count INTEGER;
  device_age_hours NUMERIC;
BEGIN
  -- Check if device exists and is active
  SELECT COUNT(*), EXTRACT(EPOCH FROM (NOW() - first_seen)) / 3600
  INTO device_count, device_age_hours
  FROM trusted_devices
  WHERE user_id = p_user_id
    AND fingerprint = p_device_fingerprint
    AND is_active = TRUE;
  
  -- Device must exist and be registered for at least 48 hours
  RETURN device_count = 1 AND device_age_hours >= 48;
END;
$$ LANGUAGE plpgsql;

-- Function to Check Address Whitelist
CREATE OR REPLACE FUNCTION is_address_whitelisted(
  p_user_id UUID,
  p_address TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
  address_count INTEGER;
  cooldown_end TIMESTAMP;
BEGIN
  -- Check if address is whitelisted and not in cooldown
  SELECT COUNT(*), cooldown_until
  INTO address_count, cooldown_end
  FROM whitelisted_addresses
  WHERE user_id = p_user_id
    AND address = p_address
    AND is_active = TRUE;
  
  -- Address must be whitelisted and either not in cooldown or cooldown has expired
  RETURN address_count = 1 AND (cooldown_end IS NULL OR cooldown_end < NOW());
END;
$$ LANGUAGE plpgsql;

-- Function to Check Daily Withdrawal Limit
CREATE OR REPLACE FUNCTION check_daily_withdrawal_limit(
  p_user_id UUID,
  p_amount DECIMAL(20,8),
  p_currency TEXT DEFAULT 'USD'
)
RETURNS TABLE(
  within_limit BOOLEAN,
  current_daily_total DECIMAL(20,8),
  daily_limit DECIMAL(20,8),
  requires_approval BOOLEAN
) AS $$
DECLARE
  settings RECORD;
  today_total DECIMAL(20,8);
BEGIN
  -- Get user's security settings
  SELECT daily_withdrawal_limit, require_secondary_approval
  INTO settings
  FROM security_settings
  WHERE user_id = p_user_id;
  
  -- Calculate today's withdrawals
  SELECT COALESCE(SUM(amount), 0)
  INTO today_total
  FROM withdrawals
  WHERE user_id = p_user_id
    AND currency = p_currency
    AND status = 'completed'
    AND DATE(created_at) = CURRENT_DATE;
  
  -- Check if within limit
  RETURN QUERY
  SELECT
    (today_total + p_amount) <= settings.daily_withdrawal_limit,
    today_total,
    settings.daily_withdrawal_limit,
    settings.require_secondary_approval AND p_amount > (settings.daily_withdrawal_limit * 0.5);
END;
$$ LANGUAGE plpgsql;

-- Function to Log Security Event
CREATE OR REPLACE FUNCTION log_security_event(
  p_event_type TEXT,
  p_user_id UUID,
  p_details JSONB DEFAULT NULL,
  p_severity TEXT DEFAULT 'medium',
  p_ip_address INET DEFAULT NULL,
  p_user_agent TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  event_id UUID;
BEGIN
  -- Insert into suspicious_activities if it's a security event
  IF p_event_type IN ('suspicious_activity', 'failed_biometric', 'failed_totp', 'unusual_location') THEN
    INSERT INTO suspicious_activities (
      user_id,
      type,
      description,
      severity,
      ip_address,
      user_agent,
      created_at
    ) VALUES (
      p_user_id,
      p_event_type,
      COALESCE((p_details->>'description')::TEXT, p_event_type),
      p_severity,
      p_ip_address,
      p_user_agent,
      NOW()
    ) RETURNING id INTO event_id;
  END IF;
  
  RETURN COALESCE(event_id, gen_random_uuid());
END;
$$ LANGUAGE plpgsql;

-- Function to Create Security Hold
CREATE OR REPLACE FUNCTION create_security_hold(
  p_user_id UUID,
  p_reason TEXT,
  p_amount DECIMAL(20,8) DEFAULT NULL,
  p_currency TEXT DEFAULT 'USD',
  p_address TEXT DEFAULT NULL,
  p_device_fingerprint TEXT DEFAULT NULL,
  p_hold_duration_hours INTEGER DEFAULT 24,
  p_ip_address INET DEFAULT NULL,
  p_user_agent TEXT DEFAULT NULL,
  p_geolocation JSONB DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  hold_id UUID;
  hold_until TIMESTAMP;
BEGIN
  hold_until := NOW() + (p_hold_duration_hours || 24) * INTERVAL '1 hour';
  
  INSERT INTO security_holds (
    user_id,
    reason,
    amount,
    currency,
    address,
    device_fingerprint,
    hold_until,
    is_active,
    created_at,
    ip_address,
    user_agent,
    geolocation
  ) VALUES (
    p_user_id,
    p_reason,
    p_amount,
    p_currency,
    p_address,
    p_device_fingerprint,
    hold_until,
    TRUE,
    NOW(),
    p_ip_address,
    p_user_agent,
    p_geolocation
  ) RETURNING id INTO hold_id;
  
  RETURN hold_id;
END;
$$ LANGUAGE plpgsql;

-- Triggers for Updated At
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to security_settings
CREATE TRIGGER update_security_settings_updated_at 
    BEFORE UPDATE ON security_settings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Insert default security settings for existing users
INSERT INTO security_settings (user_id, daily_withdrawal_limit)
SELECT 
  id,
  10000.00
FROM auth.users
WHERE id NOT IN (SELECT user_id FROM security_settings);

-- Comments for documentation
COMMENT ON TABLE security_settings IS 'User security preferences and limits';
COMMENT ON TABLE trusted_devices IS 'Trusted devices for withdrawals';
COMMENT ON TABLE whitelisted_addresses IS 'Whitelisted withdrawal addresses';
COMMENT ON TABLE security_holds IS 'Security holds on withdrawals';
COMMENT ON TABLE biometric_credentials IS 'WebAuthn biometric credentials';
COMMENT ON TABLE totp_secrets IS 'TOTP authentication secrets';
COMMENT ON TABLE secondary_approvals IS 'Secondary approval requirements';
COMMENT ON TABLE suspicious_activities IS 'Suspicious activity tracking';
COMMENT ON TABLE security_admin_actions IS 'Admin action audit log';
COMMENT ON TABLE withdrawal_attempts IS 'Failed withdrawal attempts';
COMMENT ON TABLE withdrawal_audit_log IS 'Complete withdrawal audit trail';

COMMENT ON FUNCTION process_withdrawal_transaction IS 'Atomic withdrawal processing with balance check';
COMMENT ON FUNCTION is_device_trusted IS 'Check if device is trusted and meets age requirement';
COMMENT ON FUNCTION is_address_whitelisted IS 'Check if address is whitelisted and not in cooldown';
COMMENT ON FUNCTION check_daily_withdrawal_limit IS 'Check daily withdrawal limits and approval requirements';
COMMENT ON FUNCTION log_security_event IS 'Log security events for monitoring';
COMMENT ON FUNCTION create_security_hold IS 'Create security hold on user account';
