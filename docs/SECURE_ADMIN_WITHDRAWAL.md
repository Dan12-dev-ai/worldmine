# Secure Admin Withdrawal System

## 🔐 Overview

The Secure Admin Withdrawal system ensures that ONLY the primary administrator can access and move commission funds from the Worldmine platform. This system implements defense-in-depth security with multiple layers of protection.

## 🏗️ Architecture

### 1. Database Layer (Supabase RLS)
- **Restrictive Row Level Security** policies
- **Admin-only access** to financial tables
- **Comprehensive audit logging**

### 2. Server-Side Verification (Edge Functions)
- **JWT token re-verification**
- **Admin ID validation**
- **Idempotency key protection**
- **Security event logging**

### 3. Frontend Lockdown
- **Protected routes** with automatic redirects
- **Biometric authentication** (WebAuthn)
- **Real-time admin status verification**

## 📊 Database Schema

### Tables Created

#### `platform_finances`
```sql
- id: UUID (Primary Key)
- total_commissions: DECIMAL(20,8)
- total_fees: DECIMAL(20,8)
- available_balance: DECIMAL(20,8)
- pending_withdrawals: DECIMAL(20,8)
- total_withdrawn: DECIMAL(20,8)
- last_updated: TIMESTAMP
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### `withdrawals`
```sql
- id: UUID (Primary Key)
- amount: DECIMAL(20,8) NOT NULL
- status: ENUM(pending, processing, completed, failed, cancelled)
- withdrawal_address: TEXT NOT NULL
- transaction_hash: TEXT
- idempotency_key: TEXT UNIQUE NOT NULL
- admin_id: UUID NOT NULL (Foreign Key)
- biometric_verified: BOOLEAN DEFAULT FALSE
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- processed_at: TIMESTAMP
- notes: TEXT
```

#### `admin_audit_log`
```sql
- id: UUID (Primary Key)
- admin_id: UUID NOT NULL (Foreign Key)
- action: TEXT NOT NULL
- details: JSONB
- ip_address: INET
- user_agent: TEXT
- severity: ENUM(info, warning, critical)
- created_at: TIMESTAMP
```

### RLS Policies

#### Platform Finances Policy
```sql
CREATE POLICY "Admin only platform finances access" ON platform_finances
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');
```

#### Withdrawals Policy
```sql
CREATE POLICY "Admin only withdrawals access" ON withdrawals
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');
```

#### Audit Log Policy
```sql
CREATE POLICY "Admin only audit log access" ON admin_audit_log
  FOR ALL
  USING (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE')
  WITH CHECK (auth.uid() = 'YOUR_ADMIN_USER_ID_HERE');
```

## 🔧 Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Admin User ID (CRITICAL - MUST match Supabase auth.users.id)
NEXT_PUBLIC_ADMIN_USER_ID=your-actual-admin-user-id-here

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Edge Function Configuration
ADMIN_USER_ID=your-actual-admin-user-id-here
```

### Database Setup

1. **Run Migration:**
```bash
# Apply the platform finances migration
supabase db push
```

2. **Update Admin ID:**
```sql
-- Replace YOUR_ADMIN_USER_ID_HERE with actual admin UUID
-- in all RLS policies and functions
```

3. **Initialize Finances:**
```sql
-- The migration automatically creates an initial record
-- with zero balances if none exists
```

## 🚀 API Endpoints

### Create Withdrawal
```
POST /api/admin/withdrawal
Headers:
- Authorization: Bearer <jwt_token>
- X-Idempotency-Key: <unique_key>

Body:
{
  "amount": 1000.00,
  "withdrawal_address": "0x1234...",
  "idempotency_key": "withdrawal_123456"
}
```

### Complete Withdrawal (Biometric Verified)
```
POST /api/admin/withdrawal/[id]/complete
Headers:
- Authorization: Bearer <jwt_token>
```

### Cancel Withdrawal
```
POST /api/admin/withdrawal/[id]/cancel
Headers:
- Authorization: Bearer <jwt_token>
```

## 🔐 Security Features

### 1. Multi-Layer Authentication

#### Frontend Protection
- **Protected Route Component**: Automatic redirect for non-admin users
- **Real-time Admin Check**: Verifies admin status on every access
- **Security Event Logging**: Logs all unauthorized access attempts

#### Server-Side Verification
- **JWT Re-verification**: Validates token in Edge Function
- **Admin ID Check**: Compares user ID with admin ID
- **Critical Security Alerts**: Logs breach attempts with full context

#### Database Protection
- **Restrictive RLS**: Only admin can read/write financial data
- **Audit Trail**: Complete audit log of all financial operations
- **Idempotency Protection**: Prevents duplicate withdrawals

### 2. Biometric Authentication

#### WebAuthn Integration
- **FaceID/Fingerprint**: Required for withdrawal completion
- **Hardware Security**: Uses device secure hardware
- **Fallback Handling**: Cancels withdrawal if biometric fails

#### Implementation
```typescript
const biometricSuccess = await webauthnService.authenticate({
  challenge: new Uint8Array(32),
  allowCredentials: [],
  userVerification: 'required',
});
```

### 3. Idempotency Protection

#### Key Generation
```typescript
const idempotencyKey = `withdrawal_${Date.now()}_${Math.random().toString(36).substring(7)}`;
```

#### Duplicate Prevention
- **Database Constraint**: UNIQUE constraint on idempotency_key
- **API Check**: Verifies key doesn't exist before processing
- **Client-Side**: Generates unique key per request

### 4. Security Monitoring

#### Event Types Logged
- `CRITICAL_SECURITY_ALERT`: Non-admin access attempts
- `withdrawal_created`: New withdrawal requests
- `withdrawal_completed`: Successful withdrawals
- `withdrawal_cancelled`: Cancelled withdrawals
- `platform_finances_update`: Balance changes

#### Alert Context
```json
{
  "timestamp": "2026-03-30T11:48:00Z",
  "admin_id": "user-uuid",
  "action": "CRITICAL_SECURITY_ALERT",
  "details": {
    "reason": "Non-admin attempted withdrawal",
    "attempted_admin_id": "admin-uuid",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  },
  "severity": "critical"
}
```

## 🎯 Usage Guide

### Accessing Admin Wallet

1. **Navigate to Admin URL:**
```
https://your-domain.com/admin/wallet
```

2. **Authentication Check:**
   - System verifies user is authenticated
   - Checks if user ID matches admin ID
   - Redirects non-admin users to home page

3. **Dashboard View:**
   - Available balance (toggle visibility)
   - Total commissions and fees
   - Pending withdrawals
   - Recent withdrawal history

### Making a Withdrawal

1. **Enter Amount:**
   - Specify withdrawal amount
   - System validates sufficient balance
   - Shows available balance

2. **Enter Address:**
   - Provide withdrawal address
   - System validates address format

3. **Biometric Verification:**
   - Click "Withdraw with Biometric"
   - System prompts for FaceID/Fingerprint
   - Biometric authentication required

4. **Processing:**
   - Creates withdrawal record
   - Updates platform finances
   - Logs security event
   - Completes if biometric succeeds

### Security Best Practices

#### Admin Account Security
- **Strong Password**: Use unique, complex password
- **2FA Enabled**: Enable two-factor authentication
- **Secure Device**: Use trusted device for admin access
- **Regular Rotation**: Change password periodically

#### Withdrawal Security
- **Verify Address**: Double-check withdrawal addresses
- **Biometric Only**: Never disable biometric requirement
- **Monitor Activity**: Review withdrawal history regularly
- **Audit Logs**: Check security event logs

## 🚨 Incident Response

### Security Breach Detection

#### Immediate Actions
1. **Check Audit Logs**: Review `admin_audit_log` for suspicious activity
2. **Verify Admin Access**: Confirm only admin user has access
3. **Monitor Withdrawals**: Check for unauthorized withdrawal attempts
4. **Review IP Logs**: Identify unusual access patterns

#### Critical Alert Indicators
- Non-admin user ID in withdrawal attempts
- Multiple failed biometric verifications
- Unusual IP addresses or user agents
- Rapid withdrawal requests

### Response Procedures

#### Step 1: Containment
```sql
-- Disable admin access temporarily
UPDATE auth.users 
SET email_confirmed_at = NULL 
WHERE id = 'admin-user-id';
```

#### Step 2: Investigation
```sql
-- Review recent audit events
SELECT * FROM admin_audit_log 
WHERE severity = 'critical' 
AND created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

#### Step 3: Recovery
- Change admin password
- Revoke all active sessions
- Update admin user ID if compromised
- Enable additional security measures

## 📊 Monitoring & Alerting

### Key Metrics to Monitor

#### Security Metrics
- Failed admin access attempts
- Biometric verification failures
- Withdrawal request patterns
- IP address anomalies

#### Financial Metrics
- Withdrawal amounts and frequency
- Balance changes
- Pending withdrawal count
- Transaction processing times

#### System Metrics
- API response times
- Database connection health
- Edge Function performance
- Authentication success rates

### Alert Configuration

#### High Priority Alerts
- Non-admin withdrawal attempts
- Multiple biometric failures
- Large withdrawal amounts
- Unusual IP patterns

#### Medium Priority Alerts
- Failed authentication attempts
- Slow response times
- Database connection issues
- Edge Function errors

## 🧪 Testing

### Security Testing

#### Test Scenarios
```bash
# Test non-admin access
curl -X POST /api/admin/withdrawal \
  -H "Authorization: Bearer non-admin-token" \
  -d '{"amount": 100, "withdrawal_address": "0x1234"}'

# Test invalid JWT
curl -X POST /api/admin/withdrawal \
  -H "Authorization: Bearer invalid-token" \
  -d '{"amount": 100, "withdrawal_address": "0x1234"}'

# Test duplicate requests
curl -X POST /api/admin/withdrawal \
  -H "X-Idempotency-Key: same-key" \
  -d '{"amount": 100, "withdrawal_address": "0x1234"}'
```

#### Expected Responses
- **401**: Invalid authentication
- **403**: Access denied (non-admin)
- **409**: Duplicate request
- **400**: Invalid input

### Performance Testing

#### Load Testing
```bash
# Test withdrawal endpoint under load
k6 run --vus 10 --duration 30s withdrawal-test.js
```

#### Stress Testing
- Test with concurrent withdrawal requests
- Verify biometric authentication under load
- Monitor database performance during spikes

## 🔄 Maintenance

### Regular Tasks

#### Daily
- Review security event logs
- Monitor withdrawal activity
- Check system performance metrics

#### Weekly
- Audit admin access logs
- Review withdrawal patterns
- Update security policies

#### Monthly
- Rotate admin credentials
- Update biometric settings
- Review and update RLS policies

### Backup & Recovery

#### Database Backup
```bash
# Backup financial tables
pg_dump -h localhost -U postgres -d postgres \
  -t platform_finances \
  -t withdrawals \
  -t admin_audit_log \
  > financial_backup.sql
```

#### Recovery Procedures
1. Restore database from backup
2. Verify admin access
3. Test withdrawal functionality
4. Monitor system performance

## 📞 Support

### Emergency Contacts
- **Security Team**: security@worldmine.com
- **DevOps Team**: devops@worldmine.com
- **Database Admin**: dba@worldmine.com

### Documentation
- **API Documentation**: `/docs/api`
- **Security Policies**: `/docs/security`
- **Database Schema**: `/docs/database`

---

**Last Updated:** March 30, 2026  
**Version:** 1.0.0  
**Security Level:** HIGH  
**Classification:** CONFIDENTIAL
