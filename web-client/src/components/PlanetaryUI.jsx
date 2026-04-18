import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Box, Grid, Button, Chip } from '@mui/material';

const PlanetaryUI = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [globalStats, setGlobalStats] = useState({
    usersActive: '2.5M',
    countriesServed: 156,
    revenue: '$45.2M',
    growth: '+127%'
  });

  const tabs = [
    { id: 'dashboard', label: '🌍 Global Dashboard', icon: '📊' },
    { id: 'payments', label: '💰 Send Money', icon: '💳' },
    { id: 'swarm', label: '🤖 AI Agents', icon: '🤖' },
    { id: 'partners', label: '🤝 Partners', icon: '🤝' },
    { id: 'support', label: '📞 Help', icon: '📞' }
  ];

  const fetchGlobalStats = async () => {
    try {
      const response = await fetch('/api/global/stats');
      const data = await response.json();
      setGlobalStats(data);
    } catch (error) {
      console.error('Error fetching global stats:', error);
    }
  };

  useEffect(() => {
    fetchGlobalStats();
    const interval = setInterval(fetchGlobalStats, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const renderDashboard = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, textAlign: 'center' }}>
        🌍 DEDAN WORLDMINE - GLOBAL STATUS
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#1a237e', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                👥 Active Users
              </Typography>
              <Typography variant="h3" sx={{ fontSize: '2.5rem', fontWeight: 'bold' }}>
                {globalStats.usersActive}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                +127% this month
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#1a237e', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🌍 Countries Served
              </Typography>
              <Typography variant="h3" sx={{ fontSize: '2.5rem', fontWeight: 'bold' }}>
                {globalStats.countriesServed}/256
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                61% global coverage
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#1a237e', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                💰 Total Revenue
              </Typography>
              <Typography variant="h3" sx={{ fontSize: '2.5rem', fontWeight: 'bold' }}>
                {globalStats.revenue}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                +89% this quarter
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#1a237e', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🚀 Growth Rate
              </Typography>
              <Typography variant="h3" sx={{ fontSize: '2.5rem', fontWeight: 'bold' }}>
                {globalStats.growth}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                #1 in global mining
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderPayments = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, textAlign: 'center' }}>
        💳 GLOBAL PAYMENTS - SEND MONEY WORLDWIDE
      </Typography>
      
      <Card sx={{ bgcolor: '#1a237e', color: 'white', mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🌍 Send Money to Any Country
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" sx={{ mb: 2 }}>
              💵 From:
            </Typography>
            <Box
              sx={{
                p: 2,
                border: '1px solid #333',
                borderRadius: 1,
                bgcolor: '#0a0e27'
              }}
            >
              <Typography variant="body2">Select your currency</Typography>
            </Box>
          </Box>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" sx={{ mb: 2 }}>
              🎯 To:
            </Typography>
            <Box
              sx={{
                p: 2,
                border: '1px solid #333',
                borderRadius: 1,
                bgcolor: '#0a0e27'
              }}
            >
              <Typography variant="body2">Select recipient country & currency</Typography>
            </Box>
          </Box>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" sx={{ mb: 2 }}>
              💰 Amount:
            </Typography>
            <Box
              sx={{
                p: 2,
                border: '1px solid #333',
                borderRadius: 1,
                bgcolor: '#0a0e27'
              }}
            >
              <Typography variant="body2">Enter amount</Typography>
            </Box>
          </Box>
          
          <Button
            variant="contained"
            fullWidth
            sx={{
              mt: 3,
              py: 2,
              fontSize: '1.2rem',
              fontWeight: 'bold',
              bgcolor: '#00d4ff',
              '&:hover': { bgcolor: '#00b8e6' }
            }}
          >
            🚀 SEND MONEY NOW
          </Button>
        </CardContent>
      </Card>
      
      <Card sx={{ bgcolor: '#1a237e', color: 'white' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🌍 Supported Countries
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            We support 256 countries with real-time currency conversion:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {['🇺🇸 USA', '🇨🇳 China', '🇦🇪 UAE', '🇪🇹 Ethiopia', '🇬🇧 UK', 
              '🇯🇵 Japan', '🇸🇬 Singapore', '🇧🇷 Brazil', '🇮🇳 India', 
              '🇷🇺 Russia', '🇳🇬 Nigeria', '🇿🇦 South Africa'].map((flag, index) => (
              <Chip key={index} label={flag} sx={{ m: 0.5, fontSize: '1.5rem' }} />
            ))}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );

  const renderSwarm = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, textAlign: 'center' }}>
        🤖 AI AGENTS - GLOBAL AUTOMATION
      </Typography>
      
      <Card sx={{ bgcolor: '#1a237e', color: 'white', mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🌍 Active AI Agents
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box sx={{ p: 2, border: '1px solid #333', borderRadius: 1 }}>
              <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                🗣️ Global Voice Agent
              </Typography>
              <Typography variant="body2">
                Creating content in 100+ languages
              </Typography>
              <Chip label="✅ ACTIVE" color="success" size="small" sx={{ mt: 1 }} />
            </Box>
            
            <Box sx={{ p: 2, border: '1px solid #333', borderRadius: 1 }}>
              <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                🚀 Growth Hacker Agent
              </Typography>
              <Typography variant="body2">
                Optimizing SEO worldwide
              </Typography>
              <Chip label="✅ ACTIVE" color="success" size="small" sx={{ mt: 1 }} />
            </Box>
            
            <Box sx={{ p: 2, border: '1px solid #333', borderRadius: 1 }}>
              <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                ⚖️ Legal Architect Agent
              </Typography>
              <Typography variant="body2">
                Managing global compliance
              </Typography>
              <Chip label="✅ ACTIVE" color="success" size="small" sx={{ mt: 1 }} />
            </Box>
            
            <Box sx={{ p: 2, border: '1px solid #333', borderRadius: 1 }}>
              <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                🤝 B2B Negotiator Agent
              </Typography>
              <Typography variant="body2">
                Building global partnerships
              </Typography>
              <Chip label="✅ ACTIVE" color="success" size="small" sx={{ mt: 1 }} />
            </Box>
          </Box>
        </CardContent>
      </Card>
      
      <Button
        variant="contained"
        fullWidth
        sx={{
          mt: 3,
          py: 2,
          fontSize: '1.2rem',
          fontWeight: 'bold',
          bgcolor: '#00d4ff',
          '&:hover': { bgcolor: '#00b8e6' }
        }}
        onClick={() => window.open('/swarm', '_blank')}
      >
        🎮 CONTROL AI AGENTS
      </Button>
    </Box>
  );

  const renderPartners = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, textAlign: 'center' }}>
        🤝 GLOBAL PARTNERS
      </Typography>
      
      <Card sx={{ bgcolor: '#1a237e', color: 'white', mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🏢 Fortune 500 Partners
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            WorldMine partners with leading global companies:
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {['BHP Billiton', 'Rio Tinto', 'Glencore', 'Anglo American', 'Coinbase', 'Binance'].map((partner, index) => (
              <Box key={index} sx={{ p: 2, border: '1px solid #333', borderRadius: 1 }}>
                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                  💼 {partner}
                </Typography>
                <Chip label="✅ PARTNER" color="primary" size="small" sx={{ mt: 1 }} />
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>
      
      <Card sx={{ bgcolor: '#1a237e', color: 'white' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🌍 Partnership Benefits
          </Typography>
          <Typography variant="body2">
            • Access to global mining network<br/>
            • Blockchain technology integration<br/>
            • Revenue sharing opportunities<br/>
            • Co-marketing campaigns<br/>
            • Priority support access
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );

  const renderSupport = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, textAlign: 'center' }}>
        📞 GLOBAL SUPPORT
      </Typography>
      
      <Card sx={{ bgcolor: '#1a237e', color: 'white', mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            💬 Get Help in Your Language
          </Typography>
          <Typography variant="body2" sx={{ mb: 3 }}>
            We support 100+ languages worldwide:
          </Typography>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
            {['🇺🇸 English', '🇨🇳 中文', '🇸🇦 العربية', '🇪🇹 አማማ', '🇯🇵 日本語', 
              '🇪🇸 Español', '🇧🇷 Русский', '🇮🇳 हिन्दी'].map((lang, index) => (
              <Chip key={index} label={lang} sx={{ m: 0.5, fontSize: '1rem' }} />
            ))}
          </Box>
          
          <Button
            variant="contained"
            fullWidth
            sx={{
              py: 2,
              fontSize: '1.2rem',
              fontWeight: 'bold',
              bgcolor: '#00d4ff',
              '&:hover': { bgcolor: '#00b8e6' }
            }}
          >
            💬 START LIVE CHAT
          </Button>
        </CardContent>
      </Card>
      
      <Card sx={{ bgcolor: '#1a237e', color: 'white' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            📞 Contact Options
          </Typography>
          <Typography variant="body2">
            • 24/7 Live Chat Support<br/>
            • Email: support@worldmine.com<br/>
            • Phone: +1-800-WORLDMINE<br/>
            • Telegram: @worldmine_support<br/>
            • WhatsApp: +1-555-WORLDMINE
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return renderDashboard();
      case 'payments':
        return renderPayments();
      case 'swarm':
        return renderSwarm();
      case 'partners':
        return renderPartners();
      case 'support':
        return renderSupport();
      default:
        return renderDashboard();
    }
  };

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      bgcolor: '#0a0e27',
      color: 'white',
      fontFamily: 'Arial, sans-serif'
    }}>
      {/* Header */}
      <Box sx={{ 
        p: 2, 
        bgcolor: '#1a237e', 
        borderBottom: '2px solid #00d4ff',
        textAlign: 'center'
      }}>
        <Typography variant="h5" sx={{ color: '#00d4ff', fontWeight: 'bold' }}>
          🌍 DEDAN WORLDMINE - GLOBAL PLATFORM
        </Typography>
      </Box>
      
      {/* Navigation Tabs */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        p: 2, 
        bgcolor: '#1a237e',
        borderBottom: '1px solid #333'
      }}>
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            variant={activeTab === tab.id ? 'contained' : 'outlined'}
            onClick={() => setActiveTab(tab.id)}
            sx={{
              mx: 1,
              px: 3,
              py: 1,
              fontSize: '1rem',
              fontWeight: 'bold',
              bgcolor: activeTab === tab.id ? '#00d4ff' : 'transparent',
              color: activeTab === tab.id ? 'white' : '#00d4ff',
              border: activeTab === tab.id ? 'none' : '1px solid #00d4ff',
              '&:hover': {
                bgcolor: activeTab === tab.id ? '#00b8e6' : 'transparent',
                color: '#00d4ff'
              }
            }}
          >
            {tab.icon} {tab.label}
          </Button>
        ))}
      </Box>
      
      {/* Content */}
      <Box sx={{ p: 2 }}>
        {renderContent()}
      </Box>
      
      {/* Footer */}
      <Box sx={{ 
        p: 2, 
        bgcolor: '#1a237e', 
        borderTop: '1px solid #333',
        textAlign: 'center'
      }}>
        <Typography variant="body2" sx={{ opacity: 0.7 }}>
          🌍 Available in 256 countries • 100+ languages • 24/7 support
        </Typography>
      </Box>
    </Box>
  );
};

export default PlanetaryUI;
