import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { createHash } from 'https://deno.land/std@0.168.0/crypto/mod.ts'

// Configuration
const ADMIN_USER_ID = Deno.env.get('ADMIN_USER_ID') || 'YOUR_ADMIN_USER_ID_HERE'
const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const SUPABASE_SERVICE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

// Security headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-idempotency-key',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Max-Age': '86400',
}

// Types
interface WithdrawalRequest {
  amount: number
  withdrawal_address: string
  idempotency_key: string
}

interface WithdrawalResponse {
  success: boolean
  withdrawal_id?: string
  message: string
  error?: string
}

// Helper functions
function logSecurityEvent(
  adminId: string,
  action: string,
  details: any,
  severity: 'info' | 'warning' | 'critical' = 'info',
  ipAddress?: string,
  userAgent?: string
) {
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    admin_id: adminId,
    action,
    details,
    severity,
    ip_address: ipAddress,
    user_agent: userAgent,
    type: 'SECURITY_AUDIT'
  }))
}

async function verifyJWT(token: string): Promise<{ userId: string; isValid: boolean }> {
  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    const { data: { user }, error } = await supabase.auth.getUser(token)
    
    if (error || !user) {
      return { userId: '', isValid: false }
    }
    
    return { userId: user.id, isValid: true }
  } catch (error) {
    console.error('JWT verification error:', error)
    return { userId: '', isValid: false }
  }
}

async function checkIdempotency(idempotencyKey: string): Promise<boolean> {
  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    const { data, error } = await supabase
      .from('withdrawals')
      .select('id')
      .eq('idempotency_key', idempotencyKey)
      .single()
    
    return !error && data !== null
  } catch (error) {
    console.error('Idempotency check error:', error)
    return false
  }
}

async function createWithdrawal(
  supabase: any,
  adminId: string,
  request: WithdrawalRequest
): Promise<{ success: boolean; withdrawalId?: string; error?: string }> {
  try {
    // Check if sufficient balance is available
    const { data: finances, error: financesError } = await supabase
      .from('platform_finances')
      .select('available_balance')
      .single()
    
    if (financesError || !finances) {
      throw new Error('Failed to fetch platform finances')
    }
    
    if (finances.available_balance < request.amount) {
      return { success: false, error: 'Insufficient balance' }
    }
    
    // Create withdrawal record
    const { data: withdrawal, error: withdrawalError } = await supabase
      .from('withdrawals')
      .insert({
        amount: request.amount,
        status: 'pending',
        withdrawal_address: request.withdrawal_address,
        idempotency_key: request.idempotency_key,
        admin_id: adminId,
        biometric_verified: false
      })
      .select()
      .single()
    
    if (withdrawalError || !withdrawal) {
      throw new Error('Failed to create withdrawal')
    }
    
    // Update platform finances
    const { error: updateError } = await supabase.rpc('update_platform_finances', {
      p_amount: request.amount,
      p_type: 'withdrawal_initiated',
      p_admin_id: adminId
    })
    
    if (updateError) {
      throw new Error('Failed to update platform finances')
    }
    
    return { success: true, withdrawalId: withdrawal.id }
  } catch (error) {
    console.error('Create withdrawal error:', error)
    return { success: false, error: error instanceof Error ? error.message : 'Unknown error' }
  }
}

// Main handler
serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  // Only allow POST requests
  if (req.method !== 'POST') {
    return new Response(
      JSON.stringify({ error: 'Method not allowed' }),
      { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }

  try {
    // Get request details
    const ipAddress = req.headers.get('x-forwarded-for') || 
                     req.headers.get('x-real-ip') || 
                     'unknown'
    const userAgent = req.headers.get('user-agent') || 'unknown'
    const idempotencyKey = req.headers.get('x-idempotency-key')

    if (!idempotencyKey) {
      return new Response(
        JSON.stringify({ error: 'Idempotency key required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Verify JWT token
    const authHeader = req.headers.get('authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      logSecurityEvent('unknown', 'UNAUTHORIZED_ACCESS', { reason: 'No auth token' }, 'critical', ipAddress, userAgent)
      return new Response(
        JSON.stringify({ error: 'Authorization required' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    const token = authHeader.substring(7)
    const { userId, isValid } = await verifyJWT(token)

    if (!isValid) {
      logSecurityEvent(userId, 'INVALID_JWT', { reason: 'JWT verification failed' }, 'critical', ipAddress, userAgent)
      return new Response(
        JSON.stringify({ error: 'Invalid authentication' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // CRITICAL SECURITY CHECK: Verify user is the admin
    if (userId !== ADMIN_USER_ID) {
      logSecurityEvent(userId, 'CRITICAL_SECURITY_ALERT', { 
        reason: 'Non-admin attempted withdrawal',
        attempted_admin_id: ADMIN_USER_ID,
        ip_address: ipAddress,
        user_agent: userAgent
      }, 'critical', ipAddress, userAgent)
      
      return new Response(
        JSON.stringify({ error: 'Access denied' }),
        { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Parse request body
    const body: WithdrawalRequest = await req.json()
    
    // Validate request
    if (!body.amount || body.amount <= 0) {
      return new Response(
        JSON.stringify({ error: 'Invalid amount' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    if (!body.withdrawal_address || body.withdrawal_address.trim() === '') {
      return new Response(
        JSON.stringify({ error: 'Withdrawal address required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Check idempotency
    const idempotencyExists = await checkIdempotency(idempotencyKey)
    if (idempotencyExists) {
      return new Response(
        JSON.stringify({ error: 'Duplicate request detected' }),
        { status: 409, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Create withdrawal
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    const result = await createWithdrawal(supabase, userId, {
      amount: body.amount,
      withdrawal_address: body.withdrawal_address,
      idempotency_key: idempotencyKey
    })

    if (!result.success) {
      logSecurityEvent(userId, 'WITHDRAWAL_FAILED', { 
        amount: body.amount,
        error: result.error,
        withdrawal_address: body.withdrawal_address
      }, 'warning', ipAddress, userAgent)
      
      return new Response(
        JSON.stringify({ error: result.error || 'Withdrawal failed' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Log successful withdrawal creation
    logSecurityEvent(userId, 'WITHDRAWAL_CREATED', {
      withdrawal_id: result.withdrawalId,
      amount: body.amount,
      withdrawal_address: body.withdrawal_address,
      idempotency_key: idempotencyKey
    }, 'info', ipAddress, userAgent)

    const response: WithdrawalResponse = {
      success: true,
      withdrawal_id: result.withdrawalId,
      message: 'Withdrawal created successfully. Awaiting biometric verification.'
    }

    return new Response(
      JSON.stringify(response),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )

  } catch (error) {
    console.error('Withdrawal handler error:', error)
    
    const response: WithdrawalResponse = {
      success: false,
      message: 'Internal server error',
      error: error instanceof Error ? error.message : 'Unknown error'
    }

    return new Response(
      JSON.stringify(response),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
})
