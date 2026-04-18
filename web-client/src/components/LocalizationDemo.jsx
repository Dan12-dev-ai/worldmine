import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Box, Button, Chip } from '@mui/material';
import { useTranslation, detectLanguage } from '../locales/translations';

const LocalizationDemo = () => {
  const { t, language, changeLanguage, availableLanguages } = useTranslation();
  const [browserLang, setBrowserLang] = useState('');

  useEffect(() => {
    setBrowserLang(detectLanguage());
  }, []);

  const languageInfo = {
    en: { name: 'English', code: 'en', flag: 'en' },
    am: { name: 'Amharic', code: 'am', flag: 'am' },
    es: { name: 'Español', code: 'es', flag: 'es' }
  };

  const testTranslations = {
    header: t('header.title'),
    dashboard: t('dashboard.title'),
    payments: t('payments.title'),
    swarm: t('swarm.title'),
    partners: t('partners.title'),
    support: t('support.title'),
    activeUsers: t('dashboard.activeUsers'),
    countriesServed: t('dashboard.countriesServed'),
    totalRevenue: t('dashboard.totalRevenue'),
    growthRate: t('dashboard.growthRate'),
    sendMoney: t('payments.sendMoneyNow'),
    controlAgents: t('swarm.controlAiAgents'),
    footer: `${t('footer.worldwideAccess')} - ${t('footer.languages')} - ${t('footer.support')}`
  };

  return (
    <Box sx={{ p: 3, bgcolor: '#0a0e27', minHeight: '100vh', color: 'white' }}>
      <Typography variant="h4" sx={{ mb: 3, textAlign: 'center', color: '#00d4ff' }}>
        Localization Demo - PlanetaryUI
      </Typography>

      {/* Language Detection Info */}
      <Card sx={{ bgcolor: '#1a237e', color: 'white', mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Language Detection
          </Typography>
          <Typography variant="body2">
            Browser Language: {browserLang}
          </Typography>
          <Typography variant="body2">
            Current Language: {language}
          </Typography>
          <Typography variant="body2">
            Available Languages: {availableLanguages.join(', ')}
          </Typography>
        </CardContent>
      </Card>

      {/* Language Selector */}
      <Card sx={{ bgcolor: '#1a237e', color: 'white', mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Language Selector
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {availableLanguages.map((lang) => (
              <Button
                key={lang}
                variant={language === lang ? 'contained' : 'outlined'}
                onClick={() => changeLanguage(lang)}
                sx={{
                  bgcolor: language === lang ? '#00d4ff' : 'transparent',
                  color: language === lang ? 'black' : '#00d4ff',
                  border: language === lang ? 'none' : '1px solid #00d4ff',
                  '&:hover': {
                    bgcolor: language === lang ? '#00b8e6' : 'transparent',
                    color: '#00d4ff'
                  }
                }}
              >
                {languageInfo[lang].flag === 'en' && 'English'}
                {languageInfo[lang].flag === 'am' && 'Amharic'}
                {languageInfo[lang].flag === 'es' && 'Español'}
              </Button>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Translation Examples */}
      <Card sx={{ bgcolor: '#1a237e', color: 'white', mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Translation Examples
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {Object.entries(testTranslations).map(([key, value]) => (
              <Box key={key} sx={{ p: 2, border: '1px solid #333', borderRadius: 1 }}>
                <Typography variant="body2" sx={{ opacity: 0.7, fontSize: '0.8rem' }}>
                  {key}
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                  {value}
                </Typography>
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Current Language Status */}
      <Card sx={{ bgcolor: '#1a237e', color: 'white' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Current Language Status
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip 
              label={`Current: ${languageInfo[language].name}`}
              color="primary"
              sx={{ bgcolor: '#00d4ff', color: 'black' }}
            />
            <Chip 
              label={`Browser: ${languageInfo[browserLang].name}`}
              color="secondary"
              sx={{ bgcolor: '#666', color: 'white' }}
            />
          </Box>
          <Typography variant="body2" sx={{ mt: 2, opacity: 0.7 }}>
            The UI automatically detects your browser language and switches between English, Amharic, and Spanish.
            You can manually change the language using the selector above.
          </Typography>
        </CardContent>
      </Card>

      {/* Test Instructions */}
      <Card sx={{ bgcolor: '#1a237e', color: 'white', mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            How to Test
          </Typography>
          <Typography variant="body2" component="div">
            <ol style={{ paddingLeft: '20px', margin: 0 }}>
              <li>Change your browser language settings to test automatic detection</li>
              <li>Use the language selector to manually switch languages</li>
              <li>Refresh the page to see language persistence</li>
              <li>Navigate to /planetary to see the full localized interface</li>
            </ol>
          </Typography>
          <Button
            variant="contained"
            sx={{
              mt: 2,
              bgcolor: '#00d4ff',
              color: 'black',
              '&:hover': { bgcolor: '#00b8e6' }
            }}
            onClick={() => window.open('/planetary', '_blank')}
          >
            View PlanetaryUI
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default LocalizationDemo;
