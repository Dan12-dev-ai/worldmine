import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Box, Grid, Chip, LinearProgress } from '@mui/material';

const GlobalSwarmDashboard = () => {
  const [swarmStatus, setSwarmStatus] = useState({
    agents_active: 0,
    campaigns_running: 0,
    countries_covered: [],
    market_penetration: 0,
    users_active: 0,
    revenue_generated: 0,
    viral_posts: 0,
    partnerships_formed: 0,
    uptime_hours: 0,
    system_health: 'initializing'
  });

  const [agentStatus, setAgentStatus] = useState({
    global_voice: { active: false, last_heartbeat: null },
    growth_hacker: { active: false, last_heartbeat: null },
    legal_architect: { active: false, last_heartbeat: null },
    b2b_negotiator: { active: false, last_heartbeat: null }
  });

  // Fetch swarm status from backend
  const fetchSwarmStatus = async () => {
    try {
      const response = await fetch('/api/swarm/status');
      const data = await response.json();
      setSwarmStatus(data);
      setAgentStatus(data.agent_status);
    } catch (error) {
      console.error('Error fetching swarm status:', error);
    }
  };

  // Start swarm operations
  const startSwarmOperations = async () => {
    try {
      const response = await fetch('/api/swarm/start', { method: 'POST' });
      const data = await response.json();
      console.log('Swarm operations started:', data);
      // Refresh status after starting
      setTimeout(fetchSwarmStatus, 2000);
    } catch (error) {
      console.error('Error starting swarm operations:', error);
    }
  };

  // Emergency restart
  const emergencyRestart = async () => {
    try {
      const response = await fetch('/api/swarm/emergency-restart', { method: 'POST' });
      const data = await response.json();
      console.log('Emergency restart initiated:', data);
      setTimeout(fetchSwarmStatus, 5000);
    } catch (error) {
      console.error('Error restarting swarm:', error);
    }
  };

  useEffect(() => {
    fetchSwarmStatus();
    const interval = setInterval(fetchSwarmStatus, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const getHealthColor = (status) => {
    switch (status) {
      case 'operational': return '#4caf50';
      case 'warning': return '#ff9800';
      case 'error': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  const getAgentStatusColor = (active) => {
    return active ? '#4caf50' : '#9e9e9e';
  };

  return (
    <Box sx={{ p: 3, bgcolor: '#0a0e27', minHeight: '100vh' }}>
      <Typography variant="h4" sx={{ color: '#00d4ff', mb: 3, textAlign: 'center' }}>
        🌍 DEDAN WORLDMINE GLOBAL DOMINATION BACKBONE
      </Typography>
      
      <Grid container spacing={3}>
        {/* System Overview */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🌐 Global Reach Status
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2">
                  Market Penetration: <strong>{swarmStatus.market_penetration.toFixed(1)}%</strong>
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={swarmStatus.market_penetration} 
                  sx={{ mt: 1, height: 8, bgcolor: '#1a237e' }}
                />
              </Box>
              <Typography variant="body2" sx={{ mt: 2 }}>
                Active Users: <strong>{swarmStatus.users_active.toLocaleString()}</strong>
              </Typography>
              <Typography variant="body2">
                Revenue (24h): <strong>${swarmStatus.revenue_generated.toFixed(2)}</strong>
              </Typography>
              <Typography variant="body2">
                Viral Posts: <strong>{swarmStatus.viral_posts}</strong>
              </Typography>
              <Typography variant="body2">
                Partnerships: <strong>{swarmStatus.partnerships_formed}</strong>
              </Typography>
              <Typography variant="body2">
                Countries: <strong>{swarmStatus.countries_covered?.length || 0}</strong>
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Agent Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🤖 Swarm Agents Status
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Global Voice: 
                  <Chip 
                    label={agentStatus.global_voice.active ? 'ACTIVE' : 'INACTIVE'} 
                    color={getAgentStatusColor(agentStatus.global_voice.active)}
                    size="small"
                  />
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Growth Hacker: 
                  <Chip 
                    label={agentStatus.growth_hacker.active ? 'ACTIVE' : 'INACTIVE'} 
                    color={getAgentStatusColor(agentStatus.growth_hacker.active)}
                    size="small"
                  />
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Legal Architect: 
                  <Chip 
                    label={agentStatus.legal_architect.active ? 'ACTIVE' : 'INACTIVE'} 
                    color={getAgentStatusColor(agentStatus.legal_architect.active)}
                    size="small"
                  />
                </Typography>
                <Typography variant="body2">
                  B2B Negotiator: 
                  <Chip 
                    label={agentStatus.b2b_negotiator.active ? 'ACTIVE' : 'INACTIVE'} 
                    color={getAgentStatusColor(agentStatus.b2b_negotiator.active)}
                    size="small"
                  />
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ mt: 2 }}>
                Uptime: <strong>{swarmStatus.uptime_hours?.toFixed(1) || 0} hours</strong>
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Control Panel */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🎮 Swarm Control Panel
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
                <button
                  onClick={startSwarmOperations}
                  disabled={swarmStatus.system_health === 'operational'}
                  style={{
                    padding: '12px 24px',
                    backgroundColor: swarmStatus.system_health === 'operational' ? '#9e9e9e' : '#00d4ff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '16px',
                    fontWeight: 'bold'
                  }}
                >
                  {swarmStatus.system_health === 'operational' ? '⏸️ Stop Swarm' : '🚀 Start Swarm'}
                </button>
                
                <button
                  onClick={emergencyRestart}
                  style={{
                    padding: '12px 24px',
                    backgroundColor: '#f44336',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '16px',
                    fontWeight: 'bold'
                  }}
                >
                  🚨 Emergency Restart
                </button>
              </Box>
              
              <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
                System Health: 
                <Chip 
                  label={swarmStatus.system_health || 'UNKNOWN'} 
                  color={getHealthColor(swarmStatus.system_health)}
                  sx={{ ml: 1 }}
                />
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Real-time Metrics */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Real-time Metrics
              </Typography>
              <Box sx={{ fontFamily: 'monospace', fontSize: '14px', lineHeight: 1.6 }}>
                <Typography variant="body2">
                  Last Update: <strong>{new Date().toLocaleString()}</strong>
                </Typography>
                <Typography variant="body2">
                  Campaigns Running: <strong>{swarmStatus.campaigns_running}</strong>
                </Typography>
                <Typography variant="body2">
                  Agents Active: <strong>{swarmStatus.agents_active}/4</strong>
                </Typography>
                <Typography variant="body2">
                  Global Reach: <strong>{swarmStatus.global_reach?.countries_active || 0} countries</strong>
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default GlobalSwarmDashboard;
