-- Create platform_finances table for tracking commissions and fees
CREATE TABLE IF NOT EXISTS platform_finances (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  total_commissions DECIMAL(20,8) DEFAULT 0.00000000 NOT NULL,
  total_fees DECIMAL(20,8) DEFAULT 0.00000000 NOT NULL,
  available_balance DECIMAL(20,8) DEFAULT 0.00000000 NOT NULL,
  pending_withdrawals DECIMAL(20,8) DEFAULT 0.00000000 NOT NULL,
  total_withdrawn DECIMAL(20,8) DEFAULT 0.00000000 NOT NULL,
  last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create withdrawals table for tracking admin withdrawals
CREATE TABLE IF NOT EXISTS withdrawals (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  amount DECIMAL(20,8) NOT NULL CHECK (amount > 0),
  status TEXT NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')) DEFAULT 'pending',
  withdrawal_address TEXT NOT NULL,
  transaction_hash TEXT,
  idempotency_key TEXT UNIQUE NOT NULL,
  admin_id UUID NOT NULL REFERENCES auth.users(id),
  biometric_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  processed_at TIMESTAMP WITH TIME ZONE,
  notes TEXT
);

-- Create admin_audit_log table for security tracking
CREATE TABLE IF NOT EXISTS admin_audit_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  admin_id UUID NOT NULL REFERENCES auth.users(id),
  action TEXT NOT NULL,
  details JSONB,
  ip_address INET,
  user_agent TEXT,
  severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'critical')) DEFAULT 'info',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE platform_finances ENABLE ROW LEVEL SECURITY;
ALTER TABLE withdrawals ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_audit_log ENABLE ROW LEVEL SECURITY;

-- Create indexes for performance
CREATE INDEX idx_withdrawals_admin_id ON withdrawals(admin_id);
CREATE INDEX idx_withdrawals_status ON withdrawals(status);
CREATE INDEX idx_withdrawals_created_at ON withdrawals(created_at DESC);
CREATE INDEX idx_admin_audit_log_admin_id ON admin_audit_log(admin_id);
CREATE INDEX idx_admin_audit_log_created_at ON admin_audit_log(created_at DESC);
CREATE INDEX idx_admin_audit_log_severity ON admin_audit_log(severity);

-- Create function to automatically update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_platform_finances_updated_at
  BEFORE UPDATE ON platform_finances
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_withdrawals_updated_at
  BEFORE UPDATE ON withdrawals
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Create function to update platform finances
CREATE OR REPLACE FUNCTION update_platform_finances(
  p_amount DECIMAL,
  p_type TEXT,
  p_admin_id UUID
)
RETURNS BOOLEAN AS $$
DECLARE
  v_current_balance DECIMAL;
BEGIN
  -- Lock the row to prevent concurrent modifications
  SELECT available_balance INTO v_current_balance 
  FROM platform_finances 
  FOR UPDATE;
  
  IF p_type = 'commission_earned' THEN
    UPDATE platform_finances 
    SET 
      total_commissions = total_commissions + p_amount,
      available_balance = available_balance + p_amount;
  ELSIF p_type = 'fee_earned' THEN
    UPDATE platform_finances 
    SET 
      total_fees = total_fees + p_amount,
      available_balance = available_balance + p_amount;
  ELSIF p_type = 'withdrawal_initiated' THEN
    -- Check if sufficient balance is available
    IF v_current_balance < p_amount THEN
      RETURN FALSE;
    END IF;
    
    UPDATE platform_finances 
    SET 
      available_balance = available_balance - p_amount,
      pending_withdrawals = pending_withdrawals + p_amount;
  ELSIF p_type = 'withdrawal_completed' THEN
    UPDATE platform_finances 
    SET 
      pending_withdrawals = pending_withdrawals - p_amount,
      total_withdrawn = total_withdrawn + p_amount;
  ELSIF p_type = 'withdrawal_failed' THEN
    UPDATE platform_finances 
    SET 
      available_balance = available_balance + p_amount,
      pending_withdrawals = pending_withdrawals - p_amount;
  END IF;
  
  -- Log the action
  INSERT INTO admin_audit_log (admin_id, action, details, severity)
  VALUES (
    p_admin_id,
    'platform_finances_update',
    json_build_object('amount', p_amount, 'type', p_type, 'new_balance', 
      (SELECT available_balance FROM platform_finances)),
    'info'
  );
  
  RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Initialize platform finances if not exists
INSERT INTO platform_finances (total_commissions, total_fees, available_balance)
VALUES (0, 0, 0)
ON CONFLICT DO NOTHING;

-- RESTRICTIVE RLS Policies - ONLY ADMIN CAN ACCESS

-- Platform finances policy - ONLY admin can read/write
CREATE POLICY "Admin only platform finances access" ON platform_finances
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- Withdrawals policy - ONLY admin can read/write their own withdrawals
CREATE POLICY "Admin only withdrawals access" ON withdrawals
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- Audit log policy - ONLY admin can read/write their own logs
CREATE POLICY "Admin only audit log access" ON admin_audit_log
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');

-- Create function to check if user is admin
CREATE OR REPLACE FUNCTION is_admin_user()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN auth.uid() = 'YOUR_ADMIN_USER_ID_HERE';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create view for admin dashboard (simplified access)
CREATE OR REPLACE VIEW admin_dashboard AS
SELECT 
  pf.total_commissions,
  pf.total_fees,
  pf.available_balance,
  pf.pending_withdrawals,
  pf.total_withdrawn,
  pf.last_updated,
  (SELECT COUNT(*) FROM withdrawals WHERE status = 'pending') as pending_count,
  (SELECT COUNT(*) FROM withdrawals WHERE status = 'processing') as processing_count,
  (SELECT COUNT(*) FROM withdrawals WHERE created_at >= NOW() - INTERVAL '24 hours') as withdrawals_24h
FROM platform_finances pf;

-- Grant access to admin view
GRANT SELECT ON admin_dashboard TO authenticated;

-- Create RLS policy for admin view
CREATE POLICY "Admin only dashboard access" ON admin_dashboard
  FOR SELECT
  USING (is_admin_user());
