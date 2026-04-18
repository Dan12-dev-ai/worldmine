import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Box, Grid, Button, Chip, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { useTranslation } from '../locales/translations';

const PlanetaryUI = () => {
  const { t, language, changeLanguage, availableLanguages } = useTranslation();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [globalStats, setGlobalStats] = useState({
    usersActive: '2.5M',
    countriesServed: 156,
    revenue: '$45.2M',
    growth: '+127%'
  });

  const languageOptions = {
    en: { name: 'English', flag: 'en' },
    am: { name: 'Amharic', flag: 'am' },
    es: { name: 'Español', flag: 'es' }
  };

  const tabs = [
    { id: 'dashboard', label: t('header.globalStatus'), icon: 'Global Dashboard' },
    { id: 'payments', label: t('header.sendMoney'), icon: 'Send Money' },
    { id: 'swarm', label: t('header.aiAgents'), icon: 'AI Agents' },
    { id: 'partners', label: t('header.partners'), icon: 'Partners' },
    { id: 'support', label: t('header.help'), icon: 'Help' }
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
        {t('dashboard.title')}
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#1a237e', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {t('dashboard.activeUsers')}
              </Typography>
              <Typography variant="h3" sx={{ fontSize: '2.5rem', fontWeight: 'bold' }}>
                {globalStats.usersActive}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                +127% {t('dashboard.thisMonth')}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#1a237e', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {t('dashboard.countriesServed')}
              </Typography>
              <Typography variant="h3" sx={{ fontSize: '2.5rem', fontWeight: 'bold' }}>
                {globalStats.countriesServed}/256
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                {t('dashboard.globalCoverage')}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#1a237e', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {t('dashboard.totalRevenue')}
              </Typography>
              <Typography variant="h3" sx={{ fontSize: '2.5rem', fontWeight: 'bold' }}>
                {globalStats.revenue}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                +89% {t('dashboard.thisQuarter')}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: '#1a237e', color: 'white' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {t('dashboard.growthRate')}
              </Typography>
              <Typography variant="h3" sx={{ fontSize: '2.5rem', fontWeight: 'bold' }}>
                {globalStats.growth}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                {t('dashboard.globalMining')}
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
        {t('payments.title')}
      </Typography>
      
      <Card sx={{ bgcolor: '#1a237e', color: 'white', mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {t('payments.sendMoneyToAnyCountry')}
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" sx={{ mb: 2 }}>
              {t('payments.from')}
            </Typography>
            <Box
              sx={{
                p: 2,
                border: '1px solid #333',
                borderRadius: 1,
                bgcolor: '#0a0e27'
              }}
            >
              <Typography variant="body2">{t('payments.selectYourCurrency')}</Typography>
            </Box>
          </Box>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" sx={{ mb: 2 }}>
              {t('payments.to')}
            </Typography>
            <Box
              sx={{
                p: 2,
                border: '1px solid #333',
                borderRadius: 1,
                bgcolor: '#0a0e27'
              }}
            >
              <Typography variant="body2">{t('payments.selectRecipientCountry')}</Typography>
            </Box>
          </Box>
          
          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" sx={{ mb: 2 }}>
              {t('payments.amount')}
            </Typography>
            <Box
              sx={{
                p: 2,
                border: '1px solid #333',
                borderRadius: 1,
                bgcolor: '#0a0e27'
              }}
            >
              <Typography variant="body2">{t('payments.enterAmount')}</Typography>
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
            {t('payments.sendMoneyNow')}
          </Button>
        </CardContent>
      </Card>
      
      <Card sx={{ bgcolor: '#1a237e', color: 'white' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {t('payments.supportedCountries')}
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {t('payments.supportedCountriesDesc')}
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {['USA', 'China', 'UAE', 'Ethiopia', 'UK', 
              'Japan', 'Singapore', 'Brazil', 'India', 
              'Russia', 'Nigeria', 'South Africa'].map((country, index) => (
              <Chip key={index} label={country} sx={{ m: 0.5, fontSize: '1.5rem' }} />
            ))}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );

  const renderSwarm = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, textAlign: 'center' }}>
        {t('swarm.title')}
      </Typography>
      
      <Card sx={{ bgcolor: '#1a237e', color: 'white', mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {t('swarm.activeAiAgents')}
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box sx={{ p: 2, border: '1px solid #333', borderRadius: 1 }}>
              <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                {t('swarm.globalVoiceAgent.title')}
              </Typography>
              <Typography variant="body2">
                {t('swarm.globalVoiceAgent.description')}
              </Typography>
              <Chip label={t('swarm.globalVoiceAgent.active')} color="success" size="small" sx={{ mt: 1 }} />
            </Box>
            
            <Box sx={{ p: 2, border: '1px solid #333', borderRadius: 1 }}>
              <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                {t('swarm.growthHackerAgent.title')}
              </Typography>
              <Typography variant="body2">
                {t('swarm.growthHackerAgent.description')}
              </Typography>
              <Chip label={t('swarm.growthHackerAgent.active')} color="success" size="small" sx={{ mt: 1 }} />
            </Box>
            
            <Box sx={{ p: 2, border: '1px solid #333', borderRadius: 1 }}>
              <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                {t('swarm.legalArchitectAgent.title')}
              </Typography>
              <Typography variant="body2">
                {t('swarm.legalArchitectAgent.description')}
              </Typography>
              <Chip label={t('swarm.legalArchitectAgent.active')} color="success" size="small" sx={{ mt: 1 }} />
            </Box>
            
            <Box sx={{ p: 2, border: '1px solid #333', borderRadius: 1 }}>
              <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                {t('swarm.b2bNegotiatorAgent.title')}
              </Typography>
              <Typography variant="body2">
                {t('swarm.b2bNegotiatorAgent.description')}
              </Typography>
              <Chip label={t('swarm.b2bNegotiatorAgent.active')} color="success" size="small" sx={{ mt: 1 }} />
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
        {t('swarm.controlAiAgents')}
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
        textAlign: 'center',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Typography variant="h5" sx={{ color: '#00d4ff', fontWeight: 'bold', flex: 1, textAlign: 'center' }}>
          {t('header.title')}
        </Typography>
        
        {/* Language Selector */}
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <Select
            value={language}
            onChange={(e) => changeLanguage(e.target.value)}
            sx={{
              bgcolor: '#0a0e27',
              color: 'white',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: '#00d4ff',
              },
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: '#00d4ff',
              },
              '& .MuiSvgIcon-root': {
                color: '#00d4ff',
              },
            }}
          >
            {availableLanguages.map((lang) => (
              <MenuItem key={lang} value={lang}>
                {languageOptions[lang].flag === 'en' && 'English'}
                {languageOptions[lang].flag === 'am' && 'Amharic'}
                {languageOptions[lang].flag === 'es' && 'Español'}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
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
          {t('footer.worldwideAccess')} - {t('footer.languages')} - {t('footer.support')}
        </Typography>
      </Box>
    </Box>
  );
};

export default PlanetaryUI;
