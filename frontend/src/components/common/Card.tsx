import React from 'react'
import { Card as MuiCard, CardProps as MuiCardProps } from '@mui/material'
import { styled } from '@mui/material/styles'

interface CardProps extends MuiCardProps {
  hoverable?: boolean
  variant?: 'default' | 'surface' | 'feature'
}

const StyledCard = styled(MuiCard, {
  shouldForwardProp: (prop) => prop !== 'hoverable' && prop !== 'variant',
})<CardProps>(({ theme, hoverable, variant }) => ({
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  backgroundColor: theme.palette.background.paper,
  borderRadius: variant === 'surface' ? 12 : 8,
  border: `1px solid ${theme.palette.grey[200]}`,
  
  ...(variant === 'surface' && {
    padding: theme.spacing(4),
    background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${theme.palette.grey[50]} 100%)`,
  }),
  
  ...(variant === 'feature' && {
    padding: theme.spacing(3),
    position: 'relative',
    overflow: 'hidden',
    '&::before': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      height: 4,
      background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
    },
  }),
  
  ...(hoverable && {
    cursor: 'pointer',
    '&:hover': {
      transform: 'translateY(-4px)',
      boxShadow: theme.shadows[4],
      borderColor: theme.palette.primary.light,
    },
  }),
}))

export const Card: React.FC<CardProps> = ({ 
  children, 
  hoverable = false,
  variant = 'default',
  ...props 
}) => {
  return (
    <StyledCard hoverable={hoverable} variant={variant} {...props}>
      {children}
    </StyledCard>
  )
}