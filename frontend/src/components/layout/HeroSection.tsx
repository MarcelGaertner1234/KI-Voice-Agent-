import React from 'react'
import { Box, Container, Typography, Grid } from '@mui/material'
import { styled } from '@mui/material/styles'
import { Button } from '../common/Button'

interface HeroSectionProps {
  title: string
  subtitle?: string
  description?: string
  primaryAction?: {
    label: string
    onClick: () => void
  }
  secondaryAction?: {
    label: string
    onClick: () => void
  }
  image?: string
  imageAlt?: string
  variant?: 'default' | 'centered' | 'split'
}

const HeroContainer = styled(Box)(({ theme }) => ({
  background: `linear-gradient(180deg, ${theme.palette.grey[50]} 0%, ${theme.palette.background.default} 100%)`,
  paddingTop: theme.spacing(12),
  paddingBottom: theme.spacing(8),
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'radial-gradient(circle at 20% 50%, rgba(0, 120, 212, 0.05) 0%, transparent 50%)',
    pointerEvents: 'none',
  },
}))

const HeroImage = styled('img')(({ theme }) => ({
  width: '100%',
  height: 'auto',
  maxWidth: 600,
  filter: 'drop-shadow(0px 10px 40px rgba(0, 0, 0, 0.1))',
  [theme.breakpoints.down('md')]: {
    maxWidth: 400,
  },
}))

export const HeroSection: React.FC<HeroSectionProps> = ({
  title,
  subtitle,
  description,
  primaryAction,
  secondaryAction,
  image,
  imageAlt,
  variant = 'default',
}) => {
  const isCentered = variant === 'centered'
  const isSplit = variant === 'split'

  return (
    <HeroContainer>
      <Container maxWidth="xl">
        <Grid 
          container 
          spacing={6} 
          alignItems="center"
          direction={isSplit ? 'row' : 'column'}
        >
          <Grid item xs={12} md={isSplit ? 6 : 12}>
            <Box
              sx={{
                textAlign: isCentered ? 'center' : isSplit ? 'left' : 'left',
                maxWidth: isCentered ? 800 : isSplit ? '100%' : 600,
                mx: isCentered ? 'auto' : 0,
              }}
            >
              {subtitle && (
                <Typography
                  variant="overline"
                  sx={{
                    color: 'primary.main',
                    fontWeight: 600,
                    letterSpacing: 1.5,
                    display: 'block',
                    mb: 2,
                  }}
                >
                  {subtitle}
                </Typography>
              )}
              
              <Typography
                variant="h1"
                sx={{
                  fontWeight: 700,
                  mb: 3,
                  background: 'linear-gradient(180deg, #323130 0%, #605E5C 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                {title}
              </Typography>
              
              {description && (
                <Typography
                  variant="h6"
                  sx={{
                    color: 'text.secondary',
                    fontWeight: 400,
                    mb: 4,
                    lineHeight: 1.7,
                  }}
                >
                  {description}
                </Typography>
              )}
              
              <Box
                sx={{
                  display: 'flex',
                  gap: 2,
                  flexDirection: { xs: 'column', sm: 'row' },
                  justifyContent: isCentered ? 'center' : 'flex-start',
                }}
              >
                {primaryAction && (
                  <Button
                    variant="contained"
                    size="large"
                    gradient
                    onClick={primaryAction.onClick}
                  >
                    {primaryAction.label}
                  </Button>
                )}
                {secondaryAction && (
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={secondaryAction.onClick}
                  >
                    {secondaryAction.label}
                  </Button>
                )}
              </Box>
            </Box>
          </Grid>
          
          {image && isSplit && (
            <Grid item xs={12} md={6}>
              <Box sx={{ textAlign: 'center' }}>
                <HeroImage src={image} alt={imageAlt || title} />
              </Box>
            </Grid>
          )}
        </Grid>
        
        {image && !isSplit && (
          <Box sx={{ textAlign: 'center', mt: 6 }}>
            <HeroImage src={image} alt={imageAlt || title} />
          </Box>
        )}
      </Container>
    </HeroContainer>
  )
}