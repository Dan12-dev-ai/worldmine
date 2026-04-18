import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Box, Grid, Chip, LinearProgress, Alert, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

const TransparencyPortal = () => {
  const [reserves, setReserves] = useState([]);
  const [quantumSecurity, setQuantumSecurity] = useState({});
  const [auditLogs, setAuditLogs] = useState([]);
  const [systemStatus, setSystemStatus] = useState({});
  const [complianceMetrics, setComplianceMetrics] = useState({});

  useEffect(() => {
    fetchTransparencyData();
    const interval = setInterval(fetchTransparencyData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchTransparencyData = async () => {
    try {
      const [reservesData, securityData, auditData, statusData, complianceData] = await Promise.all([
        fetch('/api/transparency/reserves').then(r => r.json()),
        fetch('/api/transparency/quantum-security').then(r => r.json()),
        fetch('/api/transparency/audit-logs').then(r => r.json()),
        fetch('/api/transparency/system-status').then(r => r.json()),
        fetch('/api/transparency/compliance-metrics').then(r => r.json())
      ]);

      setReserves(reservesData);
      setQuantumSecurity(securityData);
      setAuditLogs(auditData);
      setSystemStatus(statusData);
      setComplianceMetrics(complianceData);
    } catch (error) {
      console.error('Error fetching transparency data:', error);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const getSecurityStatusColor = (status) => {
    switch (status) {
      case 'secure': return 'success';
      case 'warning': return 'warning';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getComplianceScore = (score) => {
    if (score >= 95) return { color: 'success', label: 'Excellent' };
    if (score >= 85) return { color: 'info', label: 'Good' };
    if (score >= 70) return { color: 'warning', label: 'Fair' };
    return { color: 'error', label: 'Poor' };
  };

  return (
    <Box sx={{ p: 3, bgcolor: '#0a0e27', minHeight: '100vh', color: 'white' }}>
      <Typography variant="h3" sx={{ mb: 3, textAlign: 'center', color: '#00d4ff' }}>
        🏛️ DEDAN WORLDMINE TRANSPARENCY PORTAL
      </Typography>

      {/* Quantum Security Heartbeat */}
      <Card sx={{ mb: 3, bgcolor: '#1a237e' }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, color: '#00d4ff' }}>
            🔐 Quantum Security Heartbeat
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Encryption Status
              </Typography>
              <Chip 
                label={quantumSecurity.encryption || 'Unknown'} 
                color={getSecurityStatusColor(quantumSecurity.encryption)}
                sx={{ mb: 1 }}
              />
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                CRYSTALS-Kyber 512-bit
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                ZK-Proof Status
              </Typography>
              <Chip 
                label={quantumSecurity.zkProof || 'Unknown'} 
                color={getSecurityStatusColor(quantumSecurity.zkProof)}
                sx={{ mb: 1 }}
              />
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                Zero-Knowledge Proofs Active
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Lattice Security
              </Typography>
              <Chip 
                label={quantumSecurity.lattice || 'Unknown'} 
                color={getSecurityStatusColor(quantumSecurity.lattice)}
                sx={{ mb: 1 }}
              />
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                Lattice-based Commitments
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Last Verification
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                {quantumSecurity.lastVerification || 'Unknown'}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                {quantumSecurity.verificationTime || 'Unknown'}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Proof of Reserves */}
      <Card sx={{ mb: 3, bgcolor: '#1a237e' }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, color: '#00d4ff' }}>
            💰 Proof of Reserves
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Total Reserves
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#00ff00' }}>
                {formatCurrency(reserves.total || 0)}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Backed Assets
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                {reserves.backedAssets || 0}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Reserve Ratio
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                {reserves.reserveRatio || 0}%
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Last Audit
              </Typography>
              <Typography variant="body2">
                {reserves.lastAudit || 'Unknown'}
              </Typography>
            </Grid>
          </Grid>
          
          {/* Reserve Chart */}
          <Box sx={{ mt: 2, height: 200 }}>
            <ResponsiveContainer width="100%">
              <AreaChart data={reserves.chartData || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="reserves" stroke="#00d4ff" fill="#00d4ff" />
              </AreaChart>
            </ResponsiveContainer>
          </Box>
        </CardContent>
      </Card>

      {/* Audit Log */}
      <Card sx={{ mb: 3, bgcolor: '#1a237e' }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, color: '#00d4ff' }}>
            📋 Immutable Audit Log
          </Typography>
          
          <TableContainer component={Paper} sx={{ bgcolor: '#0a0e27' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: '#00d4ff' }}>Timestamp</TableCell>
                  <TableCell sx={{ color: '#00d4ff' }}>Action</TableCell>
                  <TableCell sx={{ color: '#00d4ff' }}>Entity</TableCell>
                  <TableCell sx={{ color: '#00d4ff' }}>User</TableCell>
                  <TableCell sx={{ color: '#00d4ff' }}>Hash</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {auditLogs.slice(0, 10).map((log, index) => (
                  <TableRow key={index}>
                    <TableCell sx={{ color: 'white' }}>{log.timestamp}</TableCell>
                    <TableCell sx={{ color: 'white' }}>{log.action}</TableCell>
                    <TableCell sx={{ color: 'white' }}>{log.entity}</TableCell>
                    <TableCell sx={{ color: 'white' }}>{log.user}</TableCell>
                    <TableCell sx={{ color: 'white', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {log.hash}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Compliance Metrics */}
      <Card sx={{ mb: 3, bgcolor: '#1a237e' }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, color: '#00d4ff' }}>
            ⚖️ Compliance Metrics
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                AML Compliance Score
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                  {complianceMetrics.amlScore || 0}
                </Typography>
                <Chip 
                  label={getComplianceScore(complianceMetrics.amlScore).label}
                  color={getComplianceScore(complianceMetrics.amlScore).color}
                  size="small"
                />
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={complianceMetrics.amlScore || 0} 
                sx={{ mt: 1, color: '#00d4ff' }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                KYC Verification Rate
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                  {complianceMetrics.kycRate || 0}%
                </Typography>
                <Chip 
                  label={complianceMetrics.kycRate >= 95 ? 'Excellent' : 'Needs Improvement'}
                  color={complianceMetrics.kycRate >= 95 ? 'success' : 'warning'}
                  size="small"
                />
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={complianceMetrics.kycRate || 0} 
                sx={{ mt: 1, color: '#00d4ff' }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Transaction Monitoring
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                  {complianceMetrics.transactionMonitoring || 0}%
                </Typography>
                <Chip 
                  label={complianceMetrics.transactionMonitoring >= 90 ? 'Active' : 'Limited'}
                  color={complianceMetrics.transactionMonitoring >= 90 ? 'success' : 'warning'}
                  size="small"
                />
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={complianceMetrics.transactionMonitoring || 0} 
                sx={{ mt: 1, color: '#00d4ff' }}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* System Status */}
      <Card sx={{ mb: 3, bgcolor: '#1a237e' }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, color: '#00d4ff' }}>
            🚀 System Status
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                API Status
              </Typography>
              <Chip 
                label={systemStatus.apiStatus || 'Unknown'} 
                color={systemStatus.apiStatus === 'healthy' ? 'success' : 'error'}
                sx={{ mb: 1 }}
              />
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                {systemStatus.apiResponseTime || 'Unknown'}ms
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Swarm Status
              </Typography>
              <Chip 
                label={systemStatus.swarmStatus || 'Unknown'} 
                color={systemStatus.swarmStatus === 'healthy' ? 'success' : 'warning'}
                sx={{ mb: 1 }}
              />
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                {systemStatus.activeAgents || 0} agents
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Payment Status
              </Typography>
              <Chip 
                label={systemStatus.paymentStatus || 'Unknown'} 
                color={systemStatus.paymentStatus === 'healthy' ? 'success' : 'error'}
                sx={{ mb: 1 }}
              />
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                {systemStatus.paymentMethods || 0} methods
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                Uptime
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#00ff00' }}>
                {systemStatus.uptime || 99.9}%
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                Last 30 days
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Real-time Alerts */}
      {(systemStatus.alerts || []).length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="h6">
            🚨 System Alerts
          </Typography>
          {systemStatus.alerts.map((alert, index) => (
            <Typography key={index} variant="body2">
              • {alert.message}
            </Typography>
          ))}
        </Alert>
      )}

      {/* Download Reports */}
      <Box sx={{ textAlign: 'center', mt: 3 }}>
        <Button 
          variant="contained" 
          sx={{ 
            bgcolor: '#00d4ff', 
            color: 'black',
            '&:hover': { bgcolor: '#00b8e6' }
          }}
          onClick={() => window.open('/api/transparency/download-report', '_blank')}
        >
          📊 Download Full Report
        </Button>
      </Box>
    </Box>
  );
};

export default TransparencyPortal;
