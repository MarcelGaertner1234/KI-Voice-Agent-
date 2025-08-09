import React from 'react'
import { Box, Typography, CardContent } from '@mui/material'
import { styled } from '@mui/material/styles'
import { TrendingUp, TrendingDown } from '@mui/icons-material'
import { Card } from './Card'

interface StatCardProps {
  title: string
  value: string | number
  change?: number
  changeLabel?: string
  icon?: React.ReactNode
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info'
}

const TrendBox = styled(Box)<{ trend: 'up' | 'down' }>(({ theme, trend }) => ({
  display: 'inline-flex',
  alignItems: 'center',
  gap: theme.spacing(0.5),
  padding: theme.spacing(0.5, 1),
  borderRadius: theme.shape.borderRadius,
  fontSize: '0.875rem',
  fontWeight: 600,
  backgroundColor: trend === 'up' 
    ? theme.palette.success.light + '20'
    : theme.palette.error.light + '20',
  color: trend === 'up' 
    ? theme.palette.success.main
    : theme.palette.error.main,
}))

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  changeLabel,
  icon,
  color = 'primary',
}) => {
  const trend = change && change > 0 ? 'up' : 'down'
  const TrendIcon = trend === 'up' ? TrendingUp : TrendingDown
  
  return (
    <Card variant="surface">
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography
            variant="body2"
            sx={{
              color: 'text.secondary',
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: 0.5,
            }}
          >
            {title}
          </Typography>
          {icon && (
            <Box sx={{ color: `${color}.main`, opacity: 0.8 }}>
              {icon}
            </Box>
          )}
        </Box>
        
        <Typography
          variant="h3"
          sx={{
            fontWeight: 700,
            color: 'text.primary',
            mb: 2,
          }}
        >
          {value}
        </Typography>
        
        {change !== undefined && (
          <TrendBox trend={trend}>
            <TrendIcon fontSize="small" />
            <span>{Math.abs(change)}%</span>
            {changeLabel && (
              <Typography
                variant="caption"
                sx={{ color: 'text.secondary', ml: 0.5 }}
              >
                {changeLabel}
              </Typography>
            )}
          </TrendBox>
        )}
      </CardContent>
    </Card>
  )
}