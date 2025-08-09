import React from 'react'
import { Box, Container, Grid, Typography } from '@mui/material'
import { 
  Phone as PhoneIcon,
  People as PeopleIcon,
  AccessTime as AccessTimeIcon,
  TrendingUp as TrendingUpIcon,
  SmartToy as SmartToyIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material'
import { StatCard, FeatureCard } from '../components/common'
import { useNavigate } from 'react-router-dom'

export const Dashboard: React.FC = () => {
  const navigate = useNavigate()

  const stats = [
    {
      title: 'Aktive Anrufe',
      value: '3',
      change: 12,
      changeLabel: 'seit gestern',
      icon: <PhoneIcon />,
      color: 'primary' as const,
    },
    {
      title: 'Gesamtanrufe heute',
      value: '147',
      change: 8,
      changeLabel: 'seit gestern',
      icon: <TrendingUpIcon />,
      color: 'success' as const,
    },
    {
      title: 'Durchschn. Anrufdauer',
      value: '4:32',
      change: -5,
      changeLabel: 'seit letzter Woche',
      icon: <AccessTimeIcon />,
      color: 'info' as const,
    },
    {
      title: 'Aktive Kunden',
      value: '1,284',
      change: 15,
      changeLabel: 'seit letztem Monat',
      icon: <PeopleIcon />,
      color: 'secondary' as const,
    },
  ]

  const features = [
    {
      icon: <SmartToyIcon />,
      title: 'Agents verwalten',
      description: 'Erstellen und konfigurieren Sie KI-Agenten für verschiedene Anwendungsfälle.',
      onClick: () => navigate('/agents'),
    },
    {
      icon: <PhoneIcon />,
      title: 'Anrufe überwachen',
      description: 'Verfolgen Sie aktive Anrufe und greifen Sie auf Aufzeichnungen zu.',
      onClick: () => navigate('/calls'),
    },
    {
      icon: <PeopleIcon />,
      title: 'Kundenverwaltung',
      description: 'Verwalten Sie Kundeninformationen und Interaktionshistorie.',
      onClick: () => navigate('/customers'),
    },
    {
      icon: <AnalyticsIcon />,
      title: 'Analysen & Berichte',
      description: 'Detaillierte Einblicke in Leistung und Kundenzufriedenheit.',
      onClick: () => navigate('/analytics'),
    },
  ]

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
            Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Willkommen zurück! Hier ist Ihre Übersicht für heute.
          </Typography>
        </Box>

        <Grid container spacing={3} sx={{ mb: 6 }}>
          {stats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <StatCard {...stat} />
            </Grid>
          ))}
        </Grid>

        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" sx={{ fontWeight: 600, mb: 3 }}>
            Schnellzugriff
          </Typography>
          <Grid container spacing={3}>
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <FeatureCard {...feature} />
              </Grid>
            ))}
          </Grid>
        </Box>
      </Container>
  )
}