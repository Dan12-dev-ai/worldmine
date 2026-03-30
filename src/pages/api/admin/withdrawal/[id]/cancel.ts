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

    // Get withdrawal details before cancellation
    const { data: withdrawal, error: fetchError } = await supabase
      .from('withdrawals')
      .select('amount, status')
      .eq('id', id)
      .eq('admin_id', user.id)
      .single();

    if (fetchError || !withdrawal) {
      return res.status(404).json({ error: 'Withdrawal not found' });
    }

    // Only allow cancellation of pending withdrawals
    if (withdrawal.status !== 'pending') {
      return res.status(400).json({ error: 'Can only cancel pending withdrawals' });
    }

    // Update withdrawal status to cancelled
    const { error: updateError } = await supabase
      .from('withdrawals')
      .update({
        status: 'cancelled',
        processed_at: new Date().toISOString()
      })
      .eq('id', id)
      .eq('admin_id', user.id);

    if (updateError) {
      console.error('Cancel withdrawal error:', updateError);
      return res.status(500).json({ error: 'Failed to cancel withdrawal' });
    }

    // Restore funds to platform finances
    const { error: financeError } = await supabase.rpc('update_platform_finances', {
      p_amount: withdrawal.amount,
      p_type: 'withdrawal_failed',
      p_admin_id: user.id
    });

    if (financeError) {
      console.error('Restore finances error:', financeError);
    }

    // Log the cancellation
    await supabase
      .from('admin_audit_log')
      .insert({
        admin_id: user.id,
        action: 'withdrawal_cancelled',
        details: { withdrawal_id: id, amount: withdrawal.amount },
        severity: 'info'
      });

    res.status(200).json({ success: true, message: 'Withdrawal cancelled successfully' });

  } catch (error) {
    console.error('Cancel withdrawal error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
