import { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const adminUserId = process.env.NEXT_PUBLIC_ADMIN_USER_ID || 'YOUR_ADMIN_USER_ID_HERE';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Verify user is authenticated
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Authorization required' });
    }

    const token = authHeader.substring(7);
    const supabase = createClient(supabaseUrl, supabaseServiceKey);
    
    const { data: { user }, error: authError } = await supabase.auth.getUser(token);
    
    if (authError || !user) {
      return res.status(401).json({ error: 'Invalid authentication' });
    }

    // CRITICAL SECURITY CHECK: Verify user is the admin
    if (user.id !== adminUserId) {
      // Log security breach attempt
      console.error('CRITICAL_SECURITY_ALERT', {
        timestamp: new Date().toISOString(),
        user_id: user.id,
        attempted_action: 'admin_withdrawal',
        ip_address: req.headers['x-forwarded-for'] || req.headers['x-real-ip'],
        user_agent: req.headers['user-agent']
      });
      
      return res.status(403).json({ error: 'Access denied' });
    }

    // Parse request body
    const { amount, withdrawal_address, idempotency_key } = req.body;

    if (!amount || amount <= 0) {
      return res.status(400).json({ error: 'Invalid amount' });
    }

    if (!withdrawal_address || withdrawal_address.trim() === '') {
      return res.status(400).json({ error: 'Withdrawal address required' });
    }

    if (!idempotency_key) {
      return res.status(400).json({ error: 'Idempotency key required' });
    }

    // Forward to Supabase Edge Function
    const edgeFunctionUrl = `${supabaseUrl}/functions/v1/handle-admin-withdrawal`;
    
    const response = await fetch(edgeFunctionUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Idempotency-Key': idempotency_key,
      },
      body: JSON.stringify({
        amount,
        withdrawal_address,
        idempotency_key,
      }),
    });

    const result = await response.json();

    if (!response.ok) {
      return res.status(response.status).json(result);
    }

    res.status(200).json(result);

  } catch (error) {
    console.error('Admin withdrawal error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
