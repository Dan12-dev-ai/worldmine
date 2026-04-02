import React, { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

// Types
interface SecurityHold {
  id: string;
  userId: string;
  reason: 'new_device' | 'address_change' | 'limit_exceeded' | 'suspicious_activity';
  amount?: number;
  currency?: string;
  address?: string;
  deviceId?: string;
  holdUntil: string;
  isActive: boolean;
  createdAt: string;
  resolvedAt?: string;
  resolvedBy?: string;
  notes?: string;
  userProfile?: {
    email: string;
    fullName: string;
  };
}

interface SecurityMetrics {
  totalHolds: number;
  activeHolds: number;
  resolvedHolds: number;
  holdsByReason: Record<string, number>;
  averageHoldDuration: number;
  suspiciousActivityCount: number;
  newDeviceCount: number;
  addressChangeCount: number;
  limitExceededCount: number;
}

interface SuspiciousActivity {
  id: string;
  userId: string;
  type: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  ipAddress: string;
  userAgent: string;
  geolocation?: {
    country: string;
    city: string;
  };
  createdAt: string;
  isInvestigated: boolean;
  investigatedBy?: string;
  investigatedAt?: string;
  investigationNotes?: string;
  userProfile?: {
    email: string;
    fullName: string;
  };
}

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export const SecurityDashboard: React.FC = () => {
  const [securityHolds, setSecurityHolds] = useState<SecurityHold[]>([]);
  const [suspiciousActivities, setSuspiciousActivities] = useState<SuspiciousActivity[]>([]);
  const [metrics, setMetrics] = useState<SecurityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'holds' | 'activity' | 'metrics'>('holds');
  const [selectedHold, setSelectedHold] = useState<SecurityHold | null>(null);
  const [selectedActivity, setSelectedActivity] = useState<SuspiciousActivity | null>(null);
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [showInvestigateModal, setShowInvestigateModal] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [investigationNotes, setInvestigationNotes] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'resolved'>('active');
  const [filterReason, setFilterReason] = useState<string>('all');

  useEffect(() => {
    loadSecurityData();
    
    // Set up real-time subscription
    const subscription = supabase
      .channel('security-updates')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'security_holds' },
        () => {
          loadSecurityData();
        }
      )
      .subscribe();

    return () => {
      subscription.unsubscribe();
    };
  }, [filterStatus, filterReason]);

  const loadSecurityData = async () => {
    try {
      setLoading(true);

      // Load security holds
      let holdsQuery = supabase
        .from('security_holds')
        .select(`
          *,
          user_profiles!inner(
            email,
            full_name
          )
        `)
        .order('created_at', { ascending: false });

      // Apply filters
      if (filterStatus !== 'all') {
        holdsQuery = holdsQuery.eq('is_active', filterStatus === 'active');
      }
      if (filterReason !== 'all') {
        holdsQuery = holdsQuery.eq('reason', filterReason);
      }

      const { data: holdsData } = await holdsQuery;
      setSecurityHolds(holdsData || []);

      // Load suspicious activities
      const { data: activitiesData } = await supabase
        .from('suspicious_activities')
        .select(`
          *,
          user_profiles!inner(
            email,
            full_name
          )
        `)
        .eq('is_investigated', false)
        .order('created_at', { ascending: false })
        .limit(50);

      setSuspiciousActivities(activitiesData || []);

      // Calculate metrics
      const metricsData = await calculateMetrics(holdsData || []);
      setMetrics(metricsData);

    } catch (error) {
      console.error('Error loading security data:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateMetrics = async (holds: SecurityHold[]): Promise<SecurityMetrics> => {
    const totalHolds = holds.length;
    const activeHolds = holds.filter(h => h.isActive).length;
    const resolvedHolds = holds.filter(h => !h.isActive).length;

    const holdsByReason = holds.reduce((acc, hold) => {
      acc[hold.reason] = (acc[hold.reason] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const averageHoldDuration = resolvedHolds > 0
      ? holds
          .filter(h => !h.isActive && h.resolvedAt)
          .reduce((sum, hold) => {
            const duration = new Date(hold.resolvedAt!).getTime() - new Date(hold.createdAt).getTime();
            return sum + duration;
          }, 0) / resolvedHolds / (1000 * 60 * 60) // Convert to hours
      : 0;

    return {
      totalHolds,
      activeHolds,
      resolvedHolds,
      holdsByReason,
      averageHoldDuration,
      suspiciousActivityCount: holdsByReason.suspicious_activity || 0,
      newDeviceCount: holdsByReason.new_device || 0,
      addressChangeCount: holdsByReason.address_change || 0,
      limitExceededCount: holdsByReason.limit_exceeded || 0
    };
  };

  const resolveSecurityHold = async () => {
    if (!selectedHold || !resolutionNotes.trim()) return;

    try {
      const user = await supabase.auth.getUser();
      if (!user.data.user) return;

      const { error } = await supabase
        .from('security_holds')
        .update({
          is_active: false,
          resolved_at: new Date().toISOString(),
          resolved_by: user.data.user.id,
          notes: resolutionNotes
        })
        .eq('id', selectedHold.id);

      if (error) throw error;

      // Log resolution
      await supabase
        .from('security_admin_actions')
        .insert({
          action_type: 'resolve_hold',
          target_id: selectedHold.id,
          notes: resolutionNotes,
          admin_id: user.data.user.id,
          created_at: new Date().toISOString()
        });

      setShowResolveModal(false);
      setSelectedHold(null);
      setResolutionNotes('');
      loadSecurityData();
    } catch (error) {
      console.error('Error resolving security hold:', error);
    }
  };

  const investigateSuspiciousActivity = async () => {
    if (!selectedActivity || !investigationNotes.trim()) return;

    try {
      const user = await supabase.auth.getUser();
      if (!user.data.user) return;

      const { error } = await supabase
        .from('suspicious_activities')
        .update({
          is_investigated: true,
          investigated_at: new Date().toISOString(),
          investigated_by: user.data.user.id,
          investigation_notes: investigationNotes
        })
        .eq('id', selectedActivity.id);

      if (error) throw error;

      // Log investigation
      await supabase
        .from('security_admin_actions')
        .insert({
          action_type: 'investigate_activity',
          target_id: selectedActivity.id,
          notes: investigationNotes,
          admin_id: user.data.user.id,
          created_at: new Date().toISOString()
        });

      setShowInvestigateModal(false);
      setSelectedActivity(null);
      setInvestigationNotes('');
      loadSecurityData();
    } catch (error) {
      console.error('Error investigating suspicious activity:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getReasonColor = (reason: string) => {
    switch (reason) {
      case 'suspicious_activity': return 'text-red-600 bg-red-100';
      case 'new_device': return 'text-blue-600 bg-blue-100';
      case 'address_change': return 'text-orange-600 bg-orange-100';
      case 'limit_exceeded': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading security dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">Security Dashboard</h1>
            <p className="text-gray-600 mt-1">Monitor and manage security holds and suspicious activities</p>
          </div>

          {/* Metrics Cards */}
          {metrics && (
            <div className="p-6 border-b border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white p-6 rounded-lg border border-gray-200">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-blue-100 rounded-lg p-3">
                      <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Active Holds</p>
                      <p className="text-2xl font-semibold text-gray-900">{metrics.activeHolds}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-lg border border-gray-200">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-red-100 rounded-lg p-3">
                      <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Suspicious Activity</p>
                      <p className="text-2xl font-semibold text-gray-900">{metrics.suspiciousActivityCount}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-lg border border-gray-200">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-green-100 rounded-lg p-3">
                      <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Resolved Today</p>
                      <p className="text-2xl font-semibold text-gray-900">{metrics.resolvedHolds}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-lg border border-gray-200">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-purple-100 rounded-lg p-3">
                      <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Avg Hold Duration</p>
                      <p className="text-2xl font-semibold text-gray-900">{metrics.averageHoldDuration.toFixed(1)}h</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('holds')}
                className={`py-4 px-6 text-sm font-medium border-b-2 ${
                  activeTab === 'holds'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Security Holds ({securityHolds.filter(h => h.isActive).length})
              </button>
              <button
                onClick={() => setActiveTab('activity')}
                className={`py-4 px-6 text-sm font-medium border-b-2 ${
                  activeTab === 'activity'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Suspicious Activity ({suspiciousActivities.length})
              </button>
              <button
                onClick={() => setActiveTab('metrics')}
                className={`py-4 px-6 text-sm font-medium border-b-2 ${
                  activeTab === 'metrics'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Metrics
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Security Holds Tab */}
            {activeTab === 'holds' && (
              <div>
                {/* Filters */}
                <div className="flex flex-col sm:flex-row gap-4 mb-6">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                    <select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value as any)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="all">All</option>
                      <option value="active">Active</option>
                      <option value="resolved">Resolved</option>
                    </select>
                  </div>
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Reason</label>
                    <select
                      value={filterReason}
                      onChange={(e) => setFilterReason(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="all">All Reasons</option>
                      <option value="new_device">New Device</option>
                      <option value="address_change">Address Change</option>
                      <option value="limit_exceeded">Limit Exceeded</option>
                      <option value="suspicious_activity">Suspicious Activity</option>
                    </select>
                  </div>
                </div>

                {/* Holds List */}
                <div className="space-y-4">
                  {securityHolds.map((hold) => (
                    <div key={hold.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getReasonColor(hold.reason)}`}>
                              {hold.reason.replace('_', ' ').toUpperCase()}
                            </span>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              hold.isActive ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                            }`}>
                              {hold.isActive ? 'Active' : 'Resolved'}
                            </span>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                            <div>
                              <p className="text-gray-600">User: {hold.userProfile?.fullName} ({hold.userProfile?.email})</p>
                              <p className="text-gray-600">Created: {new Date(hold.createdAt).toLocaleString()}</p>
                              {hold.amount && (
                                <p className="text-gray-600">Amount: ${hold.amount} {hold.currency}</p>
                              )}
                              {hold.address && (
                                <p className="text-gray-600">Address: {hold.address}</p>
                              )}
                            </div>
                            <div>
                              <p className="text-gray-600">Hold Until: {new Date(hold.holdUntil).toLocaleString()}</p>
                              {hold.resolvedAt && (
                                <p className="text-gray-600">Resolved: {new Date(hold.resolvedAt).toLocaleString()}</p>
                              )}
                              {hold.notes && (
                                <p className="text-gray-600">Notes: {hold.notes}</p>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex space-x-2">
                          {hold.isActive && (
                            <button
                              onClick={() => {
                                setSelectedHold(hold);
                                setShowResolveModal(true);
                              }}
                              className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                            >
                              Resolve
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Suspicious Activity Tab */}
            {activeTab === 'activity' && (
              <div>
                <div className="space-y-4">
                  {suspiciousActivities.map((activity) => (
                    <div key={activity.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(activity.severity)}`}>
                              {activity.severity.toUpperCase()}
                            </span>
                            <span className="text-sm text-gray-600">
                              {new Date(activity.createdAt).toLocaleString()}
                            </span>
                          </div>
                          
                          <div className="mb-2">
                            <p className="font-medium text-gray-900">{activity.description}</p>
                            <p className="text-sm text-gray-600 mt-1">
                              User: {activity.userProfile?.fullName} ({activity.userProfile?.email})
                            </p>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                            <p>IP: {activity.ipAddress}</p>
                            <p>Location: {activity.geolocation?.city}, {activity.geolocation?.country}</p>
                            <p>Type: {activity.type}</p>
                          </div>
                        </div>
                        
                        <div className="flex space-x-2">
                          <button
                            onClick={() => {
                              setSelectedActivity(activity);
                              setShowInvestigateModal(true);
                            }}
                            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                          >
                            Investigate
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Metrics Tab */}
            {activeTab === 'metrics' && metrics && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Security Metrics</h3>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Holds by Reason */}
                  <div className="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 className="text-md font-medium text-gray-900 mb-4">Holds by Reason</h4>
                    <div className="space-y-3">
                      {Object.entries(metrics.holdsByReason).map(([reason, count]) => (
                        <div key={reason} className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">{reason.replace('_', ' ').toUpperCase()}</span>
                          <span className="text-sm font-medium text-gray-900">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recent Activity Summary */}
                  <div className="bg-white p-6 rounded-lg border border-gray-200">
                    <h4 className="text-md font-medium text-gray-900 mb-4">Activity Summary</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">New Devices</span>
                        <span className="text-sm font-medium text-gray-900">{metrics.newDeviceCount}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Address Changes</span>
                        <span className="text-sm font-medium text-gray-900">{metrics.addressChangeCount}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Limit Exceeded</span>
                        <span className="text-sm font-medium text-gray-900">{metrics.limitExceededCount}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Suspicious Activity</span>
                        <span className="text-sm font-medium text-gray-900">{metrics.suspiciousActivityCount}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Resolve Hold Modal */}
      {showResolveModal && selectedHold && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Resolve Security Hold</h3>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                Hold: {selectedHold.reason.replace('_', ' ').toUpperCase()}
              </p>
              <p className="text-sm text-gray-600 mb-2">
                User: {selectedHold.userProfile?.fullName}
              </p>
              {selectedHold.amount && (
                <p className="text-sm text-gray-600 mb-2">
                  Amount: ${selectedHold.amount} {selectedHold.currency}
                </p>
              )}
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Resolution Notes</label>
              <textarea
                value={resolutionNotes}
                onChange={(e) => setResolutionNotes(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter resolution notes..."
                required
              />
            </div>

            <div className="flex space-x-3">
              <button
                onClick={resolveSecurityHold}
                className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
              >
                Resolve Hold
              </button>
              <button
                onClick={() => {
                  setShowResolveModal(false);
                  setSelectedHold(null);
                  setResolutionNotes('');
                }}
                className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Investigate Activity Modal */}
      {showInvestigateModal && selectedActivity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Investigate Suspicious Activity</h3>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                Activity: {selectedActivity.description}
              </p>
              <p className="text-sm text-gray-600 mb-2">
                User: {selectedActivity.userProfile?.fullName}
              </p>
              <p className="text-sm text-gray-600 mb-2">
                Severity: {selectedActivity.severity.toUpperCase()}
              </p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Investigation Notes</label>
              <textarea
                value={investigationNotes}
                onChange={(e) => setInvestigationNotes(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter investigation notes..."
                required
              />
            </div>

            <div className="flex space-x-3">
              <button
                onClick={investigateSuspiciousActivity}
                className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
              >
                Mark Investigated
              </button>
              <button
                onClick={() => {
                  setShowInvestigateModal(false);
                  setSelectedActivity(null);
                  setInvestigationNotes('');
                }}
                className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SecurityDashboard;
