import { NextApiRequest, NextApiResponse } from '../../../../../types/next';
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
    // Verify user is authenticated and is admin
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

    if (user.id !== adminUserId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    const { id } = req.query;
    if (!id || typeof id !== 'string') {
      return res.status(400).json({ error: 'Withdrawal ID required' });
    }

    // Update withdrawal status to completed and mark as biometric verified
    const { error: updateError } = await supabase
      .from('withdrawals')
      .update({
        status: 'completed',
        biometric_verified: true,
        processed_at: new Date().toISOString()
      })
      .eq('id', id)
      .eq('admin_id', user.id);

    if (updateError) {
      console.error('Complete withdrawal error:', updateError);
      return res.status(500).json({ error: 'Failed to complete withdrawal' });
    }

    // Update platform finances
    const { error: financeError } = await supabase.rpc('update_platform_finances', {
      p_amount: (await supabase.from('withdrawals').select('amount').eq('id', id).single()).data?.amount || 0,
      p_type: 'withdrawal_completed',
      p_admin_id: user.id
    });

    if (financeError) {
      console.error('Update finances error:', financeError);
    }

    // Log the completion
    await supabase
      .from('admin_audit_log')
      .insert({
        admin_id: user.id,
        action: 'withdrawal_completed',
        details: { withdrawal_id: id },
        severity: 'info'
      });

    res.status(200).json({ success: true, message: 'Withdrawal completed successfully' });

  } catch (error) {
    console.error('Complete withdrawal error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
