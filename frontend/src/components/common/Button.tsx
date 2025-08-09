import React from 'react'
import { Button as MuiButton, ButtonProps as MuiButtonProps, CircularProgress } from '@mui/material'
import { styled } from '@mui/material/styles'

interface ButtonProps extends MuiButtonProps {
  loading?: boolean
  gradient?: boolean
}

const StyledButton = styled(MuiButton, {
  shouldForwardProp: (prop) => prop !== 'gradient',
})<{ gradient?: boolean }>(({ theme, gradient }) => ({
  position: 'relative',
  overflow: 'hidden',
  transition: 'all 0.2s ease-in-out',
  ...(gradient && {
    background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
    color: theme.palette.primary.contrastText,
    '&:hover': {
      background: `linear-gradient(90deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.main} 100%)`,
      transform: 'translateY(-1px)',
    },
  }),
}))

export const Button: React.FC<ButtonProps> = ({ 
  children, 
  loading, 
  disabled, 
  gradient = false,
  ...props 
}) => {
  return (
    <StyledButton
      disabled={disabled || loading}
      gradient={gradient}
      {...props}
    >
      {loading ? (
        <CircularProgress size={20} color="inherit" />
      ) : (
        children
      )}
    </StyledButton>
  )
}