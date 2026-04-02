import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { createHash } from 'https://deno.land/std@0.168.0/crypto/mod.ts'

// Types
interface WithdrawalRequest {
  userId: string
  amount: number
  currency: string
  address: string
  addressType: 'bank_account' | 'crypto_wallet'
  idempotencyKey: string
  deviceFingerprint: string
  biometricHash: string
  totpToken?: string
  ipAddress: string
  userAgent: string
  geolocation?: {
    country: string
    city: string
    coordinates: [number, number]
  }
}

interface SecurityCheckResult {
  passed: boolean
  reason?: string
  holdType?: 'new_device' | 'address_change' | 'limit_exceeded' | 'suspicious_activity'
  holdDuration?: number
  requiresSecondaryApproval?: boolean
}

interface WithdrawalResponse {
  success: boolean
  transactionId?: string
  error?: string
  securityHold?: {
    type: string
    holdUntil: string
    reason: string
  }
  requiresApproval?: {
    approvalUrl: string
    expiresAt: string
  }
}

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    // Parse request body
    const body: WithdrawalRequest = await req.json()
    
    // Validate required fields
    if (!body.userId || !body.amount || !body.address || !body.idempotencyKey) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Check idempotency
    const { data: existingWithdrawal } = await supabaseClient
      .from('withdrawals')
      .select('id')
      .eq('idempotency_key', body.idempotencyKey)
      .single()

    if (existingWithdrawal) {
      return new Response(
        JSON.stringify({ 
          success: true, 
          transactionId: existingWithdrawal.id,
          message: 'Withdrawal already processed'
        }),
        { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Perform multi-layer security checks
    const securityResult = await performSecurityChecks(supabaseClient, body)
    
    if (!securityResult.passed) {
      // Create security hold
      const holdUntil = new Date()
      holdUntil.setHours(holdUntil.getHours() + (securityResult.holdDuration || 24))
      
      await supabaseClient
        .from('security_holds')
        .insert({
          user_id: body.userId,
          reason: securityResult.holdType,
          amount: body.amount,
          currency: body.currency,
          address: body.address,
          device_fingerprint: body.deviceFingerprint,
          hold_until: holdUntil.toISOString(),
          is_active: true,
          created_at: new Date().toISOString(),
          ip_address: body.ipAddress,
          user_agent: body.userAgent,
          geolocation: body.geolocation
        })

      return new Response(
        JSON.stringify({
          success: false,
          error: securityResult.reason,
          securityHold: {
            type: securityResult.holdType!,
            holdUntil: holdUntil.toISOString(),
            reason: securityResult.reason!
          }
        }),
        { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Check if secondary approval is required
    if (securityResult.requiresSecondaryApproval) {
      const approvalUrl = await generateSecondaryApprovalUrl(supabaseClient, body)
      
      return new Response(
        JSON.stringify({
          success: false,
          requiresApproval: {
            approvalUrl,
            expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
          }
        }),
        { status: 202, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Process withdrawal with atomic transaction
    const result = await processWithdrawal(supabaseClient, body)
    
    return new Response(
      JSON.stringify(result),
      { status: result.success ? 200 : 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Error processing withdrawal:', error)
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

async function performSecurityChecks(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<SecurityCheckResult> {
  const checks: Promise<SecurityCheckResult>[] = [
    checkUserAuthentication(supabaseClient, request),
    checkTrustedDevice(supabaseClient, request),
    checkWhitelistedAddress(supabaseClient, request),
    checkVelocityLimits(supabaseClient, request),
    checkBiometricVerification(supabaseClient, request),
    checkTOTPVerification(supabaseClient, request),
    checkSuspiciousActivity(supabaseClient, request)
  ]

  const results = await Promise.all(checks)
  
  // Return first failed check, or success if all passed
  for (const result of results) {
    if (!result.passed) {
      return result
    }
  }
  
  return { passed: true }
}

async function checkUserAuthentication(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<SecurityCheckResult> {
  // Verify user is authenticated and active
  const { data: user, error } = await supabaseClient
    .from('user_profiles')
    .select('id, is_active, is_verified')
    .eq('id', request.userId)
    .single()

  if (error || !user) {
    return { passed: false, reason: 'User not found' }
  }

  if (!user.is_active) {
    return { passed: false, reason: 'User account is inactive' }
  }

  if (!user.is_verified) {
    return { passed: false, reason: 'User account is not verified' }
  }

  return { passed: true }
}

async function checkTrustedDevice(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<SecurityCheckResult> {
  // Check if device is trusted
  const { data: device, error } = await supabaseClient
    .from('trusted_devices')
    .select('*')
    .eq('user_id', request.userId)
    .eq('fingerprint', request.deviceFingerprint)
    .eq('is_active', true)
    .single()

  if (error || !device) {
    return { 
      passed: false, 
      reason: 'Device not trusted',
      holdType: 'new_device',
      holdDuration: 24
    }
  }

  // Check if device was registered more than 48 hours ago
  const registrationTime = new Date(device.first_seen)
  const now = new Date()
  const hoursSinceRegistration = (now.getTime() - registrationTime.getTime()) / (1000 * 60 * 60)

  if (hoursSinceRegistration < 48) {
    return { 
      passed: false, 
      reason: 'Device not registered for minimum 48 hours',
      holdType: 'new_device',
      holdDuration: 24
    }
  }

  return { passed: true }
}

async function checkWhitelistedAddress(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<SecurityCheckResult> {
  // Check if address is whitelisted
  const { data: address, error } = await supabaseClient
    .from('whitelisted_addresses')
    .select('*')
    .eq('user_id', request.userId)
    .eq('address', request.address)
    .eq('is_active', true)
    .single()

  if (error || !address) {
    return { 
      passed: false, 
      reason: 'Address not whitelisted',
      holdType: 'address_change',
      holdDuration: 48
    }
  }

  // Check if address is in cooldown period
  if (address.cooldown_until && new Date(address.cooldown_until) > new Date()) {
    return { 
      passed: false, 
      reason: 'Address is in cooldown period',
      holdType: 'address_change',
      holdDuration: 48
    }
  }

  return { passed: true }
}

async function checkVelocityLimits(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<SecurityCheckResult> {
  // Get user's security settings
  const { data: settings, error } = await supabaseClient
    .from('security_settings')
    .select('daily_withdrawal_limit, require_secondary_approval')
    .eq('user_id', request.userId)
    .single()

  if (error || !settings) {
    return { passed: false, reason: 'Security settings not found' }
  }

  // Calculate today's withdrawals
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const { data: todayWithdrawals } = await supabaseClient
    .from('withdrawals')
    .select('amount, currency')
    .eq('user_id', request.userId)
    .eq('status', 'completed')
    .gte('created_at', today.toISOString())

  const todayTotal = todayWithdrawals?.reduce((sum: number, w: any) => {
    return sum + (w.currency === request.currency ? w.amount : 0)
  }, 0) || 0

  // Check daily limit
  if (todayTotal + request.amount > settings.daily_withdrawal_limit) {
    return { 
      passed: false, 
      reason: `Daily withdrawal limit exceeded. Current: $${todayTotal}, Limit: $${settings.daily_withdrawal_limit}`,
      holdType: 'limit_exceeded',
      holdDuration: 24
    }
  }

  // Check if secondary approval is required
  const requiresApproval = settings.require_secondary_approval && 
    request.amount > (settings.daily_withdrawal_limit * 0.5)

  return { 
    passed: true, 
    requiresSecondaryApproval: requiresApproval 
  }
}

async function checkBiometricVerification(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<SecurityCheckResult> {
  // Verify biometric hash matches stored credential
  const { data: credential, error } = await supabaseClient
    .from('biometric_credentials')
    .select('public_key, created_at')
    .eq('user_id', request.userId)
    .eq('is_active', true)
    .order('created_at', { ascending: false })
    .limit(1)
    .single()

  if (error || !credential) {
    return { passed: false, reason: 'No biometric credentials found' }
  }

  // In a real implementation, you would verify the biometric hash
  // against the stored public key using cryptographic verification
  const isValidBiometric = await verifyBiometricHash(request.biometricHash, credential.public_key)
  
  if (!isValidBiometric) {
    return { passed: false, reason: 'Invalid biometric verification' }
  }

  return { passed: true }
}

async function checkTOTPVerification(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<SecurityCheckResult> {
  // Get user's security settings
  const { data: settings, error } = await supabaseClient
    .from('security_settings')
    .select('totp_enabled, require_totp')
    .eq('user_id', request.userId)
    .single()

  if (error || !settings) {
    return { passed: false, reason: 'Security settings not found' }
  }

  // Check if TOTP is required
  if (!settings.require_totp || !settings.totp_enabled) {
    return { passed: true }
  }

  // Verify TOTP token
  if (!request.totpToken) {
    return { passed: false, reason: 'TOTP token required' }
  }

  const isValidTOTP = await verifyTOTPToken(request.userId, request.totpToken)
  
  if (!isValidTOTP) {
    return { passed: false, reason: 'Invalid TOTP token' }
  }

  return { passed: true }
}

async function checkSuspiciousActivity(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<SecurityCheckResult> {
  // Check for suspicious patterns
  const checks = [
    checkRapidWithdrawals(supabaseClient, request),
    checkUnusualLocation(supabaseClient, request),
    checkUnusualAmount(supabaseClient, request),
    checkFailedAttempts(supabaseClient, request)
  ]

  const results = await Promise.all(checks)
  
  for (const result of results) {
    if (!result.passed) {
      return result
    }
  }
  
  return { passed: true }
}

async function checkRapidWithdrawals(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<SecurityCheckResult> {
  // Check for multiple withdrawals in short time
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000)
  
  const { data: recentWithdrawals } = await supabaseClient
    .from('withdrawals')
    .select('id')
    .eq('user_id', request.userId)
    .gte('created_at', oneHourAgo.toISOString())

  if (recentWithdrawals && recentWithdrawals.length >= 5) {
    return { 
      passed: false, 
      reason: 'Too many withdrawal attempts in short time',
      holdType: 'suspicious_activity',
      holdDuration: 72
    }
  }

  return { passed: true }
}

async function checkUnusualLocation(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<SecurityCheckResult> {
  if (!request.geolocation) {
    return { passed: true }
  }

  // Check recent withdrawal locations
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  
  const { data: recentLocations } = await supabaseClient
    .from('withdrawals')
    .select('geolocation')
    .eq('user_id', request.userId)
    .gte('created_at', sevenDaysAgo.toISOString())

  if (recentLocations && recentLocations.length > 0) {
    // Check if current location is significantly different from usual locations
    const usualCountries = recentLocations
      .map((w: any) => w.geolocation?.country)
      .filter(Boolean)

    if (usualCountries.length > 0 && !usualCountries.includes(request.geolocation.country)) {
      return { 
        passed: false, 
        reason: 'Unusual withdrawal location detected',
        holdType: 'suspicious_activity',
        holdDuration: 48
      }
    }
  }

  return { passed: true }
}

async function checkUnusualAmount(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<SecurityCheckResult> {
  // Check if amount is significantly higher than usual
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
  
  const { data: historicalWithdrawals } = await supabaseClient
    .from('withdrawals')
    .select('amount, currency')
    .eq('user_id', request.userId)
    .eq('status', 'completed')
    .gte('created_at', thirtyDaysAgo.toISOString())

  if (historicalWithdrawals && historicalWithdrawals.length > 0) {
    const sameCurrencyWithdrawals = historicalWithdrawals
      .filter((w: any) => w.currency === request.currency)
      .map((w: any) => w.amount)

    if (sameCurrencyWithdrawals.length > 0) {
      const average = sameCurrencyWithdrawals.reduce((sum: number, amount: number) => sum + amount, 0) / sameCurrencyWithdrawals.length
      const standardDeviation = Math.sqrt(
        sameCurrencyWithdrawals.reduce((sum: number, amount: number) => {
          return sum + Math.pow(amount - average, 2)
        }, 0) / sameCurrencyWithdrawals.length
      )

      // Flag if amount is more than 3 standard deviations from average
      if (request.amount > average + (3 * standardDeviation)) {
        return { 
          passed: false, 
          reason: 'Unusual withdrawal amount detected',
          holdType: 'suspicious_activity',
          holdDuration: 24
        }
      }
    }
  }

  return { passed: true }
}

async function checkFailedAttempts(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<SecurityCheckResult> {
  // Check recent failed withdrawal attempts
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000)
  
  const { data: failedAttempts } = await supabaseClient
    .from('withdrawal_attempts')
    .select('id')
    .eq('user_id', request.userId)
    .eq('status', 'failed')
    .gte('created_at', oneHourAgo.toISOString())

  if (failedAttempts && failedAttempts.length >= 3) {
    return { 
      passed: false, 
      reason: 'Too many failed withdrawal attempts',
      holdType: 'suspicious_activity',
      holdDuration: 24
    }
  }

  return { passed: true }
}

async function verifyBiometricHash(hash: string, publicKey: string): Promise<boolean> {
  // In a real implementation, you would use cryptographic verification
  // This is a simplified placeholder
  try {
    // Verify the hash against the stored public key
    const encoder = new TextEncoder()
    const data = encoder.encode(hash)
    const keyData = encoder.encode(publicKey)
    
    // Use Web Crypto API for verification
    const key = await crypto.subtle.importKey(
      'raw',
      keyData,
      { name: 'ECDSA', namedCurve: 'P-256' },
      false,
      ['verify']
    )
    
    const signature = new Uint8Array(64) // Placeholder signature
    
    const isValid = await crypto.subtle.verify(
      { name: 'ECDSA', hash: 'SHA-256' },
      key,
      signature,
      data
    )
    
    return isValid
  } catch (error) {
    console.error('Biometric verification error:', error)
    return false
  }
}

async function verifyTOTPToken(userId: string, token: string): Promise<boolean> {
  // In a real implementation, you would use a TOTP library
  // This is a simplified placeholder
  try {
    // Get user's TOTP secret
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )
    
    const { data: totpData } = await supabase
      .from('totp_secrets')
      .select('secret')
      .eq('user_id', userId)
      .single()

    if (!totpData) {
      return false
    }

    // Verify TOTP token (simplified)
    const isValid = token.length === 6 && /^\d{6}$/.test(token)
    
    // Log TOTP verification attempt
    await supabase
      .from('totp_verification_logs')
      .insert({
        user_id: userId,
        token: token,
        is_valid: isValid,
        created_at: new Date().toISOString()
      })
    
    return isValid
  } catch (error) {
    console.error('TOTP verification error:', error)
    return false
  }
}

async function generateSecondaryApprovalUrl(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<string> {
  // Generate secure approval URL
  const approvalId = crypto.randomUUID()
  const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000)
  
  // Store approval request
  await supabaseClient
    .from('secondary_approvals')
    .insert({
      id: approvalId,
      user_id: request.userId,
      amount: request.amount,
      currency: request.currency,
      address: request.address,
      address_type: request.addressType,
      expires_at: expiresAt.toISOString(),
      is_approved: false,
      created_at: new Date().toISOString(),
      device_fingerprint: request.deviceFingerprint,
      ip_address: request.ipAddress,
      user_agent: request.userAgent
    })

  // Generate approval URL
  const baseUrl = Deno.env.get('APP_URL') || 'https://worldmine.vercel.app'
  return `${baseUrl}/approve-withdrawal/${approvalId}`
}

async function processWithdrawal(
  supabaseClient: any,
  request: WithdrawalRequest
): Promise<WithdrawalResponse> {
  // Use database transaction for atomic operation
  const transactionId = crypto.randomUUID()
  
  try {
    // Start transaction
    const { data: transactionResult, error } = await supabaseClient.rpc('process_withdrawal_transaction', {
      p_user_id: request.userId,
      p_amount: request.amount,
      p_currency: request.currency,
      p_address: request.address,
      p_address_type: request.addressType,
      p_transaction_id: transactionId,
      p_idempotency_key: request.idempotencyKey,
      p_device_fingerprint: request.deviceFingerprint,
      p_ip_address: request.ipAddress,
      p_user_agent: request.userAgent,
      p_geolocation: request.geolocation
    })

    if (error) {
      throw error
    }

    // Log successful withdrawal
    await supabaseClient
      .from('withdrawal_audit_log')
      .insert({
        transaction_id: transactionId,
        user_id: request.userId,
        amount: request.amount,
        currency: request.currency,
        address: request.address,
        address_type: request.addressType,
        status: 'completed',
        created_at: new Date().toISOString(),
        device_fingerprint: request.deviceFingerprint,
        ip_address: request.ipAddress,
        user_agent: request.userAgent,
        geolocation: request.geolocation,
        security_checks_passed: true
      })

    return {
      success: true,
      transactionId
    }
  } catch (error) {
    console.error('Withdrawal processing error:', error)
    
    // Log failed withdrawal
    await supabaseClient
      .from('withdrawal_audit_log')
      .insert({
        transaction_id: transactionId,
        user_id: request.userId,
        amount: request.amount,
        currency: request.currency,
        address: request.address,
        address_type: request.addressType,
        status: 'failed',
        error_message: error.message,
        created_at: new Date().toISOString(),
        device_fingerprint: request.deviceFingerprint,
        ip_address: request.ipAddress,
        user_agent: request.userAgent,
        geolocation: request.geolocation
      })

    return {
      success: false,
      error: 'Withdrawal processing failed'
    }
  }
}
